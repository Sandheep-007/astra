import tkinter as tk
from tkinter import messagebox
import threading
import time
from listener import Listener

class AstraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Astra AI")
        self.root.geometry("320x180")
        self.root.resizable(False, False)

        self.listener = Listener()
        self.listener_thread = None
        self.is_listening = False

        # Status label
        self.status_label = tk.Label(root, text="🔴 Astra is Offline", font=("Arial", 12), fg="white", bg="#cc4c4c")
        self.status_label.pack(fill=tk.X)

        # Loading label (initially hidden)
        self.loading_label = tk.Label(root, text="", font=("Arial", 10), fg="gray")
        self.loading_label.pack()

        # Start button
        self.start_button = tk.Button(root, text="Start", font=("Arial", 14), command=self.start_listening)
        self.start_button.pack(pady=20)

        # Stop button
        self.stop_button = tk.Button(root, text="Stop", font=("Arial", 14), command=self.stop_listening)
        self.stop_button.pack(pady=10)

        self.set_offline_style()

    def set_online_style(self):
        self.root.configure(bg="#d4f4d2")  # Light green background
        self.status_label.config(text="🟢 Astra is Online", bg="#4caf50", fg="white")
        self.start_button.config(bg="white", fg="black")
        self.stop_button.config(bg="#f44336", fg="white")
        self.loading_label.config(text="")  # Clear loading

    def set_offline_style(self):
        self.root.configure(bg="#f4d2d2")  # Light red background
        self.status_label.config(text="🔴 Astra is Offline", bg="#cc4c4c", fg="white")
        self.start_button.config(bg="#4caf50", fg="white")
        self.stop_button.config(bg="white", fg="black")
        self.loading_label.config(text="")

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.loading_label.config(text="⏳ Loading... please wait")
            self.root.update_idletasks()

            # Start Astra immediately in background
            self.listener_thread = threading.Thread(target=self.listener.run)
            self.listener_thread.daemon = True
            self.listener_thread.start()

            # Delay UI update to simulate loading
            def update_gui_after_delay():
                time.sleep(5)
                self.set_online_style()

            threading.Thread(target=update_gui_after_delay, daemon=True).start()
        else:
            messagebox.showinfo("Astra", "Already running.")

    def stop_listening(self):
        if self.is_listening:
            self.listener.stop_listening()
            self.is_listening = False
            self.set_offline_style()
        else:
            messagebox.showinfo("Astra", "Astra is not running.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AstraGUI(root)
    root.mainloop()
