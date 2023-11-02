#handover_client.py
import socket
import sys
import time

# Replace with the server's IP address and port
HOST = '192.168.1.10'  # The server's IP address
PORT = 12345           # The port used by the server

def create_connection(host, port):
    """Attempts to create a socket connection to the server."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        print(f"Successfully connected to the server {host} on port {port}")
        return s
    except socket.error as err:
        print(f"Connection failed with error: {err}")
        return None

def send_handover_command(sock, ue_id, target_enb_id):
    """Sends a handover command to the server."""
    try:
        # Construct the handover command
        message = f"Handover command for UE: {ue_id} to target eNB: {target_enb_id}\n"
        sock.sendall(message.encode())

        # Wait for a response from the server
        response = sock.recv(1024)
        print("Server response:", response.decode())

    except socket.error as err:
        print(f"Send/receive failed with error: {err}")

def main():
    sock = create_connection(HOST, PORT)
    if not sock:
        print("Failed to connect to the server. Exiting.")
        sys.exit(1)

    try:
        while True:
            # Example UE ID and target eNB ID for handover
            ue_id = '123'
            target_enb_id = '456'
            
            send_handover_command(sock, ue_id, target_enb_id)

            # Example delay between handover commands
            time.sleep(5)

    except KeyboardInterrupt:
        print("Interrupted by the user.")

    finally:
        if sock:
            sock.close()

if __name__ == '__main__':
    main()
