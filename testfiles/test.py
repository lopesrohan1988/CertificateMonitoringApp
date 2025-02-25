import socket
from OpenSSL import SSL
from OpenSSL.crypto import dump_certificate, FILETYPE_PEM
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend

def get_certificate_chain(url):
    hostname = url.split("//")[1]  # Extract hostname
    port = 443  # Default HTTPS port

    # Create a context
    context = SSL.Context(SSL.TLSv1_2_METHOD)

    # Disable verification
    context.set_verify(ssl.CERT_NONE, None)

    # Create a connection
    sock = SSL.Connection(context, socket.create_connection((hostname, port)))

    # Establish the connection
    sock.set_connect_state()
    sock.set_tlsext_host_name(hostname.encode())
    sock.do_handshake()

    # Get the certificate chain
    cert_chain = sock.get_peer_cert_chain()

    # Convert the certificates to PEM format
    pem_chain = []
    for cert in cert_chain:
        pem_chain.append(dump_certificate(FILETYPE_PEM, cert).decode())

    # Parse the certificates
    parsed_chain = []
    for i, pem_cert in enumerate(pem_chain):
        cert_obj = x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())
        is_leaf = i == 0
        is_root = i == len(pem_chain) - 1
        is_intermediate = not is_leaf and not is_root
        parsed_chain.append({
            "certificate_pem": pem_cert,
            "issuer": cert_obj.issuer,
            "subject": cert_obj.subject,
            "valid_from": cert_obj.not_valid_before_utc,
            "valid_to": cert_obj.not_valid_after_utc,
            "is_leaf": is_leaf,
            "is_intermediate": is_intermediate,
            "is_root": is_root
        })

    return parsed_chain

url = "https://www.google.com"
cert_chain = get_certificate_chain(url)

for cert in cert_chain:
    print(cert)