import os
import shutil
import yaml

HUMAN_QUEUE_DIR = 'human_queue'
LOGS_DIR = 'logs'
EVENTS_DIR = 'events'

def load_yaml(filepath):
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def move_file(src, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    shutil.move(src, os.path.join(dest_dir, os.path.basename(src)))

def is_training_session_complete(data):
    feedback = data['training_session'].get('subjective_feedback', {})
    required_fields = ['perceived_effort_rpe', 'soreness_next_day', 'fatigue_event_occurred']

    for field in required_fields:
        if feedback.get(field) in (None, '', '{{' + field + '}}'):
            return False
    return True

def is_event_complete(data):
    event = data['event']
    required_fields = ['date', 'time', 'type', 'severity', 'description', 'resolution_status']
    for field in required_fields:
        if event.get(field) in (None, '', '{{' + field + '}}'):
            return False
    return True

def process_human_queue():
    for filename in os.listdir(HUMAN_QUEUE_DIR):
        filepath = os.path.join(HUMAN_QUEUE_DIR, filename)
        if not filename.endswith('.yaml'):
            continue

        file_data = load_yaml(filepath)

        if 'training_session' in file_data:
            if is_training_session_complete(file_data):
                date = str(file_data['training_session']['date'])
                year, month, day = date.split('-')
                dest_dir = os.path.join(LOGS_DIR, year, month, day)
                move_file(filepath, dest_dir)
                print(f"Finalized training session {filename} to {dest_dir}.")
            else:
                print(f"Training session {filename} is still incomplete. Fix and retry.")

        elif 'event' in file_data:
            if is_event_complete(file_data):
                date = str(file_data['event']['date'])
                year, month, day = date.split('-')
                dest_dir = os.path.join(EVENTS_DIR, year, month, day)
                move_file(filepath, dest_dir)
                print(f"Finalized event {filename} to {dest_dir}.")
            else:
                print(f"Event {filename} is still incomplete. Fix and retry.")

        else:
            print(f"Unknown file type: {filename}. Leaving it in human queue.")

if __name__ == "__main__":
    process_human_queue()
