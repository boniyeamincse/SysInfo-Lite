#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import time

class SysInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SysInfo Lite")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        # Style Configuration
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))

        # Main Container
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="System Information", style="Header.TLabel")
        title_label.pack(pady=(0, 15))

        # Information Display Area
        self.info_frame = ttk.Frame(main_frame)
        self.info_frame.pack(fill=tk.BOTH, expand=True)

        # Info Labels (stored in a dict for easy updates)
        self.labels = {}
        self.create_info_row("OS Version", "os_version")
        self.create_info_row("Kernel Version", "kernel_version")
        self.create_info_row("CPU Usage", "cpu_usage")
        self.create_info_row("RAM Usage", "ram_usage")
        self.create_info_row("Disk Usage (/)", "disk_usage")
        self.create_info_row("System Uptime", "uptime")

        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        # Refresh Button
        self.refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.refresh_info)
        self.refresh_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        # Export Button
        self.export_btn = ttk.Button(button_frame, text="Export", command=self.export_info)
        self.export_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # Initial Load
        self.refresh_info()

    def create_info_row(self, label_text, key):
        frame = ttk.Frame(self.info_frame)
        frame.pack(fill=tk.X, pady=2)
        
        lbl_key = ttk.Label(frame, text=f"{label_text}:", width=15, anchor="w")
        lbl_key.pack(side=tk.LEFT)
        
        lbl_val = ttk.Label(frame, text="Loading...", anchor="w")
        lbl_val.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.labels[key] = lbl_val

    def get_command_output(self, command):
        try:
            # Using shell=True for complex pipes, though safer to split commands when possible.
            # For this "lite" app, carefully constructed commands are acceptable.
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return output.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            return "Error"
        except Exception:
            return "Unknown"

    def get_os_info(self):
        try:
            # Try /etc/os-release first for pretty name
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            return line.split("=")[1].strip().strip('"')
            # Fallback
            return self.get_command_output("lsb_release -ds")
        except:
            return "Linux"

    def get_cpu_info(self):
        # Using top in batch mode to get CPU usage
        # This parses the "Cpu(s)" line of top command
        try:
           # Grab the top line containing Cpu(s)
           # top -bn1 | grep "Cpu(s)" -> %Cpu(s):  1.5 us,  0.7 sy,  0.0 ni, 97.7 id, ...
           # We want 100 - id (idle) to get total usage roughly
           top_out = self.get_command_output("top -bn1 | grep 'Cpu(s)'")
           parts = top_out.split(",")
           for part in parts:
               if "id" in part:
                   # Extract idle percentage
                   idle_str = part.strip().split()[0]
                   idle_pct = float(idle_str)
                   return f"{100 - idle_pct:.1f}%"
           return "N/A"
        except:
           # Alternate method: /proc/stat if top fails or parsing hard
           return "N/A"

    def refresh_info(self):
        # OS Version
        self.labels["os_version"].config(text=self.get_os_info())

        # Kernel
        self.labels["kernel_version"].config(text=self.get_command_output("uname -r"))

        # CPU Usage (Load average is easier/more reliable, but prompted for usage. Let's try to get usage)
        self.labels["cpu_usage"].config(text=self.get_cpu_info())
        
        # RAM Usage
        # free -h | grep Mem | awk '{print $3 "/" $2}'
        ram_cmd = "free -h | awk '/^Mem:/ {print $3 \" / \" $2}'"
        self.labels["ram_usage"].config(text=self.get_command_output(ram_cmd))

        # Disk Usage (Root)
        # df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}'
        disk_cmd = "df -h / | awk 'NR==2 {print $3 \" / \" $2 \" (\" $5 \")\"}'"
        self.labels["disk_usage"].config(text=self.get_command_output(disk_cmd))

        # Uptime
        self.labels["uptime"].config(text=self.get_command_output("uptime -p"))

    def export_info(self):
        data = []
        data.append("SysInfo Lite Export")
        data.append("===================")
        data.append(f"Export Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        data.append("")
        data.append(f"OS Version:     {self.labels['os_version'].cget('text')}")
        data.append(f"Kernel Version: {self.labels['kernel_version'].cget('text')}")
        data.append(f"CPU Usage:      {self.labels['cpu_usage'].cget('text')}")
        data.append(f"RAM Usage:      {self.labels['ram_usage'].cget('text')}")
        data.append(f"Disk Usage (/): {self.labels['disk_usage'].cget('text')}")
        data.append(f"System Uptime:  {self.labels['uptime'].cget('text')}")

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save System Info"
        )

        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write("\n".join(data))
                messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data:\n{str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SysInfoApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
