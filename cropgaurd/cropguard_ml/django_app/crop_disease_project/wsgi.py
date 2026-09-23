import os  # Access environment variables
from django.core.wsgi import get_wsgi_application  # Factory function to create the WSGI application

# Set the Django settings module for WSGI deployments.
# This tells Django which settings file to use when the app is served
# by a production WSGI server like Gunicorn or uWSGI.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crop_disease_project.settings")

# Create the WSGI application object that production servers will call.
# A WSGI server (e.g., Gunicorn) receives HTTP requests and passes them
# to this application object for processing by Django.
application = get_wsgi_application()
