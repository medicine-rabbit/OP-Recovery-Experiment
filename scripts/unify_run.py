import os
import yaml
import pandas as pd
from fitparse import FitFile
from datetime import datetime

def parse_fit_file(filepath, prefix=None):
    fitfile = FitFile(filepath)
    records = []

    for record in fitfile.get_messages('record'):
        fields = {field.name: field.value for field in record if field.value is not None}
        records.append(fields)

    df = pd.DataFrame(records)

    # Optionally prefix columns to avoid name collision during merge
    if prefix:
        df = df.add_prefix(prefix + '_')

    return df

def unify_run(garmin_fit_path, stryd_fit_path):
    """Parse and merge Garmin and Stryd data into a structured unified dictionary."""
    # 1. Parse Garmin and Stryd FIT files
    garmin_df = parse_fit_file(garmin_fit_path, prefix='garmin')
    stryd_df = parse_fit_file(stryd_fit_path, prefix='stryd')

    # 2. Preprocessing: compute elapsed time
    if 'garmin_timestamp' in garmin_df:
        garmin_df['elapsed_time_s'] = (garmin_df['garmin_timestamp'] - garmin_df['garmin_timestamp'].iloc[0]).dt.total_seconds()
    if 'stryd_timestamp' in stryd_df:
        stryd_df['elapsed_time_s'] = (stryd_df['stryd_timestamp'] - stryd_df['stryd_timestamp'].iloc[0]).dt.total_seconds()

    # 3. Merge Garmin and Stryd on elapsed time
    garmin_df_sorted = garmin_df.sort_values('elapsed_time_s')
    stryd_df_sorted = stryd_df.sort_values('elapsed_time_s')

    merged_df = pd.merge_asof(
        garmin_df_sorted,
        stryd_df_sorted,
        on='elapsed_time_s',
        suffixes=('', '_stryd'),
        direction='nearest'
    )

    # 4. Compute Session Averages
    avg_hr = float(merged_df['garmin_heart_rate'].mean()) if 'garmin_heart_rate' in merged_df else None
    avg_power_garmin = float(merged_df['garmin_power'].mean()) if 'garmin_power' in merged_df else None
    avg_power_stryd = float(merged_df['stryd_power'].mean()) if 'stryd_power' in merged_df else None
    avg_resp_rate = float(merged_df['garmin_respiration_rate'].mean()) if 'garmin_respiration_rate' in merged_df else None


    # 5. Build simple 1-km splits (based on distance)
    splits = []
    if 'garmin_distance' in merged_df:
        merged_df['split_km'] = (merged_df['garmin_distance'] // 1000).astype(int)
        for split_idx, split_df in merged_df.groupby('split_km'):
            if split_idx >= 0:
                split_summary = {
                    "avg_heart_rate": float(round(avg_hr, 1)) if avg_hr is not None else None,
                    "avg_power_garmin": float(round(avg_power_garmin, 1)) if avg_power_garmin is not None else None,
                    "avg_power_stryd": float(round(avg_power_stryd, 1)) if avg_power_stryd is not None else None,
                    "avg_respiration_rate": float(round(avg_resp_rate, 1)) if avg_resp_rate is not None else None,
                }
                splits.append(split_summary)

    # 6. Build Unified Data Dictionary
    unified_data = {
        "metadata": {
            "sources": [garmin_fit_path, stryd_fit_path],
            "merge_time": datetime.now().isoformat()
        },
        "data": {
            "avg_heart_rate": round(avg_hr, 1) if avg_hr else None,
            "avg_power_garmin": round(avg_power_garmin, 1) if avg_power_garmin else None,
            "avg_power_stryd": round(avg_power_stryd, 1) if avg_power_stryd else None,
            "avg_respiration_rate": round(avg_resp_rate, 1) if avg_resp_rate else None,
            "splits": splits
        }
    }

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return unified_data, timestamp

def save_unified_data(unified_data, timestamp):
    year = datetime.today().strftime('%Y')
    month = datetime.today().strftime('%m')
    day = datetime.today().strftime('%d')
    save_dir = os.path.join('data', year, month, day)
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, f"{timestamp}_unified_run.yaml")

    with open(filepath, 'w') as f:
        yaml.dump(unified_data, f, sort_keys=False)

    print(f"Saved unified run data to {filepath}.")

if __name__ == "__main__":
    print("This module is intended to be imported, not run directly.")
