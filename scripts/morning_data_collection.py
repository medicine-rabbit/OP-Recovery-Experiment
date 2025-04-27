from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError
)

from datetime import date, timedelta
import getpass
import yaml
import os

# Step 1: Login
email = input("Enter your Garmin email: ")
password = getpass.getpass("Enter your Garmin password: ")
client = Garmin(email, password)
client.login()

# Step 2: Get today's and yesterday's date
today_obj = date.today()
yesterday_obj = today_obj - timedelta(days=1)

today = today_obj.isoformat()
yesterday = yesterday_obj.isoformat()


# Step 3: Pull yesterday's health data
hrv_data = client.get_body_battery(yesterday)
stress_data = client.get_stress_data(yesterday)
sleep_data = client.get_sleep_data(yesterday)
hr_data = client.get_heart_rates(yesterday)

# Step 4: Manual inputs
grip_strength = input("Enter today's grip strength (kg): ")
body_weight = input("Enter today's body weight (kg): ")

# Step 5: Package into dict
daily_entry = {
    "log_date": today,                           # date you collected data
    "garmin_physiology_date": yesterday,         # Garmin's physiological data date
    "grip_strength_kg": float(grip_strength),
    "body_weight_kg": float(body_weight),
    "hrv_data": hrv_data,
    "stress_data": stress_data,
    "sleep_data": sleep_data,
    "hr_data": hr_data
}

# Step 6: Save as YAML in experiment directory

# Use yesterday_obj directly to extract formatted components
year = yesterday_obj.strftime("%Y")
month = yesterday_obj.strftime("%m")
month_name = yesterday_obj.strftime("%b")  # e.g., Apr
day = yesterday_obj.strftime("%d")

log_dir = f"/home/daniel/OP_Recovery_Experiment/logs/{year}/{month}-{month_name}/{day}"
os.makedirs(log_dir, exist_ok=True)

log_path = os.path.join(log_dir, f"{day}.yaml")

with open(log_path, "w") as file:
    yaml.dump(daily_entry, file)

print(f"✅ Daily data saved to {log_path}")

