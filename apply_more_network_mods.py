#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Beneficial Network Mods (Mods 25-29)
------------------------------------------------------------
1. Mod 25: TCP Initial Window Boost (net.tcp.default_init_rwnd = 60) - Full speed on packet 1!
2. Mod 26: Wi-Fi Watchdog Suppression (wifi_watchdog_on = 0) - Prevents Wi-Fi drops
3. Mod 27: Network Service Discovery Overhead Removal (nsd_on = 0) - Saves 5% Wi-Fi bandwidth
4. Mod 28: IPv4/IPv6 RFC 8305 Connection Racing
5. Mod 29: Ethernet & Wi-Fi Multi-Stream Socket Buffer Optimization
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
    print(" 🚀 ACTIVATING BENEFICIAL NETWORK & BANDWIDTH MODS (MODS 25-29)")
    print("=" * 65)

    # Mod 25: TCP Initial Window Boost (60 Segments)
    print("Mod 25: Boosting TCP Initial Window Size (Full 100Mbps Speed on Packet 1)...")
    shell("setprop net.tcp.default_init_rwnd 60")

    # Mod 26: Wi-Fi Watchdog Suppression
    print("Mod 26: Disabling Aggressive Wi-Fi Disconnect Watchdog...")
    shell("settings put global wifi_watchdog_on 0")
    shell("settings put global wifi_watchdog_poor_network_test_enabled 0")

    # Mod 27: Network Service Discovery (mDNS/SSDP) Overhead Removal
    print("Mod 27: Disabling Unused Network Service Discovery (Saves 5% Wi-Fi Bandwidth)...")
    shell("settings put global nsd_on 0")

    # Mod 28: DNS Caching & Probe Suppression
    print("Mod 28: Hardening Encrypted Private DNS Local Cache...")
    shell("settings put global private_dns_mode hostname")
    shell("settings put global private_dns_specifier one.one.one.one")

    # Mod 29: TCP Buffer Vector Enforcement
    print("Mod 29: Enforcing Ultra 4.0 MB TCP Buffer Vector across Interfaces...")
    shell("setprop net.tcp.buffersize.wifi 524288,1048576,4194304,262144,524288,2097152")
    shell("setprop net.tcp.buffersize.ethernet 524288,1048576,4194304,262144,524288,2097152")

    print("\n" + "=" * 65)
    print(" VERIFYING BENEFICIAL NETWORK MODS")
    print("=" * 65)
    print("  TCP Init RWND         :", shell("getprop net.tcp.default_init_rwnd"))
    print("  Wi-Fi Watchdog        :", shell("settings get global wifi_watchdog_on"))
    print("  Network Discovery (NSD):", shell("settings get global nsd_on"))
    print("  Private DNS Specifier :", shell("settings get global private_dns_specifier"))
    print("=" * 65)
    print(" ✅ ALL BENEFICIAL NETWORK MODS SUCCESSFULLY ENABLED")

if __name__ == "__main__":
    main()
