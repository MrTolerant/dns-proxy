import socket  # For network connections.
import ssl  # For encrypted connections over SSL/TLS.
import struct  # To work with binary data (pack/unpack DNS queries).
import logging  # For logging messages.
import threading  # To handle each client connection in a separate thread.

# Setup logging.
logger = logging.getLogger("DNSProxy")
logging.basicConfig(level=logging.INFO)  # Set log level to INFO.


def start_proxy(listen_addr, tls_dns_server_addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket.
    sock.bind(listen_addr)  # Bind socket to listening address.
    sock.listen(2)  # Listen for incoming connections, with max 2 in the queue. (Prevent overloading)
    logger.info(f"Listening for DNS on {listen_addr}")

    while True:  # Infinite loop to accept client connections.
        client, _ = sock.accept()  # Accept a new connection.
        # Create and start a new thread for handling the client.
        client_thread = threading.Thread(
            target=handle_client, args=(client, tls_dns_server_addr)
        )
        client_thread.start()


def handle_client(client_conn, tls_dns_server_addr):
    with client_conn:  # Ensure the socket is closed after handling the client.
        logger.info("Handling client connection")
        try:
            client_conn.settimeout(10)  # Set a 10-second timeout for operations.
            length = client_conn.recv(2)  # Receive the first 2 bytes (query length).
            if not length:
                logger.info("Connection closed by client.")
                return  # Exit if no data received.
            length = struct.unpack("!H", length)[0]  # Unpack length to integer.
            query = client_conn.recv(length)  # Receive the DNS query of 'length' bytes.
            if not query:
                logger.info("Incomplete query received; closing connection.")
                return  # Exit if the query is incomplete.

            domain_name = parse_domain_name(query)  # Extract domain name from query.
            logger.info(f"Received DNS query for {domain_name}")

            # Setup an SSL/TLS context for secure connection.
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            # Connect to TLS DNS server and wrap the connection with SSL/TLS.
            with socket.create_connection(tls_dns_server_addr, timeout=10) as raw_sock:
                with context.wrap_socket(
                    raw_sock, server_hostname=tls_dns_server_addr[0]
                ) as tls_conn:
                    tls_conn.send(struct.pack("!H", length) + query)  # Send query.
                    response = tls_conn.recv(4096)  # Receive the response.
                    if response:
                        client_conn.send(response)  # Send response back to client.
                        logger.info(f"Response sent back to client for {domain_name}")
        except socket.timeout:
            logger.warning("Operation timed out during DNS query handling.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            client_conn.close()  # Ensure the client connection is closed.


def parse_domain_name(query):
    position = 12  # DNS header is 12 bytes, so start reading from byte 12.
    domain_name = ""  # Initialize empty domain name.
    # Loop to extract domain name from the query.
    while position < len(query):
        length = query[position]  # Get the length of the next segment.
        if length == 0:  # If length is 0, it's the end of the domain name.
            break
        position += 1  # Move to the start of the segment.
        # Decode segment and append it to the domain name.
        domain_name += query[position: position + length].decode() + "."
        position += length  # Move to the next segment.
    logger.info(f"Parsed domain name: {domain_name[:-1]}")
    return domain_name[:-1]  # Return domain name, excluding the trailing dot.


if __name__ == "__main__":
    start_proxy(("", 53), ("1.1.1.1", 853))  # Start the proxy.
