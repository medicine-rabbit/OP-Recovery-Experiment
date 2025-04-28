import yaml
import os
import re

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
                print(weight)
                total_volume += weight['weight'] * weight.get('reps', 1)
            else:
                # Extract numeric part if weight is a string like "28 kg"
                if isinstance(weight, str):
                    numeric_part = re.findall(r'\d+', weight)
                    if numeric_part:
                        total_volume += int(numeric_part[0])
                    else:
                        print(f"Warning: Could not extract number from {weight}")
                else:
                    total_volume += int(weight)  # already a number
    return total_volume


def calculate_fatigue(total_volume, rpe=8):
    # Simple model for now: volume divided by effort level
    return total_volume / rpe


def process_owl_session(session):
    # --- Calculate volume ---
    total_volume = calculate_total_volume(session['results'])

    # --- Calculate fatigue ---
    fatigue_score = calculate_fatigue(total_volume, rpe=8)

    # --- Insert biometrics if provided ---
    pre_hrv = session.get('pre_session_biometrics', {}).get('hrv', None)
    post_hrv = session.get('post_session_biometrics', {}).get('hrv', None)
    pre_resp = session.get('pre_session_biometrics', {}).get('respiration_rate', None)
    post_resp = session.get('post_session_biometrics', {}).get('respiration_rate', None)

    # --- Update session ---
    session['computed_metrics'] = {
        'total_volume_kg': total_volume,
        'fatigue_score': fatigue_score,
        'pre_hrv': pre_hrv,
        'post_hrv': post_hrv,
        'pre_respiration': pre_resp,
        'post_respiration': post_resp
    }

    return session  # ✅ return the enriched dictionary, no save here


# Example usage
if __name__ == "__main__":
    # Change this to your actual OWL YAML file path
    owl_file = "../logs/owl/2025-04-27-owl.yaml"
    process_owl_session(owl_file)
