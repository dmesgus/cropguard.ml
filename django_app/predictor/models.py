from django.db import models  # Provides model field types (FloatField, CharField, etc.)
from django.conf import settings  # Access Django settings, particularly AUTH_USER_MODEL


class PredictionRecord(models.Model):
    """Stores every prediction made through the dashboard, so we can show
    a history/analytics view later without extra work.

    Each record captures:
    - Who made the prediction (user)
    - What inputs they provided (7 soil/climate features + optional crop)
    - What the ML model predicted (recommended crop, disease risk, confidence)
    - When it was created (auto timestamp)
    """

    # Allowed values for the disease_risk field.
    # Each tuple is (stored_value, display_value) — they're identical here.
    RISK_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    # === Owner ===

    # ForeignKey links each prediction to the user who created it.
    # on_delete=models.CASCADE: if a user is deleted, all their predictions are also deleted.
    # related_name="predictions": allows reverse lookup: user.predictions.all()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # Points to Django's user model (auth.User)
        on_delete=models.CASCADE,   # Cascade delete: user deletion removes their predictions
        related_name="predictions", # user.predictions returns all PredictionRecords for that user
    )

    # === Inputs ===

    # The 7 soil/climate features the user entered into the form.
    # FloatField stores decimal numbers (e.g., 90.5, 6.2, 220.0).
    nitrogen = models.FloatField()      # Nitrogen level in kg/ha
    phosphorus = models.FloatField()    # Phosphorus level in kg/ha
    potassium = models.FloatField()     # Potassium level in kg/ha
    temperature = models.FloatField()   # Air temperature in °C
    humidity = models.FloatField()      # Relative humidity in %
    ph = models.FloatField()            # Soil pH level (0-14 scale)
    rainfall = models.FloatField()      # Rainfall in mm

    # The crop the user selected (optional — may be empty if auto-recommended).
    # blank=True: field can be empty in forms; null=True: column can be NULL in database.
    selected_crop = models.CharField(max_length=50, blank=True, null=True)

    # === Outputs ===

    # The crop recommended by the ML model (or the user's choice echoed back).
    recommended_crop = models.CharField(max_length=50, blank=True, null=True)

    # The predicted disease risk level: "Low", "Medium", or "High".
    # choices=RISK_CHOICES limits the field to only these three values.
    disease_risk = models.CharField(max_length=10, choices=RISK_CHOICES)

    # The model's confidence score (0-1) for the predicted risk class.
    # Higher confidence = more certainty in the prediction.
    risk_confidence = models.FloatField(help_text="Model's confidence (0-1) in the predicted risk class")

    # Auto-set timestamp: automatically records the current datetime when the record is created.
    # auto_now_add=True means it's set once on creation and never updated.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Default ordering: most recent records first (descending by creation time)
        ordering = ["-created_at"]

    def __str__(self):
        """Human-readable string representation of the record.
        Used in the Django admin panel and shell to identify records.
        Format: "CropName - RiskLevel risk (YYYY-MM-DD HH:MM)"
        """
        crop = self.selected_crop or self.recommended_crop or "NFA"  # Fallback chain
        return f"{crop} - {self.disease_risk} risk ({self.created_at:%Y-%m-%d %H:%M})"
