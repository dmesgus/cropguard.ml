from django.apps import AppConfig  # Base class for app configuration in Django


class PredictorConfig(AppConfig):
    """Django application configuration for the 'predictor' app.

    This class tells Django how to configure this app. It's referenced
    in settings.py INSTALLED_APPS as "predictor".
    """
    # Specify the type of auto-generated primary key for models in this app.
    # BigAutoField uses 64-bit integers (more than enough capacity).
    default_auto_field = "django.db.models.BigAutoField"

    # The app's name, used for identification throughout Django's internals.
    name = "predictor"
