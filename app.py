import streamlit as st
import database
import scheduler
import datetime
import config
import pandas as pd

# Initialize the database tables on first run:
database.create_tables()

st.title("Certificate Monitor")

# Use session state to track refresh
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0

if st.button("Refresh Organizations"):
    st.session_state.refresh_counter += 1  # Increment counter to trigger refresh


if st.sidebar.checkbox("Add Organization"):
    with st.sidebar:
        org_name = st.text_input("Organization Name")
        org_url = st.text_input("Organization URL")
        if st.button("Add"):
            org_id = database.add_organization(org_name, org_url)
            if org_id:
                st.success(f"Organization '{org_name}' added.")
            else:
                st.error("Organization with this URL already exists.")

if st.sidebar.checkbox("Subscribe to Alerts"):
    with st.sidebar.form(key='subscription_form'):
        subscriber_email = st.text_input("Enter your email:")
        if st.form_submit_button("Subscribe"):
            if database.add_subscriber(subscriber_email):
                st.success("Subscribed successfully!")
            else:
                st.error("You are already subscribed.")

organizations = database.get_all_organizations()

all_certificate_data = []  # List to store ALL certificate data

for org in organizations:
    certificates = database.get_certificates_by_org_id(org['id'])
    if certificates:
        for cert in certificates:
            expiry_date = datetime.datetime.strptime(cert['valid_to'], '%b %d %H:%M:%S %Y %Z')
            days_until_expiry = (expiry_date - datetime.datetime.now()).days
            expiry_warning = f"Expires in {days_until_expiry} days!" if days_until_expiry < config.ALERT_THRESHOLD_DAYS else ""

            row = {
                "Organization": org['name'],  # Add organization name to the table
                "URL": org['url'], # Add URL to the table
                "Subject": cert['subject'],
                "Valid From": cert['valid_from'],
                "Valid To": cert['valid_to'],
                "Expiry Warning": expiry_warning,
                "Download": "",  # Placeholder for the download button
                "Certificate PEM": cert['certificate_pem'] # Store PEM data for downloads
            }
            all_certificate_data.append(row)

if all_certificate_data:  # Check if any certificates were found at all
    df = pd.DataFrame(all_certificate_data)
    st.dataframe(df)  # Display the *single* table

    # Download Buttons (after the table)
    # for i, row in df.iterrows(): # Iterate through the rows of the DataFrame
    #     if row['Certificate PEM']:
    #         st.download_button(
    #             label=f"Download Certificate {i+1} for {row['Organization']}",
    #             data=row['Certificate PEM'],
    #             file_name=f"{row['Organization']}_cert_{i+1}.pem",
    #             mime="application/x-pem-file",
    #             key=f"download_{i}" # Unique key
    #         )
    #     else:
    #         st.write(f"Certificate {i+1} for {row['Organization']} not available for download.")
else:
    st.write("No certificates found for any organization.")

if st.sidebar.button("Run Certificate Check"): # Add manual check button
    scheduler.check_certificates_and_alert()
    st.sidebar.success("Certificate check completed. Check logs for any alerts.")

