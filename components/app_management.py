import services.database as database
import streamlit as st
import pandas as pd

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