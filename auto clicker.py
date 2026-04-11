import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode

class AutoClicker:
    def __init__(self):
        self.mouse = Controller()
        self.running = False
        self.program_running = True

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

class ClickerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Auto Clicker")
        self.geometry("300x450")
        self.clicker = AutoClicker()
        
        # Hotkey setting (F8)
        self.start_stop_key = KeyCode(char='s') # Change to 's' or Key.f8
        
        self.setup_ui()
        
        # Start background threads
        self.click_thread = threading.Thread(target=self.click_worker)
        self.click_thread.daemon = True
        self.click_thread.start()
        
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def setup_ui(self):
        # Interval Settings
        ttk.Label(self, text="Click Interval", font=('Arial', 10, 'bold')).pack(pady=10)
        
        frame_time = ttk.Frame(self)
        frame_time.pack()
        
        self.min_var = tk.IntVar(value=0)
        self.sec_var = tk.IntVar(value=0)
        self.ms_var = tk.IntVar(value=100)

        ttk.Label(frame_time, text="Min").grid(row=0, column=0)
        ttk.Entry(frame_time, textvariable=self.min_var, width=5).grid(row=1, column=0, padx=5)
        
        ttk.Label(frame_time, text="Sec").grid(row=0, column=1)
        ttk.Entry(frame_time, textvariable=self.sec_var, width=5).grid(row=1, column=1, padx=5)
        
        ttk.Label(frame_time, text="MS").grid(row=0, column=2)
        ttk.Entry(frame_time, textvariable=self.ms_var, width=5).grid(row=1, column=2, padx=5)

        # Click Options
        ttk.Label(self, text="Click Options", font=('Arial', 10, 'bold')).pack(pady=10)
        
        self.btn_var = tk.StringVar(value="left")
        ttk.Radiobutton(self, text="Left Click", variable=self.btn_var, value="left").pack()
        ttk.Radiobutton(self, text="Right Click", variable=self.btn_var, value="right").pack()
        
        self.type_var = tk.StringVar(value="single")
        ttk.Radiobutton(self, text="Single", variable=self.type_var, value="single").pack()
        ttk.Radiobutton(self, text="Double", variable=self.type_var, value="double").pack()

        # Repeat Options
        ttk.Label(self, text="Repeat", font=('Arial', 10, 'bold')).pack(pady=10)
        self.repeat_inf = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Repeat Infinitely", variable=self.repeat_inf).pack()
        
        self.repeat_count = tk.IntVar(value=10)
        ttk.Entry(self, textvariable=self.repeat_count, width=10).pack()

        # Controls
        self.status_label = ttk.Label(self, text="Status: Stopped", foreground="red")
        self.status_label.pack(pady=20)
        
        ttk.Label(self, text="Hotkey: Press 's' to Start/Stop").pack()

    def on_press(self, key):
        if key == self.start_stop_key:
            if self.clicker.running:
                self.clicker.stop_clicking()
                self.status_label.config(text="Status: Stopped", foreground="red")
            else:
                self.clicker.start_clicking()
                self.status_label.config(text="Status: Running...", foreground="green")

    def click_worker(self):
        count = 0
        while self.clicker.program_running:
            if self.clicker.running:
                # Calculate delay
                delay = (self.min_var.get() * 60) + self.sec_var.get() + (self.ms_var.get() / 1000.0)
                
                # Determine button
                button = Button.left if self.btn_var.get() == "left" else Button.right
                
                # Perform click
                if self.type_var.get() == "single":
                    self.clicker.mouse.click(button, 1)
                else:
                    self.clicker.mouse.click(button, 2)
                
                # Repeat logic
                count += 1
                if not self.repeat_inf.get() and count >= self.repeat_count.get():
                    self.clicker.stop_clicking()
                    self.status_label.config(text="Status: Finished", foreground="blue")
                    count = 0
                
                time.sleep(delay)
            else:
                count = 0
                time.sleep(0.1)

if __name__ == "__main__":
    app = ClickerGUI()
    app.mainloop()