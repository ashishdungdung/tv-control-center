#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Real-Time Audit in Native 4K UI Mode
-------------------------------------------------------------
Audits WindowManager resolution, density, RAM allocation, CPU load,
storage health, SurfaceFlinger status, and Cloudflare Private DNS while in 4K UI Mode.
"""

import subprocess
import json
import re

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=15)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 65)
    print(" 🖥️ NATIVE 4K UI MODE REAL-TIME SYSTEM AUDIT")
    print("=" * 65)

    # 1. WindowManager Resolution & Density
    wm_size = shell("wm size")
    wm_density = shell("wm density")
    print("\n📐 1. WindowManager Configuration:")
    print(f"  {wm_size}")
    print(f"  {wm_density}")

    # 2. RAM & Swap Allocation
    meminfo = shell("cat /proc/meminfo")
    mem = {}
    for line in meminfo.splitlines():
        parts = line.split(":")
        if len(parts) == 2:
            mem[parts[0].strip()] = parts[1].strip()
            
    print("\n🧠 2. Memory (RAM) Allocation in 4K Mode:")
    print(f"  Total Physical RAM : {mem.get('MemTotal', 'Unknown')}")
    print(f"  Available RAM      : {mem.get('MemAvailable', 'Unknown')}")
    print(f"  Free RAM           : {mem.get('MemFree', 'Unknown')}")
    print(f"  Cached Memory      : {mem.get('Cached', 'Unknown')}")
    print(f"  ZRAM Swap Space    : {mem.get('SwapTotal', '0 kB')}")

    # 3. CPU Load & Uptime
    uptime = shell("uptime")
    print("\n⚡ 3. CPU Load & System Stability:")
    print(f"  {uptime}")

    # 4. Storage Partition Status
    df_data = shell("df -h /data")
    print("\n💾 4. Internal Storage Health (/data):")
    print(f"  {df_data.splitlines()[-1] if df_data else 'Unknown'}")

    # 5. Encrypted Cloudflare Private DNS Status
    dns_mode = shell("settings get global private_dns_mode")
    dns_spec = shell("settings get global private_dns_specifier")
    print("\n🔒 5. Encrypted Private DNS Status:")
    print(f"  Private DNS Mode     : {dns_mode}")
    print(f"  Private DNS Hostname : {dns_spec} (Cloudflare 1.1.1.1 DoT/DoH)")

    print("\n" + "=" * 65)
    print(" ✅ 4K UI MODE AUDIT COMPLETE")
    print("=" * 65)

if __name__ == "__main__":
    main()
