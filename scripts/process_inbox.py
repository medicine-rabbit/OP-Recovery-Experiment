import os
import yaml
from datetime import datetime
from scripts.process_owl import process_owl_session
# (You can import other processors later)

INBOX_DIR = "inbox/"
LOGS_DIR = "logs/"

def load_yaml(filepath):
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)

def move_to_logs(filepath, session):
    session_type = session.get('title', '').lower()

    # Parse date from session
    date_str = session.get('date')
    if not date_str:
        print(f"Warning: No date found in {filepath}")
        return

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")
    day = date_obj.strftime("%d")

    # Build output directory: logs/session_type/YYYY/MM/DD/
    output_dir = os.path.join(LOGS_DIR, session_type, year, month, day)
    os.makedirs(output_dir, exist_ok=True)

    # Use original filename
    filename = os.path.basename(filepath)
    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'w') as file:
        yaml.dump(session, file, sort_keys=False)

    print(f"Saved processed session to {output_path}")


def process_inbox():
    for filename in os.listdir(INBOX_DIR):
        if filename.endswith(".yaml"):
            filepath = os.path.join(INBOX_DIR, filename)
            session_data = load_yaml(filepath)
            session_type = session_data.get('title', '').lower()

            if session_type == "owl":
                enriched_session = process_owl_session(session_data)  # Use a function that returns enriched data
            elif session_type == "strides":
                print ("strides function not implemented")
                #enriched_session = process_strides_session(session)
            else:
                print(f"Unknown session type: {session_type}, skipping {filename}")
                continue


            move_to_logs(filepath, enriched_session)
            os.remove(filepath)  # Clean up inbox after processing

if __name__ == "__main__":
    process_inbox()


