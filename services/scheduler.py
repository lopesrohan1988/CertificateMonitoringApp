import ssl
import datetime
import smtplib
from email.mime.text import MIMEText
import services.database as database
import config.config as config
import schedule
import time
import socket
from OpenSSL import SSL
from OpenSSL.crypto import dump_certificate, FILETYPE_PEM

from cryptography import x509
from cryptography.hazmat.backends import default_backend
import socket


def get_certificate_chain(url):
    hostname = url.split("//")[1]  # Extract hostname
    port = 443  # Default HTTPS port

    # Create a context
    context = SSL.Context(SSL.TLSv1_2_METHOD)

    # Disable verification
    context.set_verify(ssl.CERT_NONE, None)

    # Create a connection
    try:
        sock = SSL.Connection(context, socket.create_connection((hostname, port)))
    except (socket.gaierror, ConnectionRefusedError, OSError) as e:  # Catch hostname/connection errors
            print(f"Error connecting to {url}: {e}") # Print error for debugging. Remove in production
            return None  # Return None to indicate failure
    # Establish the connection
    sock.set_connect_state()
    sock.set_tlsext_host_name(hostname.encode())
    sock.do_handshake()

    # Get the certificate chain
    cert_chain = sock.get_peer_cert_chain()

    # Convert the certificates to PEM format
    pem_chain = []
    for cert in cert_chain:
        pem_chain.append(dump_certificate(FILETYPE_PEM, cert).decode())

    # Parse the certificates
    parsed_chain = []
    for i, pem_cert in enumerate(pem_chain):
        cert_obj = x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())
        is_leaf = i == 0
        is_root = i == len(pem_chain) - 1
        is_intermediate = not is_leaf and not is_root
        parsed_chain.append({
            "certificate_pem": pem_cert,
            "issuer": cert_obj.issuer,
            "subject": cert_obj.subject,
            "valid_from": cert_obj.not_valid_before_utc,
            "valid_to": cert_obj.not_valid_after_utc,
            "is_leaf": is_leaf,
            "is_intermediate": is_intermediate,
            "is_root": is_root
        })

    return parsed_chain


#Not use. Can be used if only leaf is needed
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
                        #print(str(ca_cert['subject']))
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

def send_email_alert(expiring_certs):
    """
    Sends a single email alert with details of all expiring certificates in a row format.

    Args:
        expiring_certs: A list of tuples, where each tuple contains:
                        (organization_name, organization_url, expiry_date, days_until_expiry)
    """
    subscribers = database.get_all_subscribers()
    if not subscribers:
        print("No subscribers found.")
        return

    # Create a formatted table with certificate details
    message = "The following certificates are expiring soon:\n\n"
    message += "| Organization | URL | Expiry Date | Days Until Expiry |\n"
    message += "|---|---|---|---| \n"  # Separator row

    for org_name, url, expiry_date, days_until_expiry in expiring_certs:
        message += f"| {org_name} | {url} | {expiry_date} | {days_until_expiry} |\n"

    msg = MIMEText(message)
    msg['Subject'] = "Certificate Expiry Alert"
    msg['From'] = config.ALERT_EMAIL
    #print(msg)
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
    #print(config.ALERT_THRESHOLD_DAYS)
    # Clear the certificates table before checking
    database.clear_certificates_table()
    organizations = database.get_all_organizations()
    expiring_certs =  []

    for org in organizations:
        #cert_chain = check_certificate(org['url'])
        cert_chain = get_certificate_chain(org['url'])
        if cert_chain:
            for cert_data in cert_chain:
                #expiry_date = datetime.datetime.strptime(cert_data['valid_to'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (cert_data['valid_to'] - datetime.datetime.now(datetime.timezone.utc)).days
                if days_until_expiry < config.ALERT_THRESHOLD_DAYS:
                    #send_email_alert(org['name'], org['url'], cert_data, days_until_expiry)
                    expiring_certs.append((org['name'], org['url'], cert_data['valid_to'], days_until_expiry))
                database.add_certificate(org["id"], cert_data) # Store in the database
        else: # Handle the case where cert_chain is None (connection/URL error)
            print(f"Could not retrieve certificate chain for {org['url']}") # Print error for debugging. Remove in production
            continue # or pass, depending on your error handling needs
    # Send a single email with all expiring certificates
    if expiring_certs:
        send_email_alert(expiring_certs)

# Schedule the certificate check (e.g., daily):
schedule.every().day.do(check_certificates_and_alert)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1) # Check every second

if __name__ == "__main__":
    run_scheduler()