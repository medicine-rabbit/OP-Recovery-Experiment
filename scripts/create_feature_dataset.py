# create_feature_dataset.py

import pandas as pd
import numpy as np
import os
from datetime import datetime

# === CONFIGURATION ===
UNIFIED_RUN_PATH = "/home/daniel/OP_Recovery_Experiment/data/processed/unified_runs/2025-04-25_run_unified.csv"
OUTPUT_FEATURES_PATH = "/home/daniel/OP_Recovery_Experiment/data/processed/feature_datasets/2025-04-25_features.csv"

# === LOAD UNIFIED RUN ===
def load_unified_run(path):
    return pd.read_csv(path)

# === FEATURE ENGINEERING FUNCTIONS ===
def calculate_sei(df):
    # Avoid division by zero errors
    df = df.copy()
    df['SEI'] = (df.get('Speed (m/s)', np.nan) * df.get('Power (w/kg)', np.nan)) / df.get('heart_rate', np.nan)
    return df

def calculate_heart_rate_drift(df):
    # Compare average HR first half vs second half
    halfway = len(df) // 2
    hr_first_half = df['heart_rate'][:halfway].mean()
    hr_second_half = df['heart_rate'][halfway:].mean()
    if hr_first_half > 0:
        hr_drift_pct = ((hr_second_half - hr_first_half) / hr_first_half) * 100
    else:
        hr_drift_pct = np.nan
    return hr_drift_pct

def calculate_power_drift(df):
    halfway = len(df) // 2
    pw_first_half = df['Power (w/kg)'][:halfway].mean()
    pw_second_half = df['Power (w/kg)'][halfway:].mean()
    if pw_first_half > 0:
        pw_drift_pct = ((pw_second_half - pw_first_half) / pw_first_half) * 100
    else:
        pw_drift_pct = np.nan
    return pw_drift_pct

def detect_fatigue(df):
    # Simple heuristic: GCT increase + Cadence drop
    gct_trend = df['Ground Time (ms)'].diff().mean()
    cadence_trend = df['Cadence (spm)'].diff().mean()
    if gct_trend > 0 and cadence_trend < 0:
        return True
    else:
        return False

# === MAIN EXECUTION ===
if __name__ == "__main__":
    df = load_unified_run(UNIFIED_RUN_PATH)

    df = calculate_sei(df)

    # Calculate summary features
    features = {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "avg_sei": df['SEI'].mean(),
        "heart_rate_drift_pct": calculate_heart_rate_drift(df),
        "power_drift_pct": calculate_power_drift(df),
        "fatigue_detected": detect_fatigue(df)
    }

    features_df = pd.DataFrame([features])

    os.makedirs(os.path.dirname(OUTPUT_FEATURES_PATH), exist_ok=True)
    features_df.to_csv(OUTPUT_FEATURES_PATH, index=False)

    print(f"✅ Feature dataset saved to {OUTPUT_FEATURES_PATH}")
