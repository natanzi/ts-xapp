# handover_client.py
import socket
import sys
import time

# Replace with the server's IP address and port
HOST = '127.0.0.1'  # The server's IP address
PORT = 54321        # The port used by the server

def create_connection(host, port, retries=5, delay=2):
    """Attempts to create a socket connection to the server, with retries."""
    attempt = 0
    while attempt < retries:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            print(f"Successfully connected to the server {host} on port {port}")
            return s
        except socket.error as err:
            print(f"Connection failed with error: {err}. Retrying in {delay} seconds...")
            time.sleep(delay)
            attempt += 1
    print("Maximum retries reached. Failed to connect to the server.")
    return None

def send_handover_command(sock, ue_id, target_enb_id):
    try:
        # Construct the handover command as a JSON formatted string
        command = {
            "message_id": "some_unique_id",  # You need to generate a unique ID for each message
            "command": "handover",
            "parameters": {
                "ue_id": ue_id,
                "target_enb_id": target_enb_id
            }
        }
        message = json.dumps(command) + "\n"
        sock.sendall(message.encode())

        # Wait for a response from the server
        response = sock.recv(1024)
        print("Server response:", response.decode())

    except socket.error as err:
        print(f"Send/receive failed with error: {err}.")
        return False
    except ConnectionResetError:
        print("Connection was closed by the server.")
        return False
    return True

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
            
            if not send_handover_command(sock, ue_id, target_enb_id):
                print("Attempting to reconnect to the server...")
                sock.close()  # Close the previous socket before creating a new one
                sock = create_connection(HOST, PORT)
                if not sock:
                    print("Reconnection failed. Exiting.")
                    break

            # Example delay between handover commands
            time.sleep(5)

    except KeyboardInterrupt:
        print("Interrupted by the user.")
    finally:
        if sock:
            sock.close()  # Ensure the socket is closed on exit

if __name__ == '__main__':
    main()
