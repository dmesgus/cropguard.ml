# CropGuard AI — Crop Disease Risk Prediction

A Django web app where users enter soil/climate readings (N, P, K, temperature,
humidity, pH, rainfall) and optionally a crop, and get back:
1. A recommended crop (if none selected) — from a Random Forest classifier
2. A disease risk level (Low / Medium / High) for that crop — from a second
   Random Forest classifier
3. A short advisory message and the top contributing factors

Every prediction is saved to the database and viewable in the History page.

## Project structure

```
django_app/
├── manage.py
├── requirements.txt
├── dataset.csv                  # training data (already generated)
├── generate_dataset.py          # regenerate dataset.csv if needed
├── train_model.py               # retrain both ML models
├── crop_disease_project/        # Django project settings
├── predictor/                   # main app
│   ├── models.py                # PredictionRecord (DB table)
│   ├── forms.py                 # input form
│   ├── views.py                 # dashboard / result / history views
│   ├── ml/
│   │   ├── predict.py           # loads models, runs inference
│   │   ├── crop_model.pkl
│   │   ├── disease_risk_model.pkl
│   │   ├── scaler_crop.pkl, scaler_risk.pkl
│   │   ├── crop_encoder.pkl, risk_encoder.pkl
│   │   └── feature_importance.json
│   └── templates/predictor/
└── static/css/style.css
```

## Setup (run these on your own machine)

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      (Windows)
   source venv/bin/activate   (Mac/Linux)
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. The ML models are already trained and included (`predictor/ml/*.pkl`).
   If you want to regenerate them (e.g. after changing the dataset logic):
   ```
   python generate_dataset.py
   python train_model.py
   copy the resulting .pkl and .json files into predictor/ml/
   ```

4. Run Django migrations to create the database tables:
   ```
   python manage.py makemigrations predictor
   python manage.py migrate
   ```

5. (Optional) create an admin user to view the DB via Django admin:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Open http://127.0.0.1:8000/ in your browser.
   Admin panel: http://127.0.0.1:8000/admin/

## Switching from SQLite to PostgreSQL (optional)

In `crop_disease_project/settings.py`, replace the `DATABASES` block with the
PostgreSQL config shown in the comment there, then:
```
pip install psycopg2-binary
python manage.py migrate
```

## Notes on the ML models

- **Dataset**: synthetic but agronomically realistic — generated from typical
  N-P-K / temperature / humidity / rainfall / pH ranges for 8 crops, with a
  rule + noise based disease-risk label (favorable fungal/bacterial
  conditions raise risk). See `generate_dataset.py` for exact logic — this
  is worth including in your project report as "how the dataset was
  constructed" since real labeled soil→disease datasets are hard to find
  publicly.
- **Model 1 (crop recommendation)**: RandomForestClassifier, ~82% accuracy
- **Model 2 (disease risk)**: RandomForestClassifier, ~76% accuracy
- Metrics are saved in `predictor/ml/model_metrics.json` if produced by
  `train_model.py` — good to quote directly in your report.
- Explainability: the result page shows the top 3 features (from
  `feature_importances_`) that most influence the risk model overall. This
  is a simplified, defensible substitute for full SHAP analysis, easy to
  explain in a viva.

## Ideas for extension (optional, once the core works)

- Add user login (`django.contrib.auth`) so each user sees only their own history
- Add a chart (Chart.js) on the History page showing risk distribution over time
- Add a region dropdown that auto-fills typical rainfall/temperature values
- Swap SQLite → PostgreSQL for the "production-ready" story in your report
