# Fichier: applications/utilisateurs/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Utilisateur(AbstractUser):
    """Modèle personnalisé d'utilisateur"""
    ROLES = (
        ('admin', 'Administrateur Système'),
        ('directeur', 'Directeur Médicale'),
        ('infirmier_titulaire', 'Infirmier Titulaire'),
        ('medecin', 'Médecin'),
        ('infirmier', 'Infirmier'),
        ('technicien_labo', 'Technicien de Laboratoire'),
        ('sage_femme', 'Sage-Femme'),
        ('receptionniste', 'Réceptionniste'),
        ('caissier', 'Caissier'),
        ('pharmacien', 'Pharmacien'),
    )
    
    telephone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES)
    est_actif = models.BooleanField(default=True)
    date_derniere_connexion = models.DateTimeField(null=True, blank=True)
    photo = models.ImageField(upload_to='photos_utilisateurs/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

class JournalActivite(models.Model):
    """Journal pour suivre les activités des utilisateurs"""
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    nom_utilisateur = models.CharField(max_length=150)  # Au cas où l'utilisateur est supprimé
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    date_heure = models.DateTimeField(auto_now_add=True)
    url_visitee = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-date_heure']
        
    def __str__(self):
        return f"{self.nom_utilisateur} - {self.action} - {self.date_heure}"

# Fichier: applications/utilisateurs/middleware.py
from .models import JournalActivite

class JournalActiviteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Enregistre l'activité uniquement pour les utilisateurs connectés
        if request.user.is_authenticated:
            JournalActivite.objects.create(
                utilisateur=request.user,
                nom_utilisateur=request.user.username,
                action=f"Accès à {request.path}",
                adresse_ip=self.get_client_ip(request),
                url_visitee=request.path
            )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# Fichier: applications/utilisateurs/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utilisateur

class ConnexionForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    username = forms.CharField(label="Nom d'utilisateur", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class CreationUtilisateurForm(UserCreationForm):
    """Formulaire de création d'utilisateur"""
    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'telephone', 'photo', 'password1', 'password2']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

# Fichier: applications/utilisateurs/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .forms import ConnexionForm

urlpatterns = [
    path('', views.tableau_bord, name='tableau_bord'),
    path('login/', LoginView.as_view(
        template_name='utilisateurs/login.html', 
        authentication_form=ConnexionForm
    ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/ajouter/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path('utilisateurs/modifier/<int:pk>/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/desactiver/<int:pk>/', views.desactiver_utilisateur, name='desactiver_utilisateur'),
    path('journal-activite/', views.journal_activite, name='journal_activite'),
    path('mon-profil/', views.mon_profil, name='mon_profil'),
]

# Fichier: applications/utilisateurs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Utilisateur, JournalActivite
from .forms import CreationUtilisateurForm
from django.utils import timezone

def est_admin(user):
    """Vérifie si l'utilisateur est administrateur"""
    return user.role == 'admin'

def est_direction(user):
    """Vérifie si l'utilisateur est directeur ou administrateur"""
    return user.role in ['admin', 'directeur']

@login_required
def tableau_bord(request):
    """Affiche le tableau de bord adapté au rôle de l'utilisateur"""
    # Mise à jour de la date de dernière connexion
    if not request.session.get('connexion_enregistree'):
        request.user.date_derniere_connexion = timezone.now()
        request.user.save()
        request.session['connexion_enregistree'] = True
        
    # Redirection vers le tableau de bord spécifique selon le rôle
    role = request.user.role
    template_name = f'tableaux_bord/{role}_tableau_bord.html'
    
    return render(request, template_name, {
        'utilisateur': request.user
    })

@login_required
@user_passes_test(est_admin)
def liste_utilisateurs(request):
    """Liste tous les utilisateurs du système"""
    utilisateurs = Utilisateur.objects.all().order_by('role', 'last_name')
    return render(request, 'utilisateurs/liste_utilisateurs.html', {
        'utilisateurs': utilisateurs
    })

@login_required
@user_passes_test(est_admin)
def ajouter_utilisateur(request):
    """Ajoute un nouvel utilisateur"""
    if request.method == 'POST':
        form = CreationUtilisateurForm(request.POST, request.FILES)
        if form.is_valid():
            utilisateur = form.save()
            messages.success(request, f"L'utilisateur {utilisateur.username} a été créé avec succès.")
            # Journal d'activité
            JournalActivite.objects.create(
                utilisateur=request.user,
                nom_utilisateur=request.user.username,
                action=f"Création de l'utilisateur {utilisateur.username}",
                details=f"Rôle attribué: {utilisateur.get_role_display()}"
            )
            return redirect('liste_utilisateurs')
    else:
        form = CreationUtilisateurForm()
    
    return render(request, 'utilisateurs/form_utilisateur.html', {
        'form': form,
        'titre': 'Ajouter un utilisateur'
    })

@login_required
@user_passes_test(est_admin)
def modifier_utilisateur(request, pk):
    """Modifie un utilisateur existant"""
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        form = CreationUtilisateurForm(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            utilisateur = form.save()
            messages.success(request, f"L'utilisateur {utilisateur.username} a été modifié avec succès.")
            # Journal d'activité
            JournalActivite.objects.create(
                utilisateur=request.user,
                nom_utilisateur=request.user.username,
                action=f"Modification de l'utilisateur {utilisateur.username}",
                details=f"Rôle actuel: {utilisateur.get_role_display()}"
            )
            return redirect('liste_utilisateurs')
    else:
        form = CreationUtilisateurForm(instance=utilisateur)
    
    return render(request, 'utilisateurs/form_utilisateur.html', {
        'form': form,
        'titre': f'Modifier {utilisateur.username}'
    })

@login_required
@user_passes_test(est_admin)
def desactiver_utilisateur(request, pk):
    """Désactive ou réactive un utilisateur"""
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    
    # Inverse l'état actuel
    utilisateur.est_actif = not utilisateur.est_actif
    utilisateur.is_active = utilisateur.est_actif  # Champ Django pour l'authentification
    utilisateur.save()
    
    etat = "activé" if utilisateur.est_actif else "désactivé"
    messages.success(request, f"L'utilisateur {utilisateur.username} a été {etat} avec succès.")
    
    # Journal d'activité
    JournalActivite.objects.create(
        utilisateur=request.user,
        nom_utilisateur=request.user.username,
        action=f"Changement d'état de l'utilisateur {utilisateur.username}",
        details=f"Nouvel état: {'Actif' if utilisateur.est_actif else 'Inactif'}"
    )
    
    return redirect('liste_utilisateurs')

@login_required
@user_passes_test(est_admin)
def journal_activite(request):
    """Affiche le journal des activités"""
    activites = JournalActivite.objects.all().order_by('-date_heure')
    
    # Filtrage par utilisateur si demandé
    utilisateur_id = request.GET.get('utilisateur')
    if utilisateur_id:
        activites = activites.filter(utilisateur_id=utilisateur_id)
    
    # Filtrage par date si demandé
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if date_debut:
        activites = activites.filter(date_heure__date__gte=date_debut)
    if date_fin:
        activites = activites.filter(date_heure__date__lte=date_fin)
    
    return render(request, 'utilisateurs/journal_activite.html', {
        'activites': activites,
        'utilisateurs': Utilisateur.objects.all()
    })

@login_required
def mon_profil(request):
    """Affiche et permet de modifier son propre profil"""
    utilisateur = request.user
    
    if request.method == 'POST':
        # Formulaire simplifié pour le profil personnel (sans changement de rôle)
        utilisateur.first_name = request.POST.get('first_name')
        utilisateur.last_name = request.POST.get('last_name')
        utilisateur.email = request.POST.get('email')
        utilisateur.telephone = request.POST.get('telephone')
        
        if 'photo' in request.FILES:
            utilisateur.photo = request.FILES['photo']
        
        utilisateur.save()
        messages.success(request, "Votre profil a été mis à jour avec succès.")
        return redirect('mon_profil')
    
    return render(request, 'utilisateurs/mon_profil.html', {
        'utilisateur': utilisateur
    })