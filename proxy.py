import socket   # Import socket library for network connections
import ssl      # Import ssl library for secure socket layer operations
import struct   # Import struct for packing and unpacking data
import logging  # Import logging for logging messages

# Create a named logger
logger = logging.getLogger("DNSProxy")
logging.basicConfig(
    level=logging.INFO
)  # Configure the logging to display INFO level messages


def start_proxy(listen_addr, tls_dns_server_addr):
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the specified listening address and port
    sock.bind(listen_addr)
    # Listen for incoming connections (with a maximum backlog of 2 connection)
    sock.listen(2)
    # Log that the proxy is listening
    logger.info(f"Listening for DNS on {listen_addr}")

    # Infinite loop to continuously accept new connections
    while True:
        # Accept an incoming connection
        client, _ = sock.accept()
        # Handle the client connection in a separate function
        handle_client(client, tls_dns_server_addr)


def handle_client(client_conn, tls_dns_server_addr):
    # Use 'with' to automatically close the connection when done
    with client_conn:
        # Receive the first 2 bytes indicating the query length
        length = client_conn.recv(2)
        # If no data is received, return and close the connection
        if not length:
            return
        # Unpack the length bytes to get the actual length
        length = struct.unpack("!H", length)[0]
        # Receive the query data based on the previously received length
        query = client_conn.recv(length)
        # If no query data is received, return and close the connection
        if not query:
            return

        # Parse and log the domain name from the query
        domain_name = parse_domain_name(query)
        logger.info(f"Received DNS query for {domain_name}")

        # Create a default SSL context for secure connections
        context = ssl.create_default_context()

        # Establish a secure connection to the specified TLS address
        with socket.create_connection(tls_dns_server_addr) as raw_sock:
            # Wrap the raw socket with SSL for encryption
            with context.wrap_socket(raw_sock, server_hostname=tls_dns_server_addr[0]) as tls_conn:
                # Send the query length and query data over the secure connection
                tls_conn.send(struct.pack("!H", length) + query)
                # Loop to continuously forward data from the TLS connection back to the client
                while True:
                    # Receive data from the TLS connection
                    data = tls_conn.recv(4096)
                    # If no data is received, break the loop
                    if not data:
                        break
                    # Send the received data back to the client
                    client_conn.send(data)


def parse_domain_name(query):
    # Start reading the query from byte 12 to skip the DNS header
    position = 12
    domain_name = ""
    # Loop to extract the domain name from the query
    while position < len(query):
        # Get the length of the next label
        length = query[position]
        # If the length is 0, it indicates the end of the domain name
        if length == 0:
            break
        # Move to the start of the label
        position += 1
        # Extract and decode the label, append it to the domain name
        domain_name += query[position: position + length].decode() + "."
        # Move to the next label
        position += length
    # Return the domain name, excluding the trailing dot
    return domain_name[:-1]


if __name__ == "__main__":
    # Start the proxy listening on port 53 and forwarding to 1.1.1.1:853 (Cloudflare's DNS-over-TLS endpoint)
    start_proxy(("", 53), ("1.1.1.1", 853))
