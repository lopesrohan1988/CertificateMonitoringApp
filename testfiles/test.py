import ssl
import socket

def get_certificate_chain(hostname, port=443):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            der_cert = ssock.getpeercert(binary_form=True)
            cert = ssock.getpeercert()

            # Get the certificate chain
            chain = []
            chain.append({
                "certificate_pem": ssl.DER_cert_to_PEM_cert(der_cert),
                "issuer": cert['issuer'],
                "subject": cert['subject'],
                "valid_from": cert['notBefore'],
                "valid_to": cert['notAfter'],
                "is_leaf": True,  # Server cert is always the leaf
                "is_intermediate": False,
                "is_root": False
            })

            # Get the intermediate certificates from the server
            try:
                intermediate_der_certs = ssock.getpeercertchain()
                if intermediate_der_certs is not None:
                    for intermediate_der_cert in intermediate_der_certs:
                        intermediate_cert = ssl.PEM_cert_to_DER_cert(ssl.DER_cert_to_PEM_cert(intermediate_der_cert))
                        chain.append({
                            "certificate_pem": ssl.DER_cert_to_PEM_cert(intermediate_der_cert),
                            "issuer": ssl.PEM_cert_to_DER_cert(ssl.DER_cert_to_PEM_cert(intermediate_der_cert)).issuer(),
                            "subject": ssl.PEM_cert_to_DER_cert(ssl.DER_cert_to_PEM_cert(intermediate_der_cert)).subject(),
                            "valid_from": ssl.PEM_cert_to_DER_cert(ssl.DER_cert_to_PEM_cert(intermediate_der_cert)).not_valid_before(),
                            "valid_to": ssl.PEM_cert_to_DER_cert(ssl.DER_cert_to_PEM_cert(intermediate_der_cert)).not_valid_after(),
                            "is_leaf": False,
                            "is_intermediate": True,
                            "is_root": False
                        })
                else:
                    print(f"Warning: No intermediate certificates provided by {hostname}.")
            except AttributeError:
                print(f"Warning: Unable to retrieve intermediate certificates from {hostname}.")

            # Get the root certificate
            try:
                root_der_cert = ssl.get_server_certificate((hostname, port))
                if root_der_cert is not None:
                    root_cert = ssl.PEM_cert_to_DER_cert(root_der_cert)
                    chain.append({
                        "certificate_pem": root_der_cert,
                        "issuer": root_cert.issuer(),
                        "subject": root_cert.subject(),
                        "valid_from": root_cert.not_valid_before(),
                        "valid_to": root_cert.not_valid_after(),
                        "is_leaf": False,
                        "is_intermediate": False,
                        "is_root": True
                    })
                else:
                    print(f"Warning: No root certificate provided by {hostname}.")
            except AttributeError:
                print(f"Warning: Unable to retrieve root certificate from {hostname}.")

    return chain

hostname = "www.example.com"
cert_chain = get_certificate_chain(hostname)
for cert in cert_chain:
    print(cert)