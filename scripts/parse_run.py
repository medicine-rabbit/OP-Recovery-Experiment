# parse_run.py
from datetime import datetime
import pandas as pd
import fitparse
from datetime import datetime
import os

# === CONFIGURATION ===
GARMIN_FIT_PATH = "garmin.fit"
STRYD_CSV_PATH = "stryd.csv"
today = datetime.today().strftime("%Y-%m-%d")
OUTPUT_PATH = f"/home/daniel/OP_Recovery_Experiment/data/processed/unified_runs/{today}_run_unified.csv"


# === PARSE GARMIN FIT FILE ===



def parse_garmin_fit(fit_path):
    fitfile = fitparse.FitFile(fit_path)

    garmin_records = []
    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        if record_data:
            garmin_records.append(record_data)

    garmin_df = pd.DataFrame(garmin_records)

    if 'timestamp' in garmin_df.columns:
        garmin_df['timestamp'] = pd.to_datetime(garmin_df['timestamp'])
    else:
        raise ValueError("No timestamp found in Garmin FIT data!")

    return garmin_df

# === PARSE STRYD CSV FILE ===
def parse_stryd_csv(csv_path):
    stryd_df = pd.read_csv(csv_path)

    # Try to reconstruct elapsed time if it doesn't exist
    if 'Elapsed Time (s)' not in stryd_df.columns:
        if 'Timestamp (sec)' in stryd_df.columns:
            stryd_df['Elapsed Time (s)'] = stryd_df['Timestamp (sec)']
        else:
            # If no timestamps at all, simulate elapsed time by counting rows
            stryd_df['Elapsed Time (s)'] = range(len(stryd_df))

    return stryd_df


# === MERGE GARMIN AND STRYD DATA ===
def merge_garmin_stryd(garmin_df, stryd_df):
    # Assume both have "Elapsed Time" available or reconstruct it
    garmin_df['elapsed_seconds'] = (garmin_df['timestamp'] - garmin_df['timestamp'].iloc[0]).dt.total_seconds().round().astype(int)

    # Merge based on elapsed seconds
    merged = pd.merge_asof(
        stryd_df.sort_values('Elapsed Time (s)'),
        garmin_df.sort_values('elapsed_seconds'),
        left_on='Elapsed Time (s)',
        right_on='elapsed_seconds',
        direction='nearest',
        tolerance=1
    )

    return merged

# === MAIN EXECUTION ===
if __name__ == "__main__":
    garmin_df = parse_garmin_fit(GARMIN_FIT_PATH)
    stryd_df = parse_stryd_csv(STRYD_CSV_PATH)

    merged_df = merge_garmin_stryd(garmin_df, stryd_df)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    merged_df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Unified run data saved to {OUTPUT_PATH}")
