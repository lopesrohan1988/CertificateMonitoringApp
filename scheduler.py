import requests
import ssl
import datetime
import smtplib
from email.mime.text import MIMEText
import database
import config
import schedule
import time

import socket
import ssl

def check_certificate(url):
    hostname = url.split("//")[1]  # Extract hostname
    port = 443  # Default HTTPS port
    #print(hostname)
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_default_certs()

        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                #print(cert)
                # Extract certificate chain (corrected)
                cert_chain =  []
                cert_chain.append({  # Add the server's certificate first
                    "certificate_pem": ssl.DER_cert_to_PEM_cert(cert['tbsCertificate']) if 'tbsCertificate' in cert else None,
                    "issuer": cert['issuer'],
                    "subject": cert['subject'],
                    "valid_from": cert['notBefore'],
                    "valid_to": cert['notAfter'],
                    "is_leaf": True,  # Server cert is always the leaf
                    "is_intermediate": False,
                    "is_root": False
                })

                # Get the chain of trust if available. This is not always available.
                try:
                    chain = ssock.get_verified_chain()
                    for ca_cert in chain:
                        cert_chain.append({
                            "certificate_pem": ssl.DER_cert_to_PEM_cert(ca_cert.to_cryptography().public_bytes(ssl.DER)),
                            "issuer": str(ca_cert['issuer']),
                            "subject": str(ca_cert['subject']),
                            "valid_from": str(ca_cert['notBefore']),
                            "valid_to": str(ca_cert['notAfter']),
                            "is_leaf": False,
                            "is_intermediate": True,
                            "is_root": False
                        })

                except AttributeError:
                    pass

                return cert_chain

    except Exception as e:
        print(f"Error checking certificate for {url}: {e}")
        return None

def send_email_alert(org_name, url, cert_data, days_until_expiry):
    subscribers = database.get_all_subscribers()
    if not subscribers:
        print("No subscribers found.")
        return

    message = f"Certificate for {org_name} ({url}) expires in {days_until_expiry} days!\n\nDetails:\n{cert_data}"
    msg = MIMEText(message)
    msg['Subject'] = f"Certificate Expiry Alert: {org_name}"
    msg['From'] = config.ALERT_EMAIL

    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            for subscriber_email in subscribers:
                msg['To'] = subscriber_email
                server.send_message(msg)
                print(f"Email alert sent to {subscriber_email}")
    except Exception as e:
        print(f"Error sending email alert: {e}")

def check_certificates_and_alert():
    # Clear the certificates table before checking
    database.clear_certificates_table()
    
    organizations = database.get_all_organizations()
    for org in organizations:
        cert_chain = check_certificate(org['url'])
        if cert_chain:
            for cert_data in cert_chain:
                expiry_date = datetime.datetime.strptime(cert_data['valid_to'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (expiry_date - datetime.datetime.now()).days
                if days_until_expiry < config.ALERT_THRESHOLD_DAYS:
                    send_email_alert(org.name, org.url, cert_data, days_until_expiry)
                database.add_certificate(org["id"], cert_data) # Store in the database

# Schedule the certificate check (e.g., daily):
schedule.every().day.do(check_certificates_and_alert)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1) # Check every second

if __name__ == "__main__":
    run_scheduler()