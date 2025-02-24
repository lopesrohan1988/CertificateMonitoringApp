import streamlit as st
import database
import scheduler
import datetime
import config
import pandas as pd
import re

# Initialize the database tables on first run:
database.create_tables()

st.set_page_config(page_title="Application Certificate Expiration Monitoring", page_icon=":lock:", layout="wide")
st.title("Application Certificate Expiration Monitoring")

# Styling adjustments
st.markdown("""
<style>
.dataframe {
    border: 1px solid #ddd;
}
.dataframe th {
    background-color: #f0f0f0;
    font-weight: bold;
}
.dataframe td {
    padding: 5px;
}
.dataframe tr:nth-child(even) {
    background-color: #f9f9f9;
}
.dataframe tr:hover {
    background-color: #e0e0e0;
}
.sidebar .sidebar-content {
    background-color: #f5f5f5;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)






# Sidebar enhancements
with st.sidebar:
    st.title("Actions")  # Sidebar title

    if st.button("Refresh", use_container_width=True):
        st.rerun()

    st.subheader("Manage Application URL")
    org_expander = st.expander("Add Application") # Expander for organization actions
    with org_expander:
        org_name = st.text_input("Application Name", placeholder="e.g., Example Inc.")
        org_url = st.text_input("Application URL", placeholder="e.g., https://example.com")
        if st.button("Add Application", use_container_width=True):
            url_regex = r"^https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"  # Basic URL regex
            if not re.match(url_regex, org_url):
                st.error("Invalid URL format. Please use a format like https://www.example.com")
            else:
                org_id = database.add_organization(org_name, org_url)
                if org_id:
                    st.success(f"Organization '{org_name}' added.")
                else:
                    st.error("Organization with this URL already exists.")

    st.subheader("Alert Subscriptions")
    subscribe_expander = st.expander("Manage Subscriptions")
    with subscribe_expander:
        with st.form(key='subscription_form'):
            subscriber_email = st.text_input("Enter your email:", placeholder="e.g., user@example.com")
            if st.form_submit_button("Subscribe"):
                if database.add_subscriber(subscriber_email):
                    st.success("Subscribed successfully!")
                else:
                    st.error("You are already subscribed.")


    st.subheader("Manual Checks")
    if st.button("Run Certificate Check", use_container_width=True):
        scheduler.check_certificates_and_alert()
        st.success("Certificate check completed. Check logs for any alerts.")

    # if st.button("Application Management", use_container_width=True):
    #     app_management()  # Call the app management function
    show_app_management = st.checkbox("Edit Application List")
    show_subscriber_management = st.checkbox("Show Subscriber Management")

def subscriber_management():
    """
    Function to handle the Subscriber Management page.
    """
    st.title("Subscriber Management")

    # Get all subscribers
    subscribers = database.get_all_subscribers()
    if subscribers:
        # Create a DataFrame
        df = pd.DataFrame(subscribers)

        # Display the DataFrame as an editable table (using st.data_editor)
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True
        )
        print(df.columns)
        print(edited_df.columns)
        # Update/Delete subscribers in the database
        if edited_df is not df:  # Check if any changes were made
            # Get a list of deleted IDs
            deleted_ids = set(df['id'].values) - set(edited_df['id'].values)

            for index, row in edited_df.iterrows():
                if row[0] not in df[0].values:  # New subscriber added
                    database.add_subscriber(row[1])
                elif row!= df.loc[index]:  # Subscriber updated
                    database.update_subscriber(row[0], row[1])

            # Delete subscribers
            for deleted_id in deleted_ids:
                database.delete_subscriber(deleted_id)  # Implement delete_subscriber in database.py

            st.success("Subscribers updated successfully!")

    else:
        st.info("No subscribers found.")

def app_management():
    """
    Function to handle the Application Management page.
    """
    st.title("Application Management")

    # Get all applications
    applications = database.get_all_organizations()
    if applications:
        # Create a DataFrame
        df = pd.DataFrame(applications)

        # Display the DataFrame as an editable table (using st.data_editor)
        # Make the 'id' column non-editable
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn(
                    "ID",
                    disabled=True,  # Make the 'id' column read-only
                )
            }
        )

        # Update the database with the changes
        if edited_df is not df:  # Check if any changes were made
            for index, row in edited_df.iterrows():
                # Assuming your database.update_organization function takes id, name, and url
                database.update_organization(row[0], row[1], row[2])
            #st.success("Applications updated successfully!")

    else:
        st.info("No applications found.")


def mainpage():
    organizations = database.get_all_organizations()
    all_certificate_data = []

    for org in organizations:
        certificates = database.get_certificates_by_org_id(org['id'])
        if certificates:
            for cert in certificates:
                expiry_date = datetime.datetime.strptime(cert['valid_to'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (expiry_date - datetime.datetime.now()).days
                expiry_warning = days_until_expiry

                row = {
                    "Organization": org['name'],
                    "URL": org['url'],
                    "Subject": cert['subject'],
                    "Valid From": cert['valid_from'],
                    "Valid To": cert['valid_to'],
                    "Expiry Warning": expiry_warning,
                    "Certificate PEM": cert['certificate_pem']
                }
                all_certificate_data.append(row)

    if all_certificate_data:
        df = pd.DataFrame(all_certificate_data)
        df = df.sort_values('Expiry Warning')
        #df = df.iloc[:, 1:]
        def color_expiry_warning(val):
            try:
                val = int(val)
            except ValueError:
                return ''

            color = 'red' if val < config.ALERT_THRESHOLD_DAYS else 'green'
            return f'color: {color}'

        styled_df = df.style.applymap(color_expiry_warning, subset=['Expiry Warning'])

        st.dataframe(styled_df, use_container_width=True) # Table uses full width

    else:
        st.info("No certificates found for any organization.")  # More informative message


if show_app_management:
    app_management()
elif show_subscriber_management:  # Add this elif block
    subscriber_management()
else:
    mainpage()