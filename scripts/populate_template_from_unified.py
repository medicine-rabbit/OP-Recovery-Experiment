import os
import yaml
from datetime import datetime

HUMAN_QUEUE_DIR = 'human_queue'
DATA_DIR = 'data'

def load_yaml(filepath):
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def save_yaml(data, filepath):
    with open(filepath, 'w') as f:
        yaml.dump(data, f, sort_keys=False)
    print(f"Updated template saved to {filepath}.")

def find_unified_run(date_str):
    """Locate the unified run file for a given date."""
    year, month, day = date_str.split('-')
    data_dir = os.path.join(DATA_DIR, year, month, day)
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"No data directory found for {date_str}")

    candidates = [f for f in os.listdir(data_dir) if 'unified_run' in f and f.endswith('.yaml')]
    if not candidates:
        raise FileNotFoundError(f"No unified run file found in {data_dir}")

    # Pick the most recent unified run
    candidates = sorted(candidates, reverse=True)
    return os.path.join(data_dir, candidates[0])

def calculate_sei(avg_power, avg_hr, avg_resp):
    """Simple SEI formula: Power / (HR / Respiration)"""
    if avg_hr and avg_resp and avg_resp > 0:
        return round(avg_power / (avg_hr / avg_resp), 2)
    else:
        return None

def populate_template_from_unified(template_filename):
    # 1. Load the partial template
    template_path = os.path.join(HUMAN_QUEUE_DIR, template_filename)
    template = load_yaml(template_path)

    # 2. Load unified run data
    date_str = template['training_session']['date']
    unified_run_path = find_unified_run(date_str)
    unified_run = load_yaml(unified_run_path)

    # 3. Extract basic averages
    avg_hr = unified_run.get('data', {}).get('avg_heart_rate', None)
    avg_garmin_power = unified_run.get('data', {}).get('avg_power_garmin', None)
    avg_stryd_power = unified_run.get('data', {}).get('avg_power_stryd', None)
    avg_resp_rate = unified_run.get('data', {}).get('avg_respiration_rate', None)

    avg_sei = calculate_sei(avg_garmin_power, avg_hr, avg_resp_rate)

    # 4. Insert values into template
    maf = template['maf_component']
    z2 = template['z2_heartlek_component']


    if avg_hr is not None: maf['avg_hr_bpm'] = avg_hr
    if avg_garmin_power is not None: maf['avg_garmin_power_watts'] = avg_garmin_power
    if avg_stryd_power is not None: maf['avg_stryd_power_watts'] = avg_stryd_power
    if avg_sei is not None: maf['avg_sei'] = avg_sei


    # 5. Fill split-level data if available
    splits = unified_run.get('data', {}).get('splits', [])
    if splits and len(splits) >= 5:
        maf['split_hr_bpm'] = [s.get('avg_hr', None) for s in splits[:5]]
        maf['split_garmin_power_watts'] = [s.get('avg_power_garmin', None) for s in splits[:5]]
        maf['split_stryd_power_watts'] = [s.get('avg_power_stryd', None) for s in splits[:5]]


    # 6. Save updated template back to human_queue
    save_yaml(template, template_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/populate_template_from_unified.py <TEMPLATE_FILENAME>")
    else:
        filename = sys.argv[1]
        populate_template_from_unified(filename)
