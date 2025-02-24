import sqlite3
import config  # Your config file

def get_db_connection():
    conn = sqlite3.connect(config.DATABASE_FILE)  # Path to your SQLite database file
    conn.row_factory = sqlite3.Row # To access columns by name
    return conn

def create_tables():  # Create tables if they don't exist
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE
        )
    """)
    # cursor.execute("""
    #     DROP TABLE certificates
       
    # """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            certificate_pem TEXT ,
            issuer TEXT,
            subject TEXT,
            valid_from TEXT,
            valid_to TEXT,
            is_leaf BOOLEAN,
            is_intermediate BOOLEAN,
            is_root BOOLEAN,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE
        )
    """)

    conn.commit()
    conn.close()

def add_organization(name, url):
  conn = get_db_connection()
  cursor = conn.cursor()
  try:
      cursor.execute("INSERT INTO organizations (name, url) VALUES (?,?)", (name, url))
      conn.commit()
      return cursor.lastrowid # Return the ID of the new organization
  except sqlite3.IntegrityError: # Handle unique constraint violation
      return None # Organization with this URL already exists
  finally:
      conn.close()

def get_all_organizations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,name,url FROM organizations")
    organizations = cursor.fetchall()
    conn.close()
    return organizations

def get_organization_by_id(org_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM organizations WHERE id =?", (org_id,))
    organization = cursor.fetchone()
    conn.close()
    return organization



def clear_certificates_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM certificates")
        conn.commit()
    finally:
        conn.close()


def extract_common_name(subject):
    """
    Extracts the common name (CN) from a certificate subject.

    Args:
        subject: A tuple of tuples or a string representing the certificate subject.

    Returns:
        The common name (string) or None if not found.
    """
    common_name = None

    if isinstance(subject, tuple):  # Handle tuple of tuples
        for component in subject:
            if isinstance(component, tuple):
                for attribute, value in component:
                    if attribute == 'commonName':
                        common_name = value
                        return common_name  # Return immediately once found
            elif isinstance(component, str): # Handle CN as single string
                common_name = component
                return common_name

    elif isinstance(subject, str):  # Handle CN as a single string
        common_name = subject
        return common_name

    return None  # Return None if CN not found

def add_certificate(org_id, cert_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    try:
        cert_data['issuer'] = str(cert_data['issuer'])
        cert_data['subject'] = extract_common_name(cert_data['subject'])
        #print(cert_data['subject'])

        cursor.execute("""
            INSERT INTO certificates (
                organization_id, certificate_pem, issuer, subject, 
                valid_from, valid_to, is_leaf, is_intermediate, is_root
            ) VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            org_id, cert_data['certificate_pem'], cert_data['issuer'],
            cert_data['subject'], cert_data['valid_from'], cert_data['valid_to'],
            cert_data['is_leaf'], cert_data['is_intermediate'], cert_data['is_root']
        ))
        conn.commit()
    finally:
        conn.close()

def get_certificates_by_org_id(org_id):
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM certificates WHERE organization_id =?", (org_id,))
    certificates = cursor.fetchall()
    conn.close()
    return certificates

def update_subscriber(subscriber_id, new_email):
    """Updates a subscriber's email in the database.

    Args:
      subscriber_id: The ID of the subscriber to update.
      new_email: The new email address for the subscriber.

    Returns:
      True if the update was successful, False otherwise.
    """
    try:
        conn = get_db_connection()  # Assuming you have this function
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE subscribers 
            SET email =? 
            WHERE id =?
        """, (new_email, subscriber_id))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating subscriber: {e}")
        return False
    finally:
        if conn:
            conn.close()

def add_subscriber(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO subscribers (email) VALUES (?)", (email,))
        conn.commit()
        return True  # Subscription successful
    except sqlite3.IntegrityError:  # Handle unique constraint violation
        return False  # Email already exists
    finally:
        conn.close()


def delete_subscriber(subscriber_id):
    """Deletes a subscriber from the database.

    Args:
      subscriber_id: The ID of the subscriber to delete.

    Returns:
      True if the deletion was successful, False otherwise.
    """
    try:
        conn = get_db_connection()  # Assuming you have this function
        cursor = conn.cursor()

        cursor.execute("DELETE FROM subscribers WHERE id =?", (subscriber_id,))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting subscriber: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_subscribers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,email FROM subscribers")
    subscribers = [row for row in cursor.fetchall()]  # Extract email addresses
    conn.close()
    return subscribers


def update_organization(org_id, new_name, new_url):

    try:
        conn = get_db_connection()  # Replace with your database file
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE organizations 
            SET name =?, url =? 
            WHERE id =?
        """, (new_name, new_url, org_id))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating organization: {e}")
        return False
    finally:
        if conn:
            conn.close()