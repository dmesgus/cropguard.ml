from django.shortcuts import render, redirect  # render() = render a template; redirect() = send user to another URL
from django.contrib import messages  # Flash messages framework for showing success/error notifications
from django.contrib.auth import login  # Log in a user programmatically (create session)
from django.contrib.auth.forms import UserCreationForm  # Built-in form for creating new user accounts
from django.contrib.auth.decorators import login_required  # Decorator: requires user to be logged in

from .forms import PredictionForm  # Our custom form for entering soil/climate data
from .models import PredictionRecord  # Our database model for storing prediction history
from .ml.predict import run_prediction, NUMERIC_FEATURES  # ML prediction function and feature name list


def register(request):
    """New user registration using Django's built-in UserCreationForm.

    Handles both GET (show empty form) and POST (process submitted form).
    If user is already logged in, redirects to dashboard instead.
    """
    # If the user is already authenticated, no need for registration — go to dashboard
    if request.user.is_authenticated:
        return redirect("dashboard")
    # Handle form submission (POST request)
    if request.method == "POST":
        # Bind the submitted POST data to the UserCreationForm
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user to the database (username + hashed password)
            user = form.save()
            # Automatically log in the newly registered user
            login(request, user)
            # Show a success flash message that will display on the next page
            messages.success(request, "Account created. Welcome to CropGuard!")
            # Redirect to the dashboard after successful registration
            return redirect("dashboard")
    else:
        # GET request: create a blank form to display
        form = UserCreationForm()
    # Render the registration template with the (empty or invalid) form
    return render(request, "registration/register.html", {"form": form})


@login_required  # This decorator redirects unauthenticated users to LOGIN_URL ("login")
def dashboard(request):
    """Main page: shows the input form for soil/climate data.

    On GET: displays the empty prediction form + last 5 predictions.
    On POST: validates the form, runs ML prediction, saves to DB, redirects to result page.
    """
    if request.method == "POST":
        # Bind the submitted form data to our PredictionForm
        form = PredictionForm(request.POST)
        if form.is_valid():
            # Extract the 7 numeric feature values from the cleaned form data
            features = {f: form.cleaned_data[f] for f in NUMERIC_FEATURES}
            # Get the user's crop selection (optional — may be empty string)
            selected_crop = form.cleaned_data.get("selected_crop") or ""

            # Call the ML prediction function with the features and optional crop
            # Returns a dict with recommended_crop, disease_risk, confidence, advice, etc.
            result = run_prediction(features, selected_crop)

            # Save the prediction as a record in the database for history tracking
            record = PredictionRecord.objects.create(
                user=request.user,                              # Link to the logged-in user
                nitrogen=features["nitrogen"],                 # Store input: nitrogen level
                phosphorus=features["phosphorus"],             # Store input: phosphorus level
                potassium=features["potassium"],               # Store input: potassium level
                temperature=features["temperature"],           # Store input: temperature
                humidity=features["humidity"],                 # Store input: humidity
                ph=features["ph"],                             # Store input: soil pH
                rainfall=features["rainfall"],                 # Store input: rainfall
                selected_crop=selected_crop or None,           # Store the crop the user chose (if any)
                recommended_crop=result["recommended_crop"],   # Store the ML-recommended crop
                disease_risk=result["disease_risk"],           # Store the predicted risk level
                risk_confidence=result["confidence"],          # Store the model's confidence percentage
            )

            # Save the record ID in the session so the result page can retrieve it
            request.session["last_result_id"] = record.id
            # Redirect to the result page (POST-redirect-GET pattern prevents form re-submission)
            return redirect("result")
        else:
            # Form had validation errors — show error message to user
            messages.error(request, "Please correct the errors below.")
    else:
        # GET request: create a blank PredictionForm
        form = PredictionForm()

    # Fetch the 5 most recent predictions for this user (for the sidebar display)
    recent = PredictionRecord.objects.filter(user=request.user)[:5]
    # Render the dashboard template with the form and recent predictions
    return render(request, "predictor/dashboard.html", {"form": form, "recent": recent})


@login_required
def result(request):
    """Shows the result of the most recent prediction (retrieved from session).

    The record ID is stored in the user's session by the dashboard view.
    This view loads that record and displays it with advisory text.
    """
    # Get the ID of the most recent prediction from the user's session
    record_id = request.session.get("last_result_id")
    # If no prediction ID in session (e.g., first visit), redirect to dashboard
    if not record_id:
        return redirect("dashboard")

    try:
        # Fetch the prediction record from the database.
        # Also filter by user=request.user to ensure users can only see their own results.
        record = PredictionRecord.objects.get(id=record_id, user=request.user)
    except PredictionRecord.DoesNotExist:
        # Record doesn't exist or doesn't belong to this user — redirect to dashboard
        return redirect("dashboard")

    # Import the RISK_ADVICE dictionary from our ML module.
    # This maps risk levels (Low/Medium/High) to actionable advisory text.
    from .ml.predict import RISK_ADVICE
    advice = RISK_ADVICE.get(record.disease_risk, "")

    # Render the result template with the prediction record and advisory text
    return render(request, "predictor/result.html", {"record": record, "advice": advice})


@login_required
def history(request):
    """Shows all past predictions as a table — simple analytics/history view.

    Displays total prediction count and high-risk count as summary stats,
    plus a full table of all predictions ordered by date (newest first).
    """
    # Get all prediction records for the current user
    records = PredictionRecord.objects.filter(user=request.user)
    # Count total predictions
    total = records.count()
    # Count how many predictions were flagged as "High" risk
    high_risk_count = records.filter(disease_risk="High").count()
    # Render the history template with all data
    return render(
        request,
        "predictor/history.html",
        {"records": records, "total": total, "high_risk_count": high_risk_count},
    )
