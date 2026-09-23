from django.contrib import admin  # Django's admin framework for managing database records
from .models import PredictionRecord  # Import the model we want to manage in the admin


# Register the PredictionRecord model with a custom admin configuration.
# The @admin.register() decorator is a shorthand for admin.site.register(PredictionRecord, PredictionRecordAdmin).
@admin.register(PredictionRecord)
class PredictionRecordAdmin(admin.ModelAdmin):
    """Customizes how PredictionRecord appears in the Django admin panel.

    Controls which columns are shown in the list view, how rows can be
    filtered, and the default sort order.
    """
    # Columns displayed in the admin list view (the table of all records):
    list_display = (
        "id",                # Database primary key
        "user",              # Which user made this prediction
        "selected_crop",     # The crop the user chose (if any)
        "recommended_crop",  # The crop recommended by the ML model
        "disease_risk",      # Predicted risk level (Low/Medium/High)
        "risk_confidence",   # Model confidence percentage
        "created_at",        # Timestamp of when the prediction was made
    )

    # Add filter sidebar on the right of the list view:
    # Users can quickly filter records by risk level, crop, or user.
    list_filter = ("disease_risk", "selected_crop", "user")

    # Default sort order: most recent predictions first (- prefix = descending).
    ordering = ("-created_at",)
