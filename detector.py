import csv

previous_location = {}

with open("login_data.csv", "r") as file:
    data = csv.DictReader(file)

    for login in data:

        user = login["user"]
        location = login["location"]
        failed_attempts = int(login["failed_attempts"])

        risk_score = 0

        # Rule 1: Failed attempts
        if failed_attempts > 5:
            risk_score += 40

        # Rule 2: Location changed
        if user in previous_location:
            if previous_location[user] != location:
                risk_score += 30
        # Rule 3: Unusual login time
        hour = int(login["time"].split(":")[0])
        if hour >= 0 and hour < 5:
            risk_score += 20

        previous_location[user] = location

        # Risk level
        if risk_score >= 60:
            risk = "HIGH 🔴"
        elif risk_score >= 30:
            risk = "MEDIUM 🟡"
        else:
            risk = "LOW 🟢"

        print(user, "→ Score:", risk_score, "→", risk)