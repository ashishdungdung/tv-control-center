#!/usr/bin/env python3
"""
Sony BRAVIA TV Wireless Remote Button Remapper Daemon
---------------------------------------------------
Monitors Bluetooth (SONY TV VRC 001) & IR (mtkinp_ir_events) button events over ADB:
- Google Play Remote Button -> Launches Official YouTube (com.google.android.youtube.tv)
- Blue Colored Remote Button -> Triggers Instant RAM Purge (am kill-all & pm trim-caches 4G)
"""

import subprocess
import time

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

def purge_ram_and_cache():
    print("[Remote Remapper] 🧹 BLUE BUTTON PRESSED -> Executing Instant RAM & Cache Purge...")
    try:
        subprocess.run([ADB, "-s", TARGET, "shell", "am kill-all"], capture_output=True, timeout=5)
        subprocess.run([ADB, "-s", TARGET, "shell", "pm trim-caches 4G"], capture_output=True, timeout=5)
        print("[Remote Remapper] ✅ RAM & Cache Purge Completed!")
    except Exception as e:
        print(f"[Remote Remapper] Error purging RAM: {e}")

def launch_youtube():
    print("[Remote Remapper] 🔴 GOOGLE PLAY BUTTON PRESSED -> Launching Official YouTube 4K...")
    try:
        subprocess.run([ADB, "-s", TARGET, "shell", "monkey -p com.google.android.youtube.tv -c android.intent.category.LAUNCHER 1"], capture_output=True, timeout=5)
        print("[Remote Remapper] ✅ YouTube Launched!")
    except Exception as e:
        print(f"[Remote Remapper] Error launching YouTube: {e}")

def monitor_events():
    print("=" * 65)
    print(" 🚀 STARTING SONY BRAVIA REMOTE BUTTON REMAPPER DAEMON")
    print("=" * 65)
    print(" Listening for Sony Remote Keyevents on 192.168.2.122:5555...")
    print("  • Google Play Button ➔ Launch Official 4K YouTube")
    print("  • Blue Colored Button ➔ Instant RAM & Cache Purge")
    print("=" * 65)

    proc = subprocess.Popen(
        [ADB, "-s", TARGET, "shell", "getevent -l"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    last_trigger = 0

    try:
        for line in proc.stdout:
            # Check for Keyevents
            if "KEY_BLUE" in line or "KEY_PROG4" in line or "KEY_OPTION" in line or "00b8" in line:
                now = time.time()
                if now - last_trigger > 1.5:  # Debounce 1.5s
                    last_trigger = now
                    purge_ram_and_cache()
            elif "KEY_BUTTON_3" in line or "KEY_PLAY" in line or "KEY_MOVIES" in line or "0103" in line:
                now = time.time()
                if now - last_trigger > 1.5:
                    last_trigger = now
                    launch_youtube()
    except Exception as e:
        print(f"[Remote Remapper] Error in event loop: {e}")

if __name__ == "__main__":
    monitor_events()
