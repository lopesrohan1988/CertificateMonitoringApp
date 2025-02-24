DATABASE_FILE = "cert_monitor.db"
ALERT_EMAIL = "your_email@example.com"

#pip install dumb-smtp
SMTP_SERVER = "localhost1"  # e.g., smtp.gmail.com
SMTP_PORT = 8025  # Example port
SMTP_USERNAME = "your_email@example.com"
SMTP_PASSWORD = "your_email_password"  # Securely store this! (environment variables are better)
ALERT_THRESHOLD_DAYS = 10  # Days before expiry to send alert
DEBUG = True

# Consider using YAML for config if you have many settings:
# import yaml
# with open("config.yaml", "r") as f:
#     config = yaml.safe_load(f)