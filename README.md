# SysInfo Lite

SysInfo Lite is a lightweight, GUI-based Linux application that displays essential system information.

## Features

- **CPU/RAM/Disk**: Visual progress bars for usage stats.
- **Network Info**: Hostname and Local IP address.
- **OS Info**: Operating System and Kernel version.
- **Uptime**: System uptime.
- **Auto-Refresh**: Toggle automatic data updates (every 2s).
- **Export**: Save the current system snapshot to a text file.

## Requirements

- Python 3
- `python3-tk` (Tkinter)
- `procps` (for `top`, `uptime`, `free`)

## Installation

### Manual Run

1.  Ensure you have Python 3 and Tkinter installed:
    ```bash
    sudo apt-get update
    sudo apt-get install python3 python3-tk
    ```

2.  Run the application:
    ```bash
    python3 sysinfo_lite.py
    ```

### Building a .deb Package

1.  Make the script executable:
    ```bash
    chmod +x sysinfo_lite.py
    ```

2.  Copy the script to the build directory:
    ```bash
    cp sysinfo_lite.py debian/usr/bin/sysinfo-lite
    chmod +x debian/usr/bin/sysinfo-lite
    ```

3.  Build the package:
    ```bash
    dpkg-deb --build debian sysinfo-lite_1.0_all.deb
    ```

4.  Install the package:
    ```bash
    sudo dpkg -i sysinfo-lite_1.0_all.deb
    sudo apt-get install -f  # To fix any missing dependencies
    ```

## Uninstall

```bash
sudo apt-get remove sysinfo-lite
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
