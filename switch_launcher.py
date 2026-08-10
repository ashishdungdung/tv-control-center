#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Launcher Switcher Utility
--------------------------------------------------
Allows launching or setting default home screen between:
1. FLauncher (me.efesser.flauncher)
2. Projectivy Launcher (com.spocky.projengmenu)
3. Stock Google TV Launcher (com.google.android.tvlauncher)
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

def launch_flauncher():
    print("🚀 Launching FLauncher on Sony TV...")
    out = shell("monkey -p me.efesser.flauncher -c android.intent.category.LAUNCHER 1")
    print("✅ FLauncher Opened!")

def launch_projectivy():
    print("🎨 Launching Projectivy Launcher on Sony TV...")
    out = shell("monkey -p com.spocky.projengmenu -c android.intent.category.LAUNCHER 1")
    print("✅ Projectivy Launcher Opened!")

def set_flauncher_default():
    print("🔒 Setting FLauncher as Default & Disabling Stock Launcher...")
    shell("pm disable-user --user 0 com.google.android.tvlauncher")
    launch_flauncher()

def set_projectivy_default():
    print("🔒 Setting Projectivy Launcher as Default & Disabling Stock Launcher...")
    shell("pm disable-user --user 0 com.google.android.tvlauncher")
    launch_projectivy()

def restore_stock_launcher():
    print("🔄 Restoring Stock Google TV Launcher...")
    shell("pm enable com.google.android.tvlauncher")
    shell("monkey -p com.google.android.tvlauncher -c android.intent.category.LAUNCHER 1")
    print("✅ Stock Launcher Enabled.")

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "flauncher":
            launch_flauncher()
        elif cmd == "projectivy":
            launch_projectivy()
        elif cmd == "set-flauncher":
            set_flauncher_default()
        elif cmd == "set-projectivy":
            set_projectivy_default()
        elif cmd == "stock":
            restore_stock_launcher()
        else:
            print("Usage: python3 switch_launcher.py [flauncher | projectivy | set-flauncher | set-projectivy | stock]")
    else:
        print("Installed Launchers on TV:")
        print("1. FLauncher           : me.efesser.flauncher")
        print("2. Projectivy Launcher : com.spocky.projengmenu")
        print("3. Stock Google TV     : com.google.android.tvlauncher")

if __name__ == "__main__":
    main()
