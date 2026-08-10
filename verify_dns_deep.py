#!/usr/bin/env python3
"""
Deep Android 10 Netd & Private DNS Validation Script
Inspects active Private DNS engine sockets and resolver IP addresses directly from Android 10 dumpsys.
"""

import subprocess
import re

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=20)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 65)
    print(" 🔬 ANDROID 10 NETD PRIVATE DNS ENGINE AUDIT")
    print("=" * 65)

    mode = shell("settings get global private_dns_mode")
    spec = shell("settings get global private_dns_specifier")

    print(f" Private DNS Mode Setting : {mode}")
    print(f" Target Hostname          : {spec}")

    # Inspect Dumpsys Connectivity for Private DNS validation status
    conn_out = shell("dumpsys connectivity")
    print("\n🌐 Active Network Link Properties & DNS Resolvers:")
    for line in conn_out.splitlines():
        if any(keyword in line for keyword in ["PrivateDns", "one.one.one.one", "DnsAddresses", "LinkProperties", "Validated"]):
            print(f"  {line.strip()}")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    main()
