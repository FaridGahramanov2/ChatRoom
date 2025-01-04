import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from encryption import ClientEncryption


class ChatClient:
    def __init__(self):
        # Initialize socket and encryption
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encryption = ClientEncryption()
        self.socket.connect(('127.0.0.1', 55557))

        # Get nickname and setup GUI
        self.nickname = input("Choose your nickname: ")
        self.setup_gui()

        self.running = True
        self.start()

    def setup_gui(self):
        # Setup tkinter GUI
        self.window = tk.Tk()
        self.window.title(f"Chat - {self.nickname}")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Chat frame
        self.chat_frame = tk.Frame(self.window)
        self.chat_frame.pack(expand=True, fill='both')

        self.text_area = scrolledtext.ScrolledText(self.chat_frame)
        self.text_area.pack(expand=True, fill='both')

        self.input_area = tk.Entry(self.window)
        self.input_area.pack(fill='x', padx=10, pady=5)
        self.input_area.bind('<Return>', lambda e: self.send_message())

        self.send_button = tk.Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

    def receive(self):
        # Receive messages from the server
        while self.running:
            try:
                message = self.socket.recv(1024)
                cmd = message.decode('ascii')

                if cmd == 'KEY':
                    # Send public key to server
                    public_key = self.encryption.get_public_key()
                    print(f"Sending Public Key:\n{public_key.decode('ascii')}")
                    self.socket.send(public_key)
                elif cmd == 'NICK':
                    # Send nickname to server
                    self.socket.send(self.nickname.encode('ascii'))
                elif cmd.startswith('PEER_INFO'):
                    # Handle peer-to-peer communication
                    _, peer_ip, peer_port = cmd.split(':')
                    peer_port = int(peer_port)
                    print(f"Received peer info: {peer_ip}:{peer_port}")
                    self.connect_to_peer(peer_ip, peer_port)
                else:
                    try:
                        # Try to decrypt the message
                        decrypted = self.encryption.decrypt(message)
                        self.text_area.insert(tk.END, f"{decrypted}\n")
                    except Exception as e:
                        print(f"Decryption failed: {e}")
                        self.text_area.insert(tk.END, f"{message.decode('ascii')}\n")
                self.text_area.see(tk.END)
            except Exception as e:
                # Handle disconnection or other errors
                if self.running:
                    print(f"Error: {e}")
                break

    def send_message(self):
        # Send message to the server
        message = self.input_area.get().strip()
        if message:
            try:
                self.socket.send(f"{self.nickname}: {message}".encode('ascii'))
                self.text_area.insert(tk.END, f"You: {message}\n")
                self.input_area.delete(0, tk.END)
            except Exception as e:
                print(f"Error sending message: {e}")
                self.on_closing()

    def on_closing(self):
        # Handle client closure
        self.running = False
        self.socket.close()
        self.window.destroy()

    def start(self):
        # Start the receiving thread and the GUI
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        self.window.mainloop()

    def connect_to_peer(self, peer_ip, peer_port):
        """Attempt to establish a peer-to-peer UDP connection."""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', 0))  # Bind to any available port
        udp_socket.settimeout(5)

        try:
            # Send an initial packet to punch a hole in NAT
            print(f"Sending UDP packet to {peer_ip}:{peer_port}")
            udp_socket.sendto(self.nickname.encode('ascii'), (peer_ip, peer_port))

            # Wait for a response
            response, addr = udp_socket.recvfrom(1024)
            print(f"Received response from {addr}: {response.decode('ascii')}")
            return udp_socket
        except socket.timeout:
            print("UDP connection attempt timed out.")
            return None

if __name__ == "__main__":
    client = ChatClient()