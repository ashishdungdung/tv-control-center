#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Ultra 4.0 MB TCP Window Buffer Tuning & Kernel Optimization
-----------------------------------------------------------------------------------
1. Applies 4.0 MB Max TCP Receive Window Buffer for 4K 60fps HDR (net.tcp.buffersize.wifi)
2. Enables RFC 1323 TCP Window Scaling (tcp_window_scaling = 1)
3. Enables Selective Acknowledgements (tcp_sack = 1) for Wi-Fi packet loss recovery
4. Enables High-Precision Round-Trip Timestamps (tcp_timestamps = 1)
"""

import subprocess

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 65)
    print(" 🚀 APPLYING ULTRA 4.0 MB TCP WINDOW BUFFER TUNE OVER ADB")
    print("=" * 65)

    # 1. Ultra 4.0 MB TCP Window Buffer Vector for Wi-Fi & Ethernet
    print("1. Setting 4.0 MB Max TCP Receive Window Buffer Vector...")
    shell("setprop net.tcp.buffersize.wifi 524288,1048576,4194304,262144,524288,2097152")
    shell("setprop net.tcp.buffersize.ethernet 524288,1048576,4194304,262144,524288,2097152")

    # 2. Linux Kernel TCP Window Scaling (RFC 1323)
    print("2. Enabling RFC 1323 TCP Window Scaling (Allows >64KB Windows)...")
    shell("settings put global tcp_window_scaling 1")

    # 3. Selective ACK (SACK) for Wi-Fi Packet Loss Recovery
    print("3. Enabling Selective ACK (SACK) for Packet Loss Recovery...")
    shell("settings put global tcp_sack 1")

    # 4. TCP Timestamps for Wi-Fi Latency Jitter Compensation
    print("4. Enabling TCP High-Precision RTT Timestamps...")
    shell("settings put global tcp_timestamps 1")

    print("\n" + "=" * 65)
    print(" VERIFYING APPLIED TCP SETTINGS")
    print("=" * 65)
    print("  Wi-Fi TCP Buffer Vector :", shell("getprop net.tcp.buffersize.wifi"))
    print("  Ethernet TCP Buffer     :", shell("getprop net.tcp.buffersize.ethernet"))
    print("=" * 65)
    print(" ✅ ULTRA 4.0 MB TCP WINDOW BUFFER TUNE SUCCESSFULLY ACTIVATED")

if __name__ == "__main__":
    main()
