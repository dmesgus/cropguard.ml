from pathlib import Path  # Object-oriented filesystem path handling (cross-platform)

# BASE_DIR points to the project root directory (cropguard_ml/django_app/).
# Path(__file__) = settings.py's path; .resolve().parent.parent = two levels up.
# Used throughout settings to build absolute file paths (e.g., for DB, static files).
BASE_DIR = Path(__file__).resolve().parent.parent

# Django's cryptographic signing key. Used for sessions, CSRF tokens, password reset links, etc.
# WARNING: This is an insecure default key. Must be changed to a random value in production.
SECRET_KEY = "django-insecure-change-this-in-production-xyz123"

# DEBUG mode: when True, Django shows detailed error pages with stack traces.
# Should be False in production for security (hides sensitive info from users).
DEBUG = True

# List of hostnames/IPs allowed to serve this application.
# "*" means all hosts are accepted — fine for development, but should be
# restricted to specific domains in production (e.g., ["cropguard.example.com"]).
ALLOWED_HOSTS = ["*"]

# List of Django applications that are active in this project.
# Each app provides specific functionality:
INSTALLED_APPS = [
    "django.contrib.admin",       # Built-in admin panel for managing data via browser
    "django.contrib.auth",        # User authentication system (login, logout, passwords)
    "django.contrib.contenttypes", # Content type framework (used internally by Django)
    "django.contrib.sessions",    # Session framework (stores user data between requests)
    "django.contrib.messages",    # Messaging framework (flash messages shown to users)
    "django.contrib.staticfiles", # Serves static files (CSS, JS, images) during development
    "predictor",                  # Our custom app: handles crop/disease predictions
]

# Middleware = a series of hooks that process every request/response.
# Each middleware adds functionality (security headers, session handling, CSRF protection, etc.)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",          # Adds security headers (HTTPS, HSTS, etc.)
    "django.contrib.sessions.middleware.SessionMiddleware",   # Enables session support (ties requests to users)
    "django.middleware.common.CommonMiddleware",              # URL normalization, content-length header
    "django.middleware.csrf.CsrfViewMiddleware",             # Protects POST forms from cross-site request forgery
    "django.contrib.auth.middleware.AuthenticationMiddleware", # Associates users with requests via sessions
    "django.contrib.messages.middleware.MessageMiddleware",   # Enables the messages framework (flash messages)
    "django.middleware.clickjacking.XFrameOptionsMiddleware", # Prevents clickjacking (iframe embedding attacks)
]

# Points to the root URL configuration module where all URL routes are defined.
ROOT_URLCONF = "crop_disease_project.urls"

# Template engine configuration: tells Django where to find HTML templates.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",  # Use Django's built-in template engine
        "DIRS": [],                  # Additional template directories (none; we use app-level templates)
        "APP_DIRS": True,            # Look for templates in each app's templates/ subdirectory
        "OPTIONS": {
            "context_processors": [
                # These functions run on every template render and inject common variables:
                "django.template.context_processors.debug",      # Adds debug info (SQL queries, etc.)
                "django.template.context_processors.request",    # Adds the current HttpRequest object
                "django.contrib.auth.context_processors.auth",   # Adds user, messages, perms to all templates
                "django.contrib.messages.context_processors.messages", # Adds the messages framework to templates
            ],
        },
    },
]

# Points to the WSGI application entry point for deployment servers
# (e.g., Gunicorn, uWSGI). Development server uses manage.py instead.
WSGI_APPLICATION = "crop_disease_project.wsgi.application"

# =====================================================================
# DATABASE
# =====================================================================
# Default: SQLite (zero setup, good for development/demo).
# SQLite stores the entire database in a single file (db.sqlite3).
# To switch to PostgreSQL later, replace this block with:
#
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "crop_disease_db",
#         "USER": "postgres",
#         "PASSWORD": "yourpassword",
#         "HOST": "localhost",
#         "PORT": "5432",
#     }
# }
# and run: pip install psycopg2-binary

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",     # Use SQLite database engine
        "NAME": BASE_DIR / "db.sqlite3",            # Database file path: django_app/db.sqlite3
    }
}

# List of password validators that run when users create/change passwords.
# Each validator enforces a specific security rule:
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},  # Password can't be too similar to username/email
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},              # Password must be at least 8 characters
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},            # Password can't be a commonly-used password
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},           # Password can't be entirely numeric
]

# Language and timezone settings
LANGUAGE_CODE = "en-us"    # English (US) for admin and messages
TIME_ZONE = "Asia/Kolkata" # Indian Standard Time (IST, UTC+5:30)
USE_I18N = True            # Enable Django's internationalization system
USE_TZ = True              # Enable timezone-aware datetimes (stores UTC, displays local)

# Static files (CSS, JavaScript, images) URL prefix and filesystem locations
STATIC_URL = "static/"     # URL prefix: /static/css/style.css, etc.
# Where Django looks for additional static files to collect during `collectstatic`:
STATICFILES_DIRS = [BASE_DIR / "static"]  # Points to django_app/static/

# Default primary key field type for models that don't specify one.
# BigAutoField = 64-bit integer (supports 2^63 records — more than enough).
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication URL redirects:
LOGIN_URL = "login"              # Where to redirect unauthenticated users trying to access @login_required views
LOGIN_REDIRECT_URL = "dashboard" # Where to redirect users after successful login
LOGOUT_REDIRECT_URL = "login"    # Where to redirect users after logout
