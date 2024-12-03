# gui.py
import tkinter as tk
from tkinter import scrolledtext

class ChatGUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Encrypted Chat")
        self.chat_area = scrolledtext.ScrolledText(self.root)
        self.msg_entry = tk.Entry(self.root)
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)