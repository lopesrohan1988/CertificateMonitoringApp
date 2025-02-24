# Application Certificate Expiration Monitoring

This Streamlit application provides a user-friendly interface for monitoring the expiration dates of application certificates. It allows you to add application URLs, subscribe for email alerts, and view certificate details with expiry warnings.

## Features

* **Add/Manage Applications:** Easily add and manage the URLs of the applications you want to monitor. A basic URL format validation is included.
* **Alert Subscriptions:** Subscribe to receive email notifications when certificates are nearing expiration.
* **Manual Checks:** Manually trigger a certificate check and alert generation.
* **Certificate Overview:** View a table of all certificates, including the organization, URL, subject, validity dates, and days until expiry. Expiry warnings are visually highlighted.
* **Subscriber Management:** (Optional) Manage subscriber email addresses through an interactive table. Add, update or delete subscriber emails.
* **Application Management:** (Optional) Manage application details through an interactive table. Update application names and URLs.
* **Responsive Design:** The layout adapts to different screen sizes for optimal viewing.

## Getting Started

### Prerequisites

* Python 3.7+
* Streamlit
* requests
* pyyaml (optional, for YAML configuration)
* schedule
* pandas

### Installation and Setup

1. Clone the repository:

```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://www.google.com/search?q=https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)  # Replace with your repo URL
cd YOUR_REPO_NAME

#Create a virtual environment (recommended):
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

#Install the required packages:
pip install -r requirements.txt

#Running the Application

streamlit run your_app_name.py  # Replace your_app_name.py with the name of your main script

CERTIFICATEMONITORINGAPP/
├── requirements.txt
├── your_app_name.py  # Your main Streamlit script
├── database.py       # Database interaction logic
├── scheduler.py      # Certificate checking and scheduling
├── config.py         # Configuration settings
└── README.md