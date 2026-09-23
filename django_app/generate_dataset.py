"""
Generates a synthetic but realistic dataset for:
1. Crop recommendation (based on N, P, K, temperature, humidity, ph, rainfall)
2. Disease risk level (Low/Medium/High) based on conditions being
   favorable for common fungal/bacterial disease outbreaks.

Real-world reference ranges used (approximate, from agronomy literature):
- Rice: high humidity + high rainfall + warm temp -> blast/blight risk
- Wheat: cool + humid -> rust risk
- Cotton: hot + moderate humidity -> bacterial blight risk
- Maize: warm + humid -> leaf blight risk
- etc.

We simulate ~2500 rows across 8 crops with noise, so the model has to
genuinely learn patterns rather than memorize a lookup table.
"""

import numpy as np  # Numerical operations: random number generation, clipping
import pandas as pd  # DataFrame construction and CSV export

# Set the random seed so the generated dataset is the same every time.
# This ensures reproducibility — running this script multiple times
# produces identical output.
np.random.seed(42)

# The 8 crops this application supports.
# Each crop has specific growing conditions and disease susceptibility patterns.
CROPS = ["rice", "wheat", "maize", "cotton", "sugarcane", "groundnut", "millet", "soybean"]

# Typical favorable growing ranges for each crop, stored as tuples of:
# (temp_mean, temp_sd, humidity_mean, humidity_sd,
#  rainfall_mean, rainfall_sd, ph_mean, ph_sd,
#  N_mean, P_mean, K_mean)
#
# "sd" = standard deviation — controls how much random variation/noise
# is added around the mean for each feature. Higher sd = more spread.
# These values are loosely based on agronomy literature and real datasets.
CROP_PROFILES = {
    "rice":      (26, 3, 82, 6, 220, 40, 6.2, 0.4, 90, 45, 45),   # Warm, very humid, high rainfall
    "wheat":     (18, 3, 65, 8, 90,  25, 6.8, 0.4, 100, 50, 40),  # Cool, moderate humidity
    "maize":     (24, 3, 68, 8, 100, 30, 6.3, 0.4, 95, 50, 45),   # Warm, moderate humidity
    "cotton":    (28, 3, 55, 8, 80,  25, 6.9, 0.4, 110, 40, 50),  # Hot, lower humidity
    "sugarcane": (27, 2, 78, 6, 180, 35, 6.5, 0.3, 130, 55, 60),  # Warm, high humidity, high K/N
    "groundnut": (26, 3, 60, 8, 90,  25, 6.4, 0.4, 40,  60, 55),  # Warm, high phosphorus needs
    "millet":    (29, 3, 45, 8, 60,  20, 6.7, 0.5, 45,  30, 30),  # Hot, dry-tolerant
    "soybean":   (25, 3, 65, 8, 110, 30, 6.5, 0.4, 60,  55, 50),  # Warm, moderate rainfall
}

# List to accumulate all generated rows before creating the DataFrame
rows = []

# Number of synthetic samples to generate per crop (320 * 8 crops = 2560 total rows)
N_PER_CROP = 320

# Iterate over each crop and its growing-condition profile
for crop, (tmean, tsd, hmean, hsd, rmean, rsd, phmean, phsd, Nm, Pm, Km) in CROP_PROFILES.items():
    # Generate N_PER_CROP samples for this crop
    for _ in range(N_PER_CROP):
        # Generate each feature from a normal distribution centered on the crop's
        # typical values, then clip to physically plausible ranges.
        # np.random.normal(mean, sd) draws a random value from a bell curve.
        # np.random.clip(value, min, max) ensures no unrealistic outliers.

        temperature = np.clip(np.random.normal(tmean, tsd), 5, 45)    # Temp: 5-45°C
        humidity = np.clip(np.random.normal(hmean, hsd), 10, 100)     # Humidity: 10-100%
        rainfall = np.clip(np.random.normal(rmean, rsd), 0, 400)      # Rainfall: 0-400mm
        ph = np.clip(np.random.normal(phmean, phsd), 3.5, 9.5)        # Soil pH: 3.5-9.5
        N = np.clip(np.random.normal(Nm, 15), 0, 150)                 # Nitrogen: 0-150 kg/ha
        P = np.clip(np.random.normal(Pm, 12), 0, 100)                 # Phosphorus: 0-100 kg/ha
        K = np.clip(np.random.normal(Km, 12), 0, 100)                 # Potassium: 0-100 kg/ha

        # --- Disease risk logic (rule + noise based, mimics agronomy heuristics) ---
        # High humidity + high rainfall + moderate-warm temp => favorable for fungal disease.
        # We build up a "fungal_score" from multiple contributing factors,
        # then add noise so the rules aren't perfectly deterministic.
        # This forces the ML model to genuinely learn patterns.

        fungal_score = 0  # Accumulator for disease risk factors

        # Factor 1: Humidity — high humidity promotes fungal growth on leaves
        if humidity > 75:
            fungal_score += 2     # Very high humidity = strong risk factor
        elif humidity > 60:
            fungal_score += 1     # Moderate humidity = mild risk factor

        # Factor 2: Rainfall — heavy rain creates standing water and splash-dispersed spores
        if rainfall > 150:
            fungal_score += 2     # Heavy rainfall = strong risk factor
        elif rainfall > 80:
            fungal_score += 1     # Moderate rainfall = mild risk factor

        # Factor 3: Temperature — moderate-warm temps (20-30°C) are ideal for fungal growth
        if 20 <= temperature <= 30:
            fungal_score += 1     # Ideal fungal temperature range

        # Factor 4: Extreme pH — plants stressed by very acidic or alkaline soil
        # are more susceptible to disease
        if ph < 5.5 or ph > 7.8:
            fungal_score += 1     # Stress from extreme soil pH

        # Factor 5: Nutrient deficiency — very low Nitrogen or Potassium
        # weakens plant immune response
        if N < 30 or K < 25:
            fungal_score += 1     # Weakened plant immunity

        # Add Gaussian noise to the score so the risk boundaries aren't
        # perfectly deterministic. This prevents the ML model from simply
        # memorizing exact thresholds and forces it to learn approximate patterns.
        fungal_score += np.random.normal(0, 0.8)

        # Convert the continuous fungal_score into a discrete risk category
        if fungal_score >= 4.5:
            risk = "High"      # High risk: conditions strongly favor disease
        elif fungal_score >= 2.5:
            risk = "Medium"    # Medium risk: some concerning conditions
        else:
            risk = "Low"       # Low risk: conditions are unfavorable for disease

        # Append this sample as a row: [N, P, K, temp, humidity, pH, rain, crop, risk]
        rows.append([N, P, K, temperature, humidity, ph, rainfall, crop, risk])

# Convert the list of rows into a pandas DataFrame with proper column names
df = pd.DataFrame(rows, columns=[
    "nitrogen", "phosphorus", "potassium", "temperature",
    "humidity", "ph", "rainfall", "crop", "disease_risk"
])

# Shuffle (randomize) the rows so the order isn't grouped by crop.
# frac=1 means shuffle 100% of rows; reset_index() renumbers 0..N
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save the dataset to CSV (without the DataFrame index column)
df.to_csv("dataset.csv", index=False)

# Print summary statistics to verify the dataset was generated correctly
print("Dataset generated:", df.shape)                  # (2560, 9) = 2560 rows, 9 columns
print(df["crop"].value_counts())                        # Count of samples per crop (should be ~320 each)
print(df["disease_risk"].value_counts())                # Count of samples per risk level (Low/Medium/High)
