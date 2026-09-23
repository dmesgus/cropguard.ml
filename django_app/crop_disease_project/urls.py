from django.contrib import admin  # Django's built-in admin interface
from django.urls import path, include  # path() = route definition; include() = delegate to another URL conf

# Root URL configuration for the entire project.
# Each entry maps a URL pattern to a view function or another URL config.
urlpatterns = [
    # /admin/ -> Django's admin panel (manage all models via browser UI)
    path("admin/", admin.site.urls),

    # "" (root) -> Include all URLs from the predictor app's urls.py.
    # This means / goes to the dashboard, /result/ to the result page, etc.
    path("", include("predictor.urls")),

    # /accounts/ -> Django's built-in auth views (login, logout, password reset, etc.)
    # These use Django's default templates at registration/login.html, etc.
    path("accounts/", include("django.contrib.auth.urls")),
]
