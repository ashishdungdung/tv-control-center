#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Dedicated RAM Cleaner & Memory Optimizer Engine
-------------------------------------------------------------------------
Performs deep non-root RAM purging:
1. Measures initial RAM (Available, Free, Cached, Swap)
2. Kills background cached processes (`am kill-all`)
3. Force stops idling heavy apps (Zoom, TeamViewer, Aptoide, SAI, Analiti, etc.)
4. Trims app caches (`pm trim-caches 4G`)
5. Restricts max hidden background apps (`max_hidden_apps = 4`)
6. Measures reclaimed RAM and displays memory recovery summary
"""

import subprocess
import time
import re

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

IDLE_APPS_TO_KILL = [
    "com.teamviewer.host.market",
    "com.teamviewer.quicksupport.market",
    "us.zoom.videomeetings",
    "cm.aptoidetv.pt",
    "com.aefyr.sai",
    "screnmirroring.com",
    "com.mobisystems.fileman",
    "com.analiti.fastest.android",
    "com.vewd.core.service",
    "com.cryptotvapp",
    "systems.sieber.fsclock",
    "com.earthcam.earthcamtv.android",
    "com.acowboys.oldmovies",
    "com.republicworld.tv",
    "com.aajtak.tv",
    "com.zeenews.tv",
    "dw.com.androidtv.live",
    "com.indiatoday.tv",
]

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=15)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_ram_stats():
    meminfo = shell("cat /proc/meminfo")
    stats = {}
    for line in meminfo.splitlines():
        parts = line.split(":")
        if len(parts) == 2:
            stats[parts[0].strip()] = parts[1].strip()
    return stats

def main():
    print("=" * 65)
    print(" 🚀 SONY BRAVIA DEDICATED RAM CLEANER & MEMORY OPTIMIZER")
    print("=" * 65)

    before = get_ram_stats()
    print("\n📊 BEFORE CLEANING:")
    print(f"  Total RAM     : {before.get('MemTotal', 'Unknown')}")
    print(f"  Available RAM : {before.get('MemAvailable', 'Unknown')}")
    print(f"  Free RAM      : {before.get('MemFree', 'Unknown')}")
    print(f"  Cached Memory : {before.get('Cached', 'Unknown')}")

    # 1. Kill all background processes safe to kill
    print("\n🧹 1. Triggering Android Background Process Cleaner (am kill-all)...")
    shell("am kill-all")

    # 2. Force stop idling background apps
    print("\n⚡ 2. Force-stopping idling background services & third-party apps...")
    stopped_count = 0
    for pkg in IDLE_APPS_TO_KILL:
        res = shell(f"am force-stop {pkg}")
        stopped_count += 1
    print(f"  Stopped {stopped_count} idling background packages.")

    # 3. Trim system & app cache
    print("\n💾 3. Trimming app caches & system pagecache...")
    shell("pm trim-caches 4G")

    # 4. Restrict hidden background process thrashing
    print("\n🧠 4. Enforcing Background Process Limit (Max 4)...")
    shell("settings put global max_hidden_apps 4")

    # Measure RAM after cleaning
    time.sleep(1)
    after = get_ram_stats()

    print("\n" + "=" * 65)
    print(" 🎉 RAM CLEANING COMPLETE!")
    print("=" * 65)
    print(f"  BEFORE Available RAM : {before.get('MemAvailable', 'Unknown')}")
    print(f"  AFTER Available RAM  : {after.get('MemAvailable', 'Unknown')}")
    print(f"  Free Physical RAM    : {after.get('MemFree', 'Unknown')}")
    print(f"  Cached Memory        : {after.get('Cached', 'Unknown')}")
    print("=" * 65)

if __name__ == "__main__":
    main()
