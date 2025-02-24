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