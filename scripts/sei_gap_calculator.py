import yaml
import os

INBOX_DIR = 'inbox'
TEMPLATE_FILENAME = 'your-maf-run-file.yaml'  # Replace with dynamic lookup later if you want

def calculate_sei_gap(filepath):
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)

    maf = data['training_session']['maf_component']

    # Pull necessary data
    split_power = maf.get('split_garmin_power', [])
    split_hr = maf.get('split_hr_bpm', [])
    split_respiration = maf.get('split_respiration_rate', [])

    if not (split_power and split_hr and split_respiration):
        print("Missing required split data for SEI calculation.")
        return

    split_sei = []
    for power, hr, rr in zip(split_power, split_hr, split_respiration):
        if rr == 0 or hr == 0:
            sei_value = None
        else:
            sei_value = power / (hr / rr)
        split_sei.append(round(sei_value, 3) if sei_value else None)

    # Average SEI
    avg_power = maf.get('avg_garmin_power_watts', None)
    avg_hr = maf.get('avg_hr_bpm', None)
    avg_rr = maf.get('avg_respiration_rate_bpm', None)

    if avg_power and avg_hr and avg_rr:
        avg_sei = round(avg_power / (avg_hr / avg_rr), 3)
    else:
        avg_sei = None

    # Update YAML structure
    maf['split_sei'] = split_sei
    maf['avg_sei'] = avg_sei

    # (Optional) calculate avg GAP if split GAP exists
    split_gap = maf.get('split_gap_min_per_km', [])
    if split_gap:
        maf['avg_gap_min_per_km'] = round(sum(split_gap) / len(split_gap), 2)

    # Save YAML back
    with open(filepath, 'w') as f:
        yaml.dump(data, f, sort_keys=False)

    print(f"SEI and GAP calculated and updated for {filepath}.")

if __name__ == "__main__":
    filepath = os.path.join(INBOX_DIR, TEMPLATE_FILENAME)
    calculate_sei_gap(filepath)
