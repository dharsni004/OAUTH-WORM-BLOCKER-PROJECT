# OAuth Worm Blocker
### Real-Time Detection and Auto-Revocation of Anomalous OAuth Token Activity

## Project Overview

OAuth Worm Blocker is an AI-powered cybersecurity project designed to detect suspicious OAuth token activities and prevent unauthorized access through anomaly detection and automated token revocation.

The system monitors OAuth token activities, analyzes behavioral patterns using Machine Learning, identifies potentially malicious activities, assigns risk levels, and generates security alerts through a centralized dashboard.

## Key Features

- **AI-Based Anomaly Detection:** Uses Isolation Forest Machine Learning to identify unusual OAuth token activities.
- **Token Monitoring:** Monitors token attributes, IP addresses, device information, locations, and access patterns.
- **Risk Assessment:** Assigns risk scores and categorizes suspicious activities.
- **Automatic Token Revocation:** Supports revocation of tokens identified as suspicious.
- **Email Alerts:** Sends notifications about detected security threats.
- **Interactive Dashboard:** Displays security events, anomaly details, risk levels, and revoked tokens.
- **Attack Simulation:** Simulates suspicious login and token activities for testing.
- **Event Logging:** Stores security events using SQLite.

## Technologies Used

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend | Flask |
| Machine Learning | Scikit-learn |
| ML Algorithm | Isolation Forest |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Dashboard | Web-based Dashboard |
| Notifications | Email Alerts |
| Development Environment | VS Code |

## System Workflow

1. OAuth token activity is received by the monitoring system.
2. Relevant token and user activity information is collected.
3. Machine Learning analyzes the activity.
4. Anomaly detection identifies suspicious behavior.
5. A risk score is generated.
6. High-risk token activity can trigger token revocation.
7. Email alerts notify administrators.
8. Events and security details are displayed on the dashboard.

## Project Structure

```text
OAuth-Worm-Blocker/
│
├── templates/
│
├── app.py
├── inject_attack.py
├── interceptor.py
├── interceptor_backup.py
├── setup_db.py
├── simulator.py
├── test_email.py
├── train_model.py
│
├── oauth_model.pkl
└── label_encoder.pkl
```

## Machine Learning Approach

The project uses the Isolation Forest algorithm to identify anomalous OAuth token activities based on monitored behavioral features.

The trained model analyzes activity patterns and helps distinguish normal behavior from potentially suspicious behavior.

## Testing and Evaluation

The system was tested in a configured local environment using simulated normal and suspicious OAuth activities.

The dashboard records event counts, detected anomalies, and revoked-token information. These results represent controlled project testing and should not be interpreted as independent real-world security performance measurements.

## Installation and Execution

### 1. Clone the Repository

```bash
git clone https://github.com/dharsni004/OAuth-Worm-Blocker.git
```

### 2. Open the Project Folder

```bash
cd OAuth-Worm-Blocker
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Environment (Windows)

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create your own local `.env` file with the required configuration and credentials. Never upload secrets to GitHub.

### 7. Initialize the Database

```bash
python setup_db.py
```

### 8. Run the Application

```bash
python app.py
```

Follow the application output to access the dashboard.

*Note: Execution commands and dependencies may need adjustment according to the final project configuration.*

## Security Note

- Never expose OAuth client secrets, access tokens, or email credentials.
- Keep `.env` files private.
- Local database files are excluded from the public repository.
- Use simulated activities for controlled testing.

## Project Objective

The primary objective of OAuth Worm Blocker is to strengthen OAuth security by combining Machine Learning-based anomaly detection, suspicious activity monitoring, risk assessment, and token revocation support.

## Author

**Cyber Security Project Team**

GitHub: https://github.com/dharsni004

---

**OAuth Worm Blocker – Intelligent OAuth Security Through AI-Based Anomaly Detection.**
