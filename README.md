# 🛡️ Suspicious Login Detector

A Python and Streamlit-based cybersecurity project that analyzes login activity and identifies potentially suspicious behavior using multiple risk signals.

## 📌 About the Project

The Suspicious Login Detector is a rule-based cybersecurity system designed to analyze user login records and identify unusual or potentially risky login behavior.

The system examines information such as:

* Username
* Login location
* Login timestamp
* Failed login attempts
* Device information

Based on these signals, the system calculates a risk score and classifies the login as **LOW, MEDIUM, HIGH, or CRITICAL**.

The project also includes a Streamlit web interface for uploading login data and viewing the analysis through a dashboard.

## 🎯 Problem

Suspicious login activity can be an early indication of:

* Brute-force attempts
* Account compromise
* Unauthorized access
* Unusual device usage
* Rapid location changes

Manually checking large numbers of login records can be difficult. This project provides an automated way to analyze login activity and highlight potentially risky behavior.

## ⚙️ How It Works

```text
Login Data (CSV)
       ↓
Data Validation & Cleaning
       ↓
Remove Invalid / Duplicate Records
       ↓
Analyze Login Behavior
       ↓
Calculate Risk Score
       ↓
Risk Classification
       ↓
Dashboard / Alerts
```

## 🔍 Detection Signals

The system currently analyzes multiple signals:

| Signal                         | Description                                                 |
| ------------------------------ | ----------------------------------------------------------- |
| Failed Attempts                | Detects multiple failed login attempts                      |
| Unusual Login Time             | Identifies logins during unusual hours                      |
| Unknown Device                 | Detects login activity from an unknown device               |
| Device Change                  | Detects changes in the user's device                        |
| Rapid Location Change          | Detects location changes within a short time                |
| Rapid Repeated Login           | Detects repeated login activity within a short period       |
| Repeated Failed Login Activity | Detects repeated failed-login behavior within a time window |

## 🚦 Risk Levels

|  Score | Risk Level  |
| -----: | ----------- |
|   0–29 | 🟢 LOW      |
|  30–59 | 🟡 MEDIUM   |
|  60–79 | 🟠 HIGH     |
| 80–100 | 🔴 CRITICAL |

The score is based on multiple rule-based security signals.

## 🧹 Data Validation

The system also handles several data-quality problems, including:

* Missing values
* Invalid timestamps
* Invalid failed-attempt values
* Negative failed-attempt values
* Extremely large values
* Duplicate records
* Missing CSV columns
* Missing CSV files
* Future timestamps

Invalid records are handled safely instead of causing the entire program to crash.

## 🌐 Web Application

The project includes a Streamlit web interface.

The web application allows users to:

1. Upload a login CSV file
2. Analyze login activity
3. View risk scores
4. View detected reasons
5. See overall login statistics

## 🛠️ Technologies Used

* **Python**
* **Streamlit**
* **CSV**
* **Datetime**
* **Pandas / Streamlit data handling**
* **Git & GitHub**

## 📁 Project Structure

```text
Suspicious_Login_Detector/
│
├── detector.py       # Core detection and risk analysis
├── app.py            # Streamlit web application
├── login_data.csv    # Sample login dataset
└── README.md         # Project documentation
```

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/Santhosh221207/Suspicious-Login-Detector.git
```

### 2. Open the project

```bash
cd Suspicious-Login-Detector
```

### 3. Install Streamlit

```bash
python -m pip install streamlit
```

### 4. Run the web application

```bash
python -m streamlit run app.py
```

The application will open locally in your browser.

## 🧪 Example

A login with several suspicious signals may produce:

```text
User: Arun
Risk Score: 75
Risk Level: HIGH

Reasons:
- Very high failed-attempt count
- Unknown device
- Rapid location change
```

## 🚀 Future Improvements

Possible future improvements include:

* Machine-learning-based anomaly detection
* IP address analysis
* Geographic distance calculation
* Real-time login monitoring
* Email or notification alerts
* Database integration
* Authentication and user management
* Advanced cybersecurity dashboard
* Deployment as a public web application

## ⚠️ Project Status

This is an educational cybersecurity project and currently uses **rule-based risk detection**. A high risk score indicates potentially suspicious behavior and should not be treated as definitive proof of an attack.

## 👨‍💻 Author

**Santhosh Kumar A**

B.Tech Artificial Intelligence & Data Science
