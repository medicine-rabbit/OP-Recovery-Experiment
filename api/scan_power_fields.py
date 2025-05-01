from fitparse import FitFile

def extract_power_fields(fitfile_path):
    fitfile = FitFile(fitfile_path)
    power_fields = set()

    for record in fitfile.get_messages("record"):
        for field in record:
            if "power" in field.name.lower():
                power_fields.add(field.name)

    return sorted(power_fields)

print("Garmin FIT fields:")
print(extract_power_fields("model_queue/garmin.fit"))

print("\nStryd FIT fields:")
print(extract_power_fields("model_queue/stryd.fit"))
