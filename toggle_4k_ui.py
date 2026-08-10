#!/usr/bin/env python3
"""
Sony BRAVIA 4K UI Resolution Switcher
-------------------------------------
Allows forcing native 4K (3840x2160) UI rendering or resetting back to default 1080p.
"""

import sys
import subprocess

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=15)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def set_4k_ui():
    print("🖥️ Forcing Native 4K UI Resolution (3840x2160 @ 640 DPI)...")
    shell("wm size 3840x2160")
    shell("wm density 640")
    print("✅ Applied 3840x2160 UI Resolution.")
    print("Current Size   :", shell("wm size"))
    print("Current Density:", shell("wm density"))

def reset_ui():
    print("🔄 Resetting UI Resolution back to Default 1080p...")
    shell("wm size reset")
    shell("wm density reset")
    print("✅ Reset to Default.")
    print("Current Size   :", shell("wm size"))
    print("Current Density:", shell("wm density"))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "4k":
        set_4k_ui()
    elif len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_ui()
    else:
        print("Usage: python3 toggle_4k_ui.py [4k | reset]")
        print("Current Size   :", shell("wm size"))
        print("Current Density:", shell("wm density"))
