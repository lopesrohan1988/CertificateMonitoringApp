import streamlit as st
import services.database as database

from components.subscriber_management import subscriber_management
from components.app_management import app_management
from components.mainpage import mainpage
from components.sidebar import sidebar

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



show_app_management, show_subscriber_management = sidebar()


if show_app_management:
    app_management()
elif show_subscriber_management:  # Add this elif block
    subscriber_management()
else:
    mainpage()