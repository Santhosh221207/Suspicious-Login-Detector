import csv
from datetime import datetime

# Store the previous login information for each user
previous_login = {}

with open("login_data.csv", "r") as file:
    data = csv.DictReader(file)

    for login in data:

        # Get data from CSV
        user = login["user"]
        location = login["location"]
        time = login["time"]
        failed_attempts = int(login["failed_attempts"])
        device = login["device"]

        # Convert text time into a Python datetime object
        login_time = datetime.strptime(time, "%Y-%m-%d %H:%M")

        # Start risk score
        risk_score = 0
        reasons = []

        # Rule 1: Too many failed attempts
        if failed_attempts >= 5:
            risk_score += 25
            reasons.append("Too many failed attempts")

        # Rule 2: Unusual login time
        hour = login_time.hour

        if hour >= 0 and hour < 5:
            risk_score += 10
            reasons.append("Unusual login time")

        # Rule 3: Unknown device
        if device == "Unknown":
            risk_score += 15
            reasons.append("Unknown device")

        # Rule 4: Rapid location change
        if user in previous_login:

            previous_location = previous_login[user]["location"]
            previous_time = previous_login[user]["time"]

            time_difference = login_time - previous_time
            minutes = time_difference.total_seconds() / 60

            if previous_location != location and minutes <= 5:
                risk_score += 30
                reasons.append("Rapid location change")

        # Save current login information
        previous_login[user] = {
            "location": location,
            "time": login_time
        }

        # Determine risk level
        if risk_score >= 80:
            risk = "CRITICAL 🔴"
        elif risk_score >= 60:
            risk = "HIGH 🟠"
        elif risk_score >= 30:
            risk = "MEDIUM 🟡"
        else:
            risk = "LOW 🟢"

        # Display result
        print()
        print(user, "→ Score:", risk_score, "→", risk)

        if reasons:
            print("Reasons:")
            for reason in reasons:
                print("-", reason)