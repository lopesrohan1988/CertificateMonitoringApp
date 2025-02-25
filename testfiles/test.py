import socket
import ssl

hostname = 'google.com'
port = 443

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_default_certs()

with socket.create_connection((hostname, port)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        cert = ssock.getpeercert()
        print(cert)


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