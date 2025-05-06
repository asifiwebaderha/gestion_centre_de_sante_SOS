# Fichier: centre_sante/settings.py
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-votre-cle-secrete-ici'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Applications tierces
    'crispy_forms',
    'widget_tweaks',
    
    # Nos applications
    'applications.utilisateurs',
    'applications.patients',
    'applications.chambres',
    'applications.soins',
    'applications.caisse',
    'applications.pharmacie',
    'applications.laboratoire',
    'applications.rapports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'applications.utilisateurs.middleware.JournalActiviteMiddleware',  # Journal d'activité
]

ROOT_URLCONF = 'centre_sante.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'centre_sante.wsgi.application'

# Configuration de la base de données MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'centre_sante_sos',
        'USER': 'utilisateur_bd',
        'PASSWORD': 'mot_de_passe_bd',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Utiliser notre modèle Utilisateur personnalisé
AUTH_USER_MODEL = 'utilisateurs.Utilisateur'

# URLs de redirection après connexion/déconnexion
LOGIN_REDIRECT_URL = 'tableau_bord'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Configuration des fichiers statiques
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuration des fichiers média
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuration par défaut pour les champs de PRIMARY KEY
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration pour crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Fichier: centre_sante/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('utilisateurs/', include('applications.utilisateurs.urls')),
    path('patients/', include('applications.patients.urls')),
    path('chambres/', include('applications.chambres.urls')),
    path('soins/', include('applications.soins.urls')),
    path('caisse/', include('applications.caisse.urls')),
    path('pharmacie/', include('applications.pharmacie.urls')),
    path('laboratoire/', include('applications.laboratoire.urls')),
    path('rapports/', include('applications.rapports.urls')),
    path('', include('applications.utilisateurs.urls')),  # URL racine
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)