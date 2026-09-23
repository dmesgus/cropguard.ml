#!/usr/bin/env python
# ^^^ Shebang line: tells Unix-like systems to use the Python interpreter
# found in the user's PATH when this file is executed directly (e.g., ./manage.py).

import os  # Provides functions for interacting with the operating system (env vars, paths, etc.)
import sys  # Provides access to Python runtime variables like sys.argv (command-line args)


def main():
    """Entry point for Django's command-line utility.

    This function sets the default Django settings module so that Django
    knows which settings.py file to load for this project, then hands
    control over to Django's built-in management command system.
    """
    # Set the DJANGO_SETTINGS_MODULE environment variable to point to our
    # project's settings file. This tells Django where to find configuration
    # like INSTALLED_APPS, DATABASES, MIDDLEWARE, etc.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crop_disease_project.settings")
    try:
        # Attempt to import Django's execute_from_command_line function.
        # This function parses sys.argv (e.g., "runserver", "migrate", "createsuperuser")
        # and dispatches to the appropriate management command.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # If Django is not installed or not reachable on PYTHONPATH, raise a
        # helpful error message guiding the developer to check their setup.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc  # Chains the original ImportError for better debugging context
    # Pass the command-line arguments to Django's management system.
    # sys.argv example: ['manage.py', 'runserver'] or ['manage.py', 'migrate']
    execute_from_command_line(sys.argv)


# This guard ensures that main() is only called when the script is run directly,
# not when it is imported as a module by another script.
# __name__ == "__main__" is True only at the top-level script entry point.
if __name__ == "__main__":
    main()
