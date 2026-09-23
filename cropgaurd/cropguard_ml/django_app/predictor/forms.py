from django import forms  # Django's form framework: provides form fields, validation, widgets

# Choices for the crop selection dropdown in the prediction form.
# First entry ("", "-- Auto-recommend for me --") is the default/empty choice,
# which tells the system to use the ML model to recommend a crop.
# Each tuple is (stored_value, display_label).
CROP_CHOICES = [
    ("", "-- Auto-recommend for me --"),  # No crop selected: let the model decide
    ("rice", "Rice"),       # Oryza sativa — water-intensive cereal
    ("wheat", "Wheat"),     # Triticum aestivum — cool-season cereal
    ("maize", "Maize"),     # Zea mays — warm-season cereal (corn)
    ("cotton", "Cotton"),   # Gossypium — fiber crop, hot/dry tolerant
    ("sugarcane", "Sugarcane"),  # Saccharum — tropical sugar crop
    ("groundnut", "Groundnut"),  # Arachis hypogaea — legume/peanut
    ("millet", "Millet"),        # Pennisetum — drought-tolerant cereal
    ("soybean", "Soybean"),      # Glycine max — legume, protein crop
]


class PredictionForm(forms.Form):
    """Form for submitting soil and climate data for crop/disease prediction.

    Each field corresponds to one of the 7 numeric features the ML models use.
    Fields have min/max validation to prevent unrealistic values,
    and custom CSS classes (form-control) for consistent Bootstrap-like styling.
    The crop selection is optional — if left blank, the model recommends one.
    """

    # --- Soil nutrient fields (kg/ha) ---

    nitrogen = forms.FloatField(
        label="Nitrogen (N) - kg/ha",    # Label shown next to the field in the form
        min_value=0, max_value=150,       # Validation: nitrogen must be 0-150 kg/ha
        widget=forms.NumberInput(attrs={   # Rendered as <input type="number">
            "class": "form-control",       # CSS class for styling
            "placeholder": "e.g. 90",      # Gray hint text inside empty field
            "step": "0.1"                  # Allow decimal inputs (e.g., 90.5)
        }),
    )
    phosphorus = forms.FloatField(
        label="Phosphorus (P) - kg/ha",
        min_value=0, max_value=150,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 45", "step": "0.1"}),
    )
    potassium = forms.FloatField(
        label="Potassium (K) - kg/ha",
        min_value=0, max_value=150,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 45", "step": "0.1"}),
    )

    # --- Environmental condition fields ---

    temperature = forms.FloatField(
        label="Temperature (\u00b0C)",       # \u00b0 = degree symbol (°)
        min_value=-5, max_value=55,          # Range: -5°C to 55°C (covers extreme climates)
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 26", "step": "0.1"}),
    )
    humidity = forms.FloatField(
        label="Humidity (%)",
        min_value=0, max_value=100,          # Percentage: 0-100%
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 80", "step": "0.1"}),
    )
    ph = forms.FloatField(
        label="Soil pH",
        min_value=3.0, max_value=10.0,       # Range: acidic (3.0) to alkaline (10.0)
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 6.5", "step": "0.1"}),
    )
    rainfall = forms.FloatField(
        label="Rainfall (mm)",
        min_value=0, max_value=500,          # Range: 0-500mm per period
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 200", "step": "0.1"}),
    )

    # --- Optional crop selection ---

    selected_crop = forms.ChoiceField(
        label="Crop (optional - leave blank to get a recommendation)",
        choices=CROP_CHOICES,    # Populates the <select> dropdown with our crop list
        required=False,          # User can leave this blank to auto-recommend
        widget=forms.Select(attrs={"class": "form-control"}),
    )
