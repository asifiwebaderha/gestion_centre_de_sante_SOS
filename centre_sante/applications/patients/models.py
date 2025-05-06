# Fichier: applications/patients/models.py
from django.db import models
from django.utils import timezone
from django.urls import reverse
from applications.utilisateurs.models import Utilisateur

class Patient(models.Model):
    """Modèle représentant un patient du centre de santé"""
    SEXES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('A', 'Autre'),
    )
    
    GROUPES_SANGUINS = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('Inconnu', 'Inconnu')
    )
    
    numero_dossier = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=SEXES)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    groupe_sanguin = models.CharField(max_length=20, choices=GROUPES_SANGUINS, default='Inconnu')
    profession = models.CharField(max_length=100, blank=True, null=True)
    personne_contact = models.CharField(max_length=100, blank=True, null=True)
    telephone_contact = models.CharField(max_length=20, blank=True, null=True)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='photos_patients/', null=True, blank=True)
    est_actif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.numero_dossier})"
    
    def get_age(self):
        """Calcule l'âge du patient"""
        if self.date_naissance:
            today = timezone.now().date()
            return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
        return None
    
    def get_absolute_url(self):
        """Retourne l'URL vers le détail du patient"""
        return reverse('detail_patient', args=[self.pk])
    
    class Meta:
        ordering = ['-date_enregistrement']
        indexes = [
            models.Index(fields=['numero_dossier']),
            models.Index(fields=['nom', 'prenom']),
        ]

class DossierMedical(models.Model):
    """Modèle représentant le dossier médical complet d'un patient"""
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='dossier_medical')
    antecedents_medicaux = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    maladies_chroniques = models.TextField(blank=True, null=True)
    traitements_en_cours = models.TextField(blank=True, null=True)
    notes_importantes = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dossier médical de {self.patient}"

class AntecedentMedical(models.Model):
    """Modèle pour les antécédents médicaux spécifiques"""
    TYPES = (
        ('chirurgical', 'Chirurgical'),
        ('medical', 'Médical'),
        ('familial', 'Familial'),
        ('obstétrique', 'Obstétrique'),
        ('autre', 'Autre'),
    )
    
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE, related_name='antecedents')
    type_antecedent = models.CharField(max_length=20, choices=TYPES)
    description = models.TextField()
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    traitement = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_type_antecedent_display()} - {self.dossier.patient}"

class DocumentMedical(models.Model):
    """Documents médicaux associés au dossier d'un patient"""
    TYPES = (
        ('resultats_labo', 'Résultats de laboratoire'),
        ('imagerie', 'Rapport d\'imagerie'),
        ('certificat', 'Certificat médical'),
        ('ordonnance', 'Ordonnance'),
        ('autre', 'Autre document'),
    )
    
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE, related_name='documents')
    titre = models.CharField(max_length=255)
    type_document = models.CharField(max_length=20, choices=TYPES)
    fichier = models.FileField(upload_to='documents_patients/')
    description = models.TextField(blank=True, null=True) 
    date_ajout = models.DateTimeField(auto_now_add=True)
    auteur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='documents_ajoutes')
    
    def __str__(self):
        return f"{self.titre} - {self.dossier.patient}"

# Fichier: applications/patients/forms.py
from django import forms
from .models import Patient, DossierMedical, AntecedentMedical, DocumentMedical

class PatientForm(forms.ModelForm):
    """Formulaire de création/modification d'un patient"""
    class Meta:
        model = Patient
        fields = ['nom', 'prenom', 'date_naissance', 'sexe', 'adresse', 'telephone', 
                  'email', 'groupe_sanguin', 'profession', 'personne_contact', 
                  'telephone_contact', 'photo']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'groupe_sanguin': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter la classe form-control à tous les champs
        for field_name in self.fields:
            widget = self.fields[field_name].widget
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.Textarea)):
                widget.attrs.update({'class': 'form-control'})

class DossierMedicalForm(forms.ModelForm):
    """Formulaire pour le dossier médical"""
    class Meta:
        model = DossierMedical
        fields = ['antecedents_medicaux', 'allergies', 'maladies_chroniques', 
                  'traitements_en_cours', 'notes_importantes']
        widgets = {
            'antecedents_medicaux': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'maladies_chroniques': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'traitements_en_cours': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes_importantes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class AntecedentMedicalForm(forms.ModelForm):
    """Formulaire pour ajouter un antécédent médical"""
    class Meta:
        model = AntecedentMedical
        fields = ['type_antecedent', 'description', 'date_debut', 'date_fin', 'traitement']
        widgets = {
            'type_antecedent': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'traitement': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class DocumentMedicalForm(forms.ModelForm):
    """Formulaire pour ajouter un document médical"""
    class Meta:
        model = DocumentMedical
        fields = ['titre', 'type_document', 'fichier', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'type_document': forms.Select(attrs={'class': 'form-control'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class RecherchePatientForm(forms.Form):
    """Formulaire de recherche de patients"""
    terme = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, prénom ou numéro de dossier'
        })
    )

# Fichier: applications/patients/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Gestion des patients
    path('', views.liste_patients, name='liste_patients'),
    path('ajouter/', views.ajouter_patient, name='ajouter_patient'),
    path('<int:pk>/', views.detail_patient, name='detail_patient'),
    path('modifier/<int:pk>/', views.modifier_patient, name='modifier_patient'),
    path('desactiver/<int:pk>/', views.desactiver_patient, name='desactiver_patient'),
    
    # Dossier médical
    path('<int:pk>/dossier/', views.dossier_medical, name='dossier_medical'),
    path('<int:pk>/dossier/modifier/', views.modifier_dossier, name='modifier_dossier'),
    
    # Antécédents médicaux
    path('<int:pk>/dossier/antecedent/ajouter/', views.ajouter_antecedent, name='ajouter_antecedent'),
    path('<int:pk>/doss