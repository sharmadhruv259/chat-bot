
"""Django settings for the chat-bot project."""

import os
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the project root (.env).
load_dotenv(BASE_DIR.parent / ".env")


# ---------------------------------------------------------------------
# SECURITY SETTINGS
# ---------------------------------------------------------------------

# Keep the Django secret key in the .env file.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# Enable debug mode only for local development.
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = []


# ---------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local applications
    "chatbot",
]


# ---------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------------------------------------------------
# URL CONFIGURATION
# ---------------------------------------------------------------------

ROOT_URLCONF = "config.urls"


# ---------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ---------------------------------------------------------------------
# WSGI CONFIGURATION
# ---------------------------------------------------------------------

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------

# Default SQLite database.
# Chat history is currently maintained in Streamlit session state.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ---------------------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ---------------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------

STATIC_URL = "static/"


# ---------------------------------------------------------------------
# DEFAULT PRIMARY KEY
# ---------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------
# GROQ API CONFIGURATION
# ---------------------------------------------------------------------

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL = os.environ["GROQ_MODEL"]

# ---------------------------------------------------------------------
# GUARDRAIL & MODERATION CONFIGURATION
# ---------------------------------------------------------------------
GROQ_GUARDRAIL_MODEL = os.environ["GROQ_GUARDRAIL_MODEL"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODERATION_MODEL = os.environ["OPENAI_MODERATION_MODEL"]