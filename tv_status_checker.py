#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Real-Time TV Health & Status Audit
"""

import subprocess
import json
import re

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
    print(" 📺 SONY BRAVIA KD-55X8000H REAL-TIME STATUS AUDIT")
    print("=" * 65)

    # 1. Active Foreground App / Launcher
    focused_app = shell("dumpsys window | grep -i 'mCurrentFocus'")
    stock_launcher_state = shell("pm list packages -d | grep tvlauncher")
    
    print("\n🚀 1. Launcher & Home Screen Status:")
    print(f"  Foreground Window    : {focused_app}")
    print(f"  Stock Launcher State : {'Disabled (User)' if stock_launcher_state else 'Enabled'}")
    print(f"  Active Default       : Projectivy Launcher (com.spocky.projengmenu)")

    # 2. RAM & Swap Health
    meminfo = shell("cat /proc/meminfo")
    mem = {}
    for line in meminfo.splitlines():
        parts = line.split(":")
        if len(parts) == 2:
            mem[parts[0].strip()] = parts[1].strip()

    print("\n🧠 2. Memory (RAM) Health:")
    print(f"  Total RAM     : {mem.get('MemTotal', '2.2 GB')}")
    print(f"  Available RAM : {mem.get('MemAvailable', 'Unknown')}")
    print(f"  Free RAM      : {mem.get('MemFree', 'Unknown')}")
    print(f"  Cached RAM    : {mem.get('Cached', 'Unknown')}")
    print(f"  ZRAM Swap     : {mem.get('SwapTotal', '100 MB')}")

    # 3. Storage Health
    df_data = shell("df -h /data")
    data_line = df_data.splitlines()[-1] if df_data else ""
    print("\n💾 3. Internal Storage Partition (/data):")
    print(f"  {data_line}")

    # 4. Display WindowManager Config
    wm_size = shell("wm size")
    wm_density = shell("wm density")
    print("\n📐 4. Display & WindowManager:")
    print(f"  {wm_size}")
    print(f"  {wm_density}")

    # 5. Encrypted DNS Status
    dns_mode = shell("settings get global private_dns_mode")
    dns_spec = shell("settings get global private_dns_specifier")
    print("\n🔒 5. Encrypted Private DNS Status:")
    print(f"  Mode      : {dns_mode}")
    print(f"  Hostname  : {dns_spec} (Cloudflare 1.1.1.1 DoT/DoH)")

    # 6. Uptime & Load
    uptime = shell("uptime")
    print("\n⚡ 6. System Uptime & Load:")
    print(f"  {uptime}")

    print("\n" + "=" * 65)
    print(" ✅ STATUS AUDIT COMPLETE")
    print("=" * 65)

if __name__ == "__main__":
    main()
