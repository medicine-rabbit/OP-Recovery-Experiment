from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError
)
from datetime import date, timedelta
import getpass
import yaml

# Step 1: Login
email = input("Enter your Garmin email: ")
password = getpass.getpass("Enter your Garmin password: ")
client = Garmin(email, password)
client.login()

# Step 2: Get today's and yesterday's date
today = date.today()
yesterday = today - timedelta(days=1)

# Step 3: Pull yesterday's health data
hrv_data = client.get_body_battery(yesterday.isoformat())
stress_data = client.get_stress_data(yesterday.isoformat())
sleep_data = client.get_sleep_data(yesterday.isoformat())
hr_data = client.get_heart_rates(yesterday.isoformat())

# Step 4: Manual inputs
grip_strength = input("Enter today's grip strength (kg): ")
body_weight = input("Enter today's body weight (kg): ")

# Step 5: Package into dict
daily_entry = {
    "date": str(yesterday),
    "grip_strength": float(grip_strength),
    "body_weight": float(body_weight),
    "hrv_data": hrv_data,
    "stress_data": stress_data,
    "sleep_data": sleep_data,
    "hr_data": hr_data
}

# Step 6: Save as YAML in experiment directory
with open(f"/path/to/experiment/logs/{yesterday}.yaml", "w") as file:
    yaml.dump(daily_entry, file)

print("Daily data saved successfully.")
