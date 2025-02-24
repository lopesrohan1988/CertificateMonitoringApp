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

def add_certificate(org_id, cert_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(cert_data)
    try:
        cert_data['issuer'] = str(cert_data['issuer'])
        cert_data['subject'] = str(cert_data['subject'])
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

def get_all_subscribers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM subscribers")
    subscribers = [row for row in cursor.fetchall()]  # Extract email addresses
    conn.close()
    return subscribers