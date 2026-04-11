import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode, Key

class AutoClicker:
    def __init__(self):
        self.mouse = Controller()
        self.running = False
        self.program_running = True
        # Settings updated only on 'Apply'
        self.delay = 0.1
        self.button_type = Button.left
        self.click_count = 1
        self.inf_repeat = True
        self.limit = 10

    def update_settings(self, delay, btn_str, type_str, inf, limit):
        self.delay = delay
        self.button_type = Button.left if btn_str == "left" else Button.right
        self.click_count = 1 if type_str == "single" else 2
        self.inf_repeat = inf
        self.limit = limit

class ClickerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pro Auto Clicker")
        self.geometry("350x620")
        
        # --- NEW: Always on Top ---
        self.attributes("-topmost", True)
        
        self.clicker = AutoClicker()
        self.current_hotkey = KeyCode(char='s')
        self.is_rebinding = False
        
        # Numeric validation
        self.vcmd = (self.register(self.validate_numeric), '%P')
        
        self.setup_ui()
        
        # Background Threads
        threading.Thread(target=self.click_worker, daemon=True).start()
        Listener(on_press=self.on_press).start()

    def validate_numeric(self, P):
        return P == "" or P.isdigit()

    def setup_ui(self):
        # Hotkey Section
        ttk.Label(self, text="Hotkey Settings", font=('Arial', 10, 'bold')).pack(pady=5)
        self.hotkey_label = ttk.Label(self, text=f"Current Hotkey: {self.format_key(self.current_hotkey)}")
        self.hotkey_label.pack()
        self.rebind_btn = ttk.Button(self, text="Rebind Hotkey", command=self.start_rebind)
        self.rebind_btn.pack(pady=5)

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=10, pady=10)

        # Interval Section
        ttk.Label(self, text="Click Interval", font=('Arial', 10, 'bold')).pack()
        f_time = ttk.Frame(self)
        f_time.pack(pady=5)
        
        self.min_var, self.sec_var, self.ms_var = tk.StringVar(value="0"), tk.StringVar(value="0"), tk.StringVar(value="100")
        
        for i, (txt, var) in enumerate([("Min", self.min_var), ("Sec", self.sec_var), ("MS", self.ms_var)]):
            ttk.Label(f_time, text=txt).grid(row=0, column=i, padx=5)
            ttk.Entry(f_time, textvariable=var, width=7, validate="key", validatecommand=self.vcmd).grid(row=1, column=i, padx=2)

        # Click Options
        ttk.Label(self, text="Click Options", font=('Arial', 10, 'bold')).pack(pady=10)
        self.btn_var = tk.StringVar(value="left")
        ttk.Radiobutton(self, text="Left Click", variable=self.btn_var, value="left").pack()
        ttk.Radiobutton(self, text="Right Click", variable=self.btn_var, value="right").pack()
        
        self.type_var = tk.StringVar(value="single")
        ttk.Radiobutton(self, text="Single", variable=self.type_var, value="single").pack()
        ttk.Radiobutton(self, text="Double", variable=self.type_var, value="double").pack()

        # Repeat Section
        ttk.Label(self, text="Repeat", font=('Arial', 10, 'bold')).pack(pady=5)
        self.repeat_inf = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Repeat Infinitely", variable=self.repeat_inf).pack()
        self.repeat_count = tk.StringVar(value="10")
        ttk.Entry(self, textvariable=self.repeat_count, width=10, validate="key", validatecommand=self.vcmd).pack()

        # Apply Settings
        ttk.Button(self, text="APPLY SETTINGS", command=self.apply_settings).pack(pady=15)

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=10, pady=10)

        # --- NEW: GUI Control Buttons ---
        self.toggle_btn = ttk.Button(self, text="START", command=self.toggle_clicking)
        self.toggle_btn.pack(pady=5, ipadx=20)
        
        self.status_label = ttk.Label(self, text="Status: Stopped", foreground="red", font=('Arial', 11, 'bold'))
        self.status_label.pack(pady=5)

    def format_key(self, key):
        if isinstance(key, KeyCode): return key.char
        return str(key).replace("Key.", "")

    def start_rebind(self):
        self.is_rebinding = True
        self.hotkey_label.config(text="Press any key...")
        self.rebind_btn.config(state="disabled")

    def apply_settings(self):
        try:
            m = int(self.min_var.get() or 0)
            s = int(self.sec_var.get() or 0)
            ms = int(self.ms_var.get() or 0)
            delay = (m * 60) + s + (ms / 1000.0)
            
            if delay <= 0: 
                messagebox.showwarning("Warning", "Delay must be greater than 0ms")
                return

            self.clicker.update_settings(
                delay, 
                self.btn_var.get(), 
                self.type_var.get(), 
                self.repeat_inf.get(), 
                int(self.repeat_count.get() or 1)
            )
            messagebox.showinfo("Success", "Settings Applied!")
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input")

    # Shared logic for Button and Hotkey
    def toggle_clicking(self):
        self.clicker.running = not self.clicker.running
        if self.clicker.running:
            self.status_label.config(text="Status: Running...", foreground="green")
            self.toggle_btn.config(text="STOP")
        else:
            self.status_label.config(text="Status: Stopped", foreground="red")
            self.toggle_btn.config(text="START")

    def on_press(self, key):
        if self.is_rebinding:
            self.current_hotkey = key
            self.is_rebinding = False
            self.hotkey_label.config(text=f"Current Hotkey: {self.format_key(key)}")
            self.rebind_btn.config(state="normal")
            return

        if key == self.current_hotkey:
            self.toggle_clicking()

    def click_worker(self):
        count = 0
        while self.clicker.program_running:
            if self.clicker.running:
                self.clicker.mouse.click(self.clicker.button_type, self.clicker.click_count)
                count += 1
                
                if not self.clicker.inf_repeat and count >= self.clicker.limit:
                    self.clicker.running = False
                    self.status_label.config(text="Status: Finished", foreground="blue")
                    self.toggle_btn.config(text="START")
                
                time.sleep(self.clicker.delay)
            else:
                count = 0
                time.sleep(0.1)

if __name__ == "__main__":
    app = ClickerGUI()
    app.mainloop()