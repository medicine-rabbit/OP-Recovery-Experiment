import os
import shutil
import yaml
from datetime import datetime

INBOX_DIR = 'inbox'
LOGS_DIR = 'logs'
EVENTS_DIR = 'events'

def load_yaml(filepath):
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


def process_activity(file_data, src_path):
    date = str(file_data['training_session']['date'])  # <== cast to string
    year, month, day = date.split('-')
    dest_dir = os.path.join(LOGS_DIR, year, month, day)
    os.makedirs(dest_dir, exist_ok=True)
    shutil.move(src_path, os.path.join(dest_dir, os.path.basename(src_path)))

def process_event(file_data, src_path):
    date_obj = file_data['event']['date']
    date = str(date_obj)
    year, month, day = date.split('-')
    dest_dir = os.path.join(EVENTS_DIR, year, month, day)
    os.makedirs(dest_dir, exist_ok=True)

    # --- Auto-generate event ID if missing ---
    if 'id' not in file_data['event'] or 'timestamp' in str(file_data['event']['id']):
        now = datetime.now()
        generated_id = f"event_{year}-{month}-{day}-{now.strftime('%H%M%S')}"
        file_data['event']['id'] = generated_id

        # Save the updated YAML immediately
        with open(src_path, 'w') as f:
            yaml.dump(file_data, f)

    shutil.move(src_path, os.path.join(dest_dir, os.path.basename(src_path)))



def process_inbox():
    for filename in os.listdir(INBOX_DIR):
        filepath = os.path.join(INBOX_DIR, filename)
        if not filename.endswith('.yaml'):
            continue

        file_data = load_yaml(filepath)

        if 'training_session' in file_data:
            process_activity(file_data, filepath)
        elif 'event' in file_data:
            process_event(file_data, filepath)
        else:
            print(f"Unknown file type: {filename}")

if __name__ == "__main__":
    process_inbox()
