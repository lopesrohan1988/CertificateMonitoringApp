
import services.database as database
import streamlit as st
import pandas as pd
import datetime
import config.config as config

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
                    "Expires in (days)": expiry_warning,
                   # "Certificate PEM": cert['certificate_pem']
                }
                all_certificate_data.append(row)

    if all_certificate_data:
        df = pd.DataFrame(all_certificate_data)
        df = df.sort_values('Expires in (days)')
        #df = df.iloc[:, 1:]
        def color_expiry_warning(val):
            try:
                val = int(val)
            except ValueError:
                return ''

            color = 'red' if val < config.ALERT_THRESHOLD_DAYS else 'green'
            return f'color: {color}'

        styled_df = df.style.applymap(color_expiry_warning, subset=['Expires in (days)'])

        st.dataframe(styled_df, use_container_width=True) # Table uses full width

    else:
        st.info("No certificates found for any organization.")  # More informative message