import os
import yaml
import shutil
from fitparse import FitFile
from datetime import datetime
from fitparse import FitFile  # Keep this import for future use inside unify_run
from unify_run import unify_run, save_unified_data


SYSTEM_CODES_PATH = 'system/codes.yaml'
MODEL_QUEUE_DIR = 'model_queue'
HUMAN_QUEUE_DIR = 'human_queue'
TEMPLATES_DIR = 'templates'
DATA_DIR = 'data'



def load_codes():
    with open(SYSTEM_CODES_PATH, 'r') as f:
        return yaml.safe_load(f)['codes']

def load_template(template_path):
    with open(template_path, 'r') as f:
        return yaml.safe_load(f)

def save_to_human_queue(data, filename):
    os.makedirs(HUMAN_QUEUE_DIR, exist_ok=True)
    filepath = os.path.join(HUMAN_QUEUE_DIR, filename)
    with open(filepath, 'w') as f:
        yaml.dump(data, f, sort_keys=False)
    print(f"Saved partially filled template to {filepath}.")

def find_fit_files():
    """Find two most recent .fit files in model_queue."""
    fits = [f for f in os.listdir(MODEL_QUEUE_DIR) if f.endswith('.fit')]
    fits = sorted(fits, key=lambda x: os.path.getmtime(os.path.join(MODEL_QUEUE_DIR, x)), reverse=True)
    if len(fits) < 2:
        raise Exception("Not enough .fit files found in model_queue.")
    return fits[:2]

def detect_device_type(fit_path):
    """Detect if FIT file is from Garmin or Stryd."""
    try:
        fitfile = FitFile(fit_path)
        for record in fitfile.get_messages('device_info'):
            fields = {field.name: field.value for field in record}
            manufacturer = fields.get('manufacturer')
            if manufacturer is not None:
                if isinstance(manufacturer, int):
                    if manufacturer == 1:
                        return 'garmin'
                    elif manufacturer == 222:
                        return 'stryd'
                elif isinstance(manufacturer, str):
                    manufacturer = manufacturer.lower()
                    if 'garmin' in manufacturer:
                        return 'garmin'
                    if 'stryd' in manufacturer:
                        return 'stryd'
    except Exception as e:
        print(f"Warning: could not read {fit_path}: {e}")
    return None

def assign_garmin_stryd(fit1_path, fit2_path):
    device1 = detect_device_type(fit1_path)
    device2 = detect_device_type(fit2_path)

    if device1 == 'garmin' and device2 == 'stryd':
        return fit1_path, fit2_path
    elif device2 == 'garmin' and device1 == 'stryd':
        return fit2_path, fit1_path
    else:
        # Fallback: try filename matching
        if 'stryd' in fit1_path.lower():
            return fit2_path, fit1_path
        elif 'stryd' in fit2_path.lower():
            return fit1_path, fit2_path
        else:
            raise Exception(f"Could not reliably determine device types: {device1}, {device2}")






def generate_template(code):
    codes = load_codes()

    if code not in codes:
        print(f"Code {code} not found in {SYSTEM_CODES_PATH}.")
        return

    spec_info = codes[code]
    template_path = os.path.join(TEMPLATES_DIR, spec_info['template'])

    # Load blank template
    template = load_template(template_path)

    # Find and parse FIT files
    fit_files = find_fit_files()
    fit1_path = os.path.join(MODEL_QUEUE_DIR, fit_files[0])
    fit2_path = os.path.join(MODEL_QUEUE_DIR, fit_files[1])

    device1 = detect_device_type(fit1_path)
    device2 = detect_device_type(fit2_path)



    garmin_fit, stryd_fit = assign_garmin_stryd(fit1_path, fit2_path)


    # Call unify_run
    unified_data, timestamp = unify_run(garmin_fit, stryd_fit)
    save_unified_data(unified_data, timestamp)

    # Fill only basic fields in template
    today = datetime.today().strftime('%Y-%m-%d')
    template['training_session']['date'] = today
    template['training_session']['subtype'] = spec_info['name'].replace('running_', '')  # optional simplification

    # Save partially filled template
    filename = f"{today}-{spec_info['name']}.yaml"
    save_to_human_queue(template, filename)

    print(f"Template generation complete for {code}.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/generate_template.py <CODE>")
    else:
        code = sys.argv[1]
        generate_template(code)
