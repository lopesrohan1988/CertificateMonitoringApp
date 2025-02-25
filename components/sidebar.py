import streamlit as st
import re
import services.database as database
import services.scheduler as scheduler

def sidebar():  
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
        return show_app_management, show_subscriber_management


