import csv
import os
from datetime import datetime, timedelta


# =========================================================
# SETTINGS
# =========================================================

REQUIRED_COLUMNS = {
    "user",
    "location",
    "time",
    "failed_attempts",
    "device"
}

FAILED_ATTEMPT_THRESHOLD = 5
RAPID_LOCATION_MINUTES = 5
RAPID_LOGIN_MINUTES = 2
REPEATED_LOGIN_WINDOW_MINUTES = 5

# Set this to False if you want to allow future timestamps
REJECT_FUTURE_TIMES = True


# =========================================================
# 1. READ CSV
# =========================================================

def read_data():

    file_name = "login_data.csv"

    # Check whether file exists
    if not os.path.exists(file_name):

        print("Error: login_data.csv was not found.")
        return []

    try:

        with open(
            file_name,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            # Check headers
            actual_columns = set(
                reader.fieldnames or []
            )

            missing_columns = (
                REQUIRED_COLUMNS - actual_columns
            )

            if missing_columns:

                print("Error: Missing CSV columns:")

                for column in sorted(missing_columns):
                    print("-", column)

                return []

            data = list(reader)

    except OSError as error:

        print("Error reading CSV file:", error)
        return []

    # Check empty CSV
    if not data:

        print("No login records found.")
        return []

    return data


# =========================================================
# 2. VALIDATE AND CLEAN DATA
# =========================================================

def validate_data(data):

    valid_data = []

    current_time = datetime.now()

    for row_number, login in enumerate(
        data,
        start=2
    ):

        # ---------------------------------------------
        # Get values safely
        # ---------------------------------------------

        user = login.get("user", "").strip()
        location = login.get("location", "").strip()
        time_text = login.get("time", "").strip()
        attempts_text = login.get(
            "failed_attempts",
            ""
        ).strip()

        device = login.get("device", "").strip()


        # ---------------------------------------------
        # Check required values
        # ---------------------------------------------

        if not user:

            print(
                f"Row {row_number}: "
                "Missing user. Skipped."
            )

            continue

        if not location:

            print(
                f"Row {row_number}: "
                f"{user} → Missing location. Skipped."
            )

            continue

        if not time_text:

            print(
                f"Row {row_number}: "
                f"{user} → Missing time. Skipped."
            )

            continue


        # ---------------------------------------------
        # Clean text
        # ---------------------------------------------

        user = user.strip()
        location = location.strip().lower()

        # Empty device becomes Unknown
        if not device:

            device = "Unknown"

        else:

            device = device.strip()


        # ---------------------------------------------
        # Convert date/time
        # ---------------------------------------------

        try:

            login_time = datetime.strptime(
                time_text,
                "%Y-%m-%d %H:%M"
            )

        except ValueError:

            print(
                f"Row {row_number}: "
                f"{user} → Invalid date/time. "
                "Skipped."
            )

            continue


        # ---------------------------------------------
        # Future timestamp check
        # ---------------------------------------------

        if (
            REJECT_FUTURE_TIMES
            and login_time > current_time
        ):

            print(
                f"Row {row_number}: "
                f"{user} → Future timestamp. "
                "Skipped."
            )

            continue


        # ---------------------------------------------
        # Convert failed attempts
        # ---------------------------------------------

        try:

            failed_attempts = int(
                attempts_text
            )

        except ValueError:

            print(
                f"Row {row_number}: "
                f"{user} → Invalid failed-attempt "
                "value. Treated as 0."
            )

            failed_attempts = 0


        # ---------------------------------------------
        # Negative attempts
        # ---------------------------------------------

        if failed_attempts < 0:

            print(
                f"Row {row_number}: "
                f"{user} → Negative failed attempts. "
                "Treated as 0."
            )

            failed_attempts = 0


        # ---------------------------------------------
        # Prevent unrealistic huge values
        # ---------------------------------------------

        if failed_attempts > 100000:

            print(
                f"Row {row_number}: "
                f"{user} → Extremely large failed "
                "attempt count. Capped at 100000."
            )

            failed_attempts = 100000


        # ---------------------------------------------
        # Store cleaned record
        # ---------------------------------------------

        valid_data.append({

            "user": user,
            "location": location,
            "time": login_time,
            "failed_attempts": failed_attempts,
            "device": device

        })

    return valid_data


# =========================================================
# 3. REMOVE EXACT DUPLICATES
# =========================================================

def remove_duplicates(data):

    unique_data = []
    seen_records = set()

    for login in data:

        record = (
            login["user"],
            login["location"],
            login["time"],
            login["failed_attempts"],
            login["device"]
        )

        if record in seen_records:

            print(
                login["user"],
                "→ Exact duplicate skipped."
            )

            continue

        seen_records.add(record)
        unique_data.append(login)

    return unique_data


# =========================================================
# 4. CALCULATE RISK
# =========================================================

def calculate_risk(
    login,
    previous_login,
    recent_logins
):

    user = login["user"]
    location = login["location"]
    login_time = login["time"]
    failed_attempts = login["failed_attempts"]
    device = login["device"]

    risk_score = 0
    reasons = []


    # =====================================================
    # SIGNAL 1: FAILED ATTEMPTS
    # =====================================================

    if failed_attempts >= 10:

        risk_score += 35

        reasons.append(
            "Very high failed-attempt count"
        )

    elif failed_attempts >= 5:

        risk_score += 25

        reasons.append(
            "Too many failed attempts"
        )

    elif failed_attempts >= 3:

        risk_score += 10

        reasons.append(
            "Several failed attempts"
        )


    # =====================================================
    # SIGNAL 2: UNUSUAL LOGIN TIME
    # =====================================================

    hour = login_time.hour

    if hour < 5:

        risk_score += 10

        reasons.append(
            "Unusual login time"
        )


    # =====================================================
    # SIGNAL 3: UNKNOWN DEVICE
    # =====================================================

    if device.lower() == "unknown":

        risk_score += 10

        reasons.append(
            "Unknown device"
        )


    # =====================================================
    # SIGNAL 4: NEW DEVICE
    # =====================================================

    if previous_login:

        previous_device = (
            previous_login["device"]
        )

        if (
            device.lower() != "unknown"
            and previous_device.lower() != "unknown"
            and device.lower()
            != previous_device.lower()
        ):

            risk_score += 10

            reasons.append(
                "Device changed"
            )


    # =====================================================
    # SIGNAL 5: RAPID LOCATION CHANGE
    # =====================================================

    if previous_login:

        previous_location = (
            previous_login["location"]
        )

        previous_time = (
            previous_login["time"]
        )

        time_difference = (
            login_time - previous_time
        )

        minutes = (
            time_difference.total_seconds()
            / 60
        )

        # Ignore negative time differences
        if minutes >= 0:

            if (
                previous_location != location
                and minutes <= RAPID_LOCATION_MINUTES
            ):

                risk_score += 30

                reasons.append(
                    "Rapid location change"
                )


    # =====================================================
    # SIGNAL 6: RAPID REPEATED LOGIN
    # =====================================================

    if previous_login:

        previous_time = (
            previous_login["time"]
        )

        time_difference = (
            login_time - previous_time
        )

        minutes = (
            time_difference.total_seconds()
            / 60
        )

        if (
            minutes >= 0
            and minutes <= RAPID_LOGIN_MINUTES
        ):

            risk_score += 10

            reasons.append(
                "Rapid repeated login"
            )


    # =====================================================
    # SIGNAL 7: REPEATED FAILED LOGINS
    # =====================================================

    recent_failed_attempts = 0
    recent_count = 0

    window_start = (
        login_time
        - timedelta(
            minutes=REPEATED_LOGIN_WINDOW_MINUTES
        )
    )

    for old_login in recent_logins:

        if (
            old_login["time"] >= window_start
            and old_login["time"] <= login_time
        ):

            recent_count += 1

            recent_failed_attempts += (
                old_login["failed_attempts"]
            )


    if (
        recent_count >= 2
        and recent_failed_attempts >= 5
    ):

        risk_score += 20

        reasons.append(
            "Repeated failed-login activity"
        )


    # =====================================================
    # LIMIT SCORE
    # =====================================================

    if risk_score > 100:

        risk_score = 100


    # =====================================================
    # RISK LEVEL
    # =====================================================

    if risk_score >= 80:

        risk = "CRITICAL 🔴"

    elif risk_score >= 60:

        risk = "HIGH 🟠"

    elif risk_score >= 30:

        risk = "MEDIUM 🟡"

    else:

        risk = "LOW 🟢"


    return risk_score, risk, reasons


# =========================================================
# 5. ANALYZE ALL LOGINS
# =========================================================

def analyze_logins(data):

    previous_login = {}
    recent_logins = {}

    for login in data:

        user = login["user"]

        # Get previous login for this user
        previous = previous_login.get(user)

        # Get recent login history
        if user not in recent_logins:

            recent_logins[user] = []

        history = recent_logins[user]


        # ---------------------------------------------
        # Calculate risk
        # ---------------------------------------------

        score, risk, reasons = calculate_risk(
            login,
            previous,
            history
        )


        # ---------------------------------------------
        # Display result
        # ---------------------------------------------

        print()

        print(
            login["user"],
            "→ Score:",
            score,
            "→",
            risk
        )

        if reasons:

            print("Reasons:")

            for reason in reasons:

                print("-", reason)


        # ---------------------------------------------
        # Save current login
        # ---------------------------------------------

        previous_login[user] = login

        history.append(login)


        # ---------------------------------------------
        # Keep only recent history
        # ---------------------------------------------

        cutoff_time = (
            login["time"]
            - timedelta(
                minutes=REPEATED_LOGIN_WINDOW_MINUTES
            )
        )

        recent_logins[user] = [

            old_login

            for old_login in history

            if old_login["time"] >= cutoff_time

        ]


# =========================================================
# 6. MAIN PROGRAM
# =========================================================

def main():

    print("======================================")
    print("   SUSPICIOUS LOGIN DETECTOR")
    print("======================================")

    # Read
    data = read_data()

    if not data:
        return


    # Validate
    valid_data = validate_data(data)

    if not valid_data:

        print()
        print(
            "No valid login records available."
        )

        return


    # Remove exact duplicates
    valid_data = remove_duplicates(
        valid_data
    )

    if not valid_data:

        print()
        print(
            "No unique login records available."
        )

        return


    # Sort by user and time
    valid_data.sort(
        key=lambda login: (
            login["user"].lower(),
            login["time"]
        )
    )


    # Analyze
    analyze_logins(valid_data)


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":

    main()