import yaml
import os

def load_yaml(filepath):
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)

def save_yaml(filepath, data):
    with open(filepath, 'w') as file:
        yaml.dump(data, file, sort_keys=False)

def calculate_total_volume(results):
    total_volume = 0
    for exercise, sets in results.items():
        for weight in sets:
            if isinstance(weight, dict):
                total_volume += weight['weight'] * weight.get('reps', 1)
            else:
                total_volume += weight  # Assume 1 rep if no reps specified
    return total_volume

def calculate_fatigue(total_volume, rpe=8):
    # Simple model for now: volume divided by effort level
    return total_volume / rpe

def process_owl_session(filepath):
    session = load_yaml(filepath)

    # --- Calculate volume ---
    total_volume = calculate_total_volume(session['results'])

    # --- Calculate fatigue ---
    # For now, assume average RPE of 8 unless protocol says otherwise
    fatigue_score = calculate_fatigue(total_volume, rpe=8)

    # --- Insert biometrics if provided ---
    pre_hrv = session.get('pre_hrv', None)
    post_hrv = session.get('post_hrv', None)
    pre_resp = session.get('pre_respiration', None)
    post_resp = session.get('post_respiration', None)

    # --- Update session ---
    session['computed_metrics'] = {
        'total_volume_kg': total_volume,
        'fatigue_score': fatigue_score,
        'pre_hrv': pre_hrv,
        'post_hrv': post_hrv,
        'pre_respiration': pre_resp,
        'post_respiration': post_resp
    }

    # --- Save updated session ---
    save_yaml(filepath, session)

    print(f"Processed {filepath} successfully.")
    print(session['computed_metrics'])

# Example usage
if __name__ == "__main__":
    # Change this to your actual OWL YAML file path
    owl_file = "../logs/owl/2025-04-27-owl.yaml"
    process_owl_session(owl_file)
