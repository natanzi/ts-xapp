#handover_client.py
import socket
import json

# Replace with the appropriate host and port
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 12345        # The port used by the server

def send_handover_command(server_address, ue_id, target_cell):
    """ Sends a handover command to the handover server. """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(server_address)
            
            # Construct the handover command as a dictionary
            handover_command = {
                'command': 'handover',
                'ue_id': ue_id,
                'target_cell': target_cell
            }
            
            # Convert the command to a JSON string
            handover_command_str = json.dumps(handover_command)
            
            # Send the command
            s.sendall(handover_command_str.encode('utf-8'))
            
            # Wait for a response
            response = s.recv(1024)
            print('Received:', response.decode('utf-8'))

        except socket.error as e:
            print(f"Socket error occurred: {e}")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Attempt to close the socket in case of any failure
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass  # Ignore errors in shutdown
            s.close()

# Example usage
if __name__ == "__main__":
    # Replace 'ue_id' and 'target_cell' with appropriate values
    send_handover_command((HOST, PORT), ue_id='1234', target_cell='5678')

