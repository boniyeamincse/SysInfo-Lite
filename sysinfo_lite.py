#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import time
import threading
import socket
import platform

class SystemMonitor:
    """Model component: Handles data fetching."""
    
    @staticmethod
    def get_command_output(command):
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return output.decode("utf-8").strip()
        except Exception:
            return "N/A"

    def get_os_info(self):
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            return line.split("=")[1].strip().strip('"')
            return self.get_command_output("lsb_release -ds")
        except:
            return platform.system()

    def get_kernel_info(self):
        return platform.release()

    def get_cpu_usage(self):
        try:
            # top -bn1 | grep "Cpu(s)"
            top_out = self.get_command_output("top -bn1 | grep 'Cpu(s)'")
            if "Cpu(s)" in top_out:
                # %Cpu(s):  3.5 us,  1.5 sy,  0.0 ni, 94.9 id...
                parts = top_out.split(",")
                for part in parts:
                    if "id" in part:
                         idle_str = part.strip().split()[0]
                         return 100.0 - float(idle_str)
            return 0.0
        except:
            return 0.0

    def get_ram_info(self):
        # Returns (used_str, total_str, percent)
        try:
            # free -m
            out = self.get_command_output("free -m | grep Mem")
            parts = out.split()
            # Mem: total used free shared buff/cache available
            total = int(parts[1])
            used = int(parts[2])
            percent = (used / total) * 100 if total > 0 else 0
            return f"{used}MB", f"{total}MB", percent
        except:
            return "N/A", "N/A", 0.0

    def get_disk_info(self):
        # Returns (used, total, percent)
        try:
            out = self.get_command_output("df -h / | awk 'NR==2 {print $3, $2, $5}'")
            parts = out.split() # 10G 100G 10%
            used = parts[0]
            total = parts[1]
            percent_str = parts[2].strip('%')
            return used, total, float(percent_str)
        except:
             return "N/A", "N/A", 0.0

    def get_uptime(self):
        return self.get_command_output("uptime -p").replace("up ", "")

    def get_network_info(self):
        try:
            hostname = socket.gethostname()
            # Get local IP - trick to get actual interface IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # doesn't even have to be reachable
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
            except Exception:
                ip = '127.0.0.1'
            finally:
                s.close()
            return hostname, ip
        except:
            return "Unknown", "N/A"


class SysInfoApp:
    """Controller/View component: Handles UI and interaction."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SysInfo Lite")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # Set Icon
        self.set_icon()

        self.monitor = SystemMonitor()
        self.auto_refresh_job = None
        self.is_auto_refreshing = False

        # UI Setup
        self.setup_styles()
        self.create_widgets()
        
        # Initial Data Load
        self.refresh_data()

    def set_icon(self):
        try:
            icon_paths = ["resources/sysinfo_lite.png", "/usr/share/icons/sysinfo-lite.png"]
            for path in icon_paths:
                if os.path.exists(path):
                    icon = tk.PhotoImage(file=path)
                    self.root.iconphoto(True, icon)
                    break
        except Exception as e:
            print(f"Icon load error: {e}")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        bg_color = "#f0f0f0"
        self.root.configure(bg=bg_color)
        
        # Frame styles
        style.configure("Card.TFrame", background="white", relief="raised", borderwidth=1)
        style.configure("TFrame", background=bg_color)
        style.configure("Row.TFrame", background="white") # New style for rows
        style.configure("TLabel", background="white", font=("Helvetica", 10))
        style.configure("Header.TLabel", background=bg_color, font=("Helvetica", 16, "bold"), foreground="#333")
        style.configure("SubHeader.TLabel", background="white", font=("Helvetica", 11, "bold"), foreground="#555")
        
        # Button styles
        style.configure("TButton", font=("Helvetica", 10), padding=6)

    def create_widgets(self):
        main_container = ttk.Frame(self.root, padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_lbl = ttk.Label(main_container, text="System Information", style="Header.TLabel", background="#f0f0f0")
        title_lbl.pack(pady=(0, 15))

        # Content Area (Card View)
        self.content_frame = ttk.Frame(main_container, style="Card.TFrame", padding="15")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # OS & Kernel
        self.lbl_os = self.create_info_row(self.content_frame, "OS:")
        self.lbl_kernel = self.create_info_row(self.content_frame, "Kernel:")
        self.lbl_uptime = self.create_info_row(self.content_frame, "Uptime:")
        
        ttk.Separator(self.content_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Hardware Stats (with Progress Bars)
        self.lbl_cpu, self.prog_cpu = self.create_progress_row(self.content_frame, "CPU Load:")
        self.lbl_ram, self.prog_ram = self.create_progress_row(self.content_frame, "RAM Usage:")
        self.lbl_disk, self.prog_disk = self.create_progress_row(self.content_frame, "Disk (/) :")

        ttk.Separator(self.content_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Network
        self.lbl_hostname = self.create_info_row(self.content_frame, "Hostname:")
        self.lbl_ip = self.create_info_row(self.content_frame, "IP Address:")

        # Status Bar / Actions
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=tk.X, pady=(15, 0))

        self.btn_refresh = ttk.Button(action_frame, text="Refresh", command=self.refresh_data)
        self.btn_refresh.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_auto = ttk.Button(action_frame, text="Auto: OFF", command=self.toggle_auto_refresh)
        self.btn_auto.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.btn_export = ttk.Button(action_frame, text="Export Info", command=self.export_data)
        self.btn_export.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready")
        lbl_status = ttk.Label(main_container, textvariable=self.status_var, background="#f0f0f0", font=("Helvetica", 8), foreground="#777")
        lbl_status.pack(side=tk.BOTTOM, anchor="e", pady=(5,0))

    def create_info_row(self, parent, label):
        frame = ttk.Frame(parent, style="Row.TFrame")
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label, width=12, style="SubHeader.TLabel").pack(side=tk.LEFT)
        val_lbl = ttk.Label(frame, text="--", style="TLabel")
        val_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return val_lbl

    def create_progress_row(self, parent, label):
        frame = ttk.Frame(parent, style="Row.TFrame")
        frame.pack(fill=tk.X, pady=4)
        
        top_frame = ttk.Frame(frame, style="Row.TFrame")
        top_frame.pack(fill=tk.X)
        ttk.Label(top_frame, text=label, width=12, style="SubHeader.TLabel").pack(side=tk.LEFT)
        val_lbl = ttk.Label(top_frame, text="--%", style="TLabel")
        val_lbl.pack(side=tk.RIGHT)
        
        prog = ttk.Progressbar(frame, orient="horizontal", length=100, mode="determinate")
        prog.pack(fill=tk.X, pady=(2, 0))
        return val_lbl, prog

    def toggle_auto_refresh(self):
        if self.is_auto_refreshing:
            self.is_auto_refreshing = False
            self.btn_auto.config(text="Auto: OFF")
            if self.auto_refresh_job:
                self.root.after_cancel(self.auto_refresh_job)
        else:
            self.is_auto_refreshing = True
            self.btn_auto.config(text="Auto: ON")
            self.refresh_data()

    def refresh_data(self):
        self.status_var.set("Refreshing...")
        self.btn_refresh.state(['disabled'])
        
        # Thread process to avoid UI freeze
        threading.Thread(target=self._fetch_data_thread, daemon=True).start()

    def _fetch_data_thread(self):
        # Gather data
        data = {}
        data['os'] = self.monitor.get_os_info()
        data['kernel'] = self.monitor.get_kernel_info()
        data['uptime'] = self.monitor.get_uptime()
        
        data['cpu_usage'] = self.monitor.get_cpu_usage()
        
        data['ram_used'], data['ram_total'], data['ram_pct'] = self.monitor.get_ram_info()
        data['disk_used'], data['disk_total'], data['disk_pct'] = self.monitor.get_disk_info()
        
        data['hostname'], data['ip'] = self.monitor.get_network_info()
        
        # Update UI in main thread
        self.root.after(0, self._update_ui, data)

    def _update_ui(self, data):
        # Text Updates
        self.lbl_os.config(text=data['os'])
        self.lbl_kernel.config(text=data['kernel'])
        self.lbl_uptime.config(text=data['uptime'])
        self.lbl_hostname.config(text=data['hostname'])
        self.lbl_ip.config(text=data['ip'])

        # Progress Updates
        self.lbl_cpu.config(text=f"{data['cpu_usage']:.1f}%")
        self.prog_cpu['value'] = data['cpu_usage']

        self.lbl_ram.config(text=f"{data['ram_used']} / {data['ram_total']} ({data['ram_pct']:.1f}%)")
        self.prog_ram['value'] = data['ram_pct']

        self.lbl_disk.config(text=f"{data['disk_used']} / {data['disk_total']} ({data['disk_pct']:.1f}%)")
        self.prog_disk['value'] = data['disk_pct']

        self.status_var.set(f"Last updated: {time.strftime('%H:%M:%S')}")
        self.btn_refresh.state(['!disabled'])

        if self.is_auto_refreshing:
            self.auto_refresh_job = self.root.after(2000, self.refresh_data) # Refresh every 2s

    def export_data(self):
        data = []
        data.append("SysInfo Lite Export")
        data.append("===================")
        data.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        data.append("")
        data.append(f"OS:         {self.lbl_os.cget('text')}")
        data.append(f"Kernel:     {self.lbl_kernel.cget('text')}")
        data.append(f"Uptime:     {self.lbl_uptime.cget('text')}")
        data.append(f"Hostname:   {self.lbl_hostname.cget('text')}")
        data.append(f"IP Address: {self.lbl_ip.cget('text')}")
        data.append("")
        data.append(f"CPU Load:   {self.lbl_cpu.cget('text')}")
        data.append(f"RAM Usage:  {self.lbl_ram.cget('text')}")
        data.append(f"Disk Usage: {self.lbl_disk.cget('text')}")

        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if path:
            try:
                with open(path, "w") as f:
                    f.write("\n".join(data))
                messagebox.showinfo("Export", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SysInfoApp(root)
    root.mainloop()
