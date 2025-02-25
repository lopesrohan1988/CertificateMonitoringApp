import services.database as database
import streamlit as st
import pandas as pd

def subscriber_management():
    """
    Function to handle the Subscriber Management page.
    """
    st.title("Subscriber Management")

    # Get all subscribers
    subscribers = database.get_all_subscribers()
    if subscribers:
        # Create a DataFrame
        df = pd.DataFrame(subscribers, columns=['id', 'email'])

        # Display the DataFrame as an editable table (using st.data_editor)
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True
        )

        # Update/Delete subscribers in the database
        if edited_df is not df:  # Check if any changes were made
            # Get a list of deleted IDs
            deleted_ids = set(df['id'].values) - set(edited_df['id'].values)

            for index, row in edited_df.iterrows():
                if row['id'] not in df['id'].values:  # New subscriber added
                    database.add_subscriber(row['email'])
                elif not row.equals(df.loc[index]):  # Subscriber updated
                    database.update_subscriber(row['id'], row['email'])

            # Delete subscribers
            for deleted_id in deleted_ids:
                #print(deleted_id)
                database.delete_subscriber(deleted_id)  # Implement delete_subscriber in database.py

            st.success("Subscribers updated successfully!")

    else:
        st.info("No subscribers found.")