# client/client.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from encryption import ClientEncryption

class ChatClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encryption = ClientEncryption()
        self.socket.connect(('127.0.0.1', 55557))
        self.nickname = input("Choose your nickname: ")
        self.setup_gui()
        self.running = True
        self.start()

    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title(f"Chat - {self.nickname}")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
        while self.running:
            try:
                message = self.socket.recv(1024)
                cmd = message.decode('ascii')
                
                if cmd == 'KEY':
                    self.socket.send(self.encryption.get_public_key())
                elif cmd == 'NICK':
                    self.socket.send(self.nickname.encode('ascii'))
                else:
                    try:
                        decrypted = self.encryption.decrypt(message)
                        self.text_area.insert(tk.END, f"{decrypted}\n")
                    except:
                        self.text_area.insert(tk.END, f"{message.decode('ascii')}\n")
                self.text_area.see(tk.END)
            except Exception as e:
                if self.running:
                    print(f"Error: {e}")
                break

    def send_message(self):
        message = self.input_area.get().strip()
        if message:
            try:
                self.socket.send(f"{self.nickname}: {message}".encode('ascii'))
                self.text_area.insert(tk.END, f"You: {message}\n")
                self.input_area.delete(0, tk.END)
            except:
                self.on_closing()

    def on_closing(self):
        self.running = False
        self.socket.close()
        self.window.destroy()

    def start(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        self.window.mainloop()

if __name__ == "__main__":
    client = ChatClient()