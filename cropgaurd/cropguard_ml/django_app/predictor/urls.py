from django.urls import path  # Import path() for defining URL routes
from . import views  # Import the views module from this app

# URL patterns for the predictor app.
# These are included in the project's root urls.py at the "" prefix,
# so all these paths are relative to the site root (e.g., /result/).
urlpatterns = [
    # "" (root) -> dashboard view: the main page with the prediction form
    # name="dashboard" allows us to reverse-resolve this URL in templates:
    # {% url 'dashboard' %} -> "/"
    path("", views.dashboard, name="dashboard"),

    # /result/ -> result view: shows the outcome of the most recent prediction
    path("result/", views.result, name="result"),

    # /history/ -> history view: shows all past predictions in a table
    path("history/", views.history, name="history"),

    # /register/ -> register view: new user account creation form
    path("register/", views.register, name="register"),
]
