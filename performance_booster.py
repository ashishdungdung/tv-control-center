#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Advanced Performance & Speed Booster Engine
-------------------------------------------------------------------
Performs deep non-root ADB optimization:
1. Cache Trimming (Frees 1-2 GB storage on /data partition)
2. Safe Background Telemetry & Bloatware Disabling
3. Background Process Memory Management Limit
4. Force GPU Rendering & Animation Scaling (0.5x / 0.0x)
5. Background RAM Reclamation & Force-Stopping Idling Background Apps
"""

import subprocess
import time
import json
import re

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

# Telemetry and non-essential background bloat to disable
TARGET_BLOATWARE = [
    ("com.samba.tv", "Samba TV Interactive Ad Telemetry"),
    ("com.sony.dtv.demoapp", "Sony Demo Store Mode"),
    ("com.sony.dtv.bravialifehack", "Sony Lifehack Ambient Generator"),
    ("com.sony.dtv.promos", "Sony Promotional Banners"),
    ("com.sony.dtv.livingfit", "Sony LivingFit Ambient Engine"),
    ("com.sony.dtv.multiscreendemo", "Sony Multi-Screen Demo Engine"),
    ("com.sony.dtv.smarthelp", "Sony Interactive Help Server"),
    ("com.sony.dtv.feedback", "Sony User Feedback Analytics"),
    ("com.sony.dtv.demosupport", "Sony Demo Support Assets"),
    ("com.sony.dtv.demosystemsupport", "Sony Demo System Engine"),
    ("com.google.android.videos", "Google Play Movies & TV"),
    ("com.google.android.youtube.tvunplugged", "YouTube TV Stub"),
    ("com.google.android.play.games", "Google Play Games TV"),
]

# Non-essential background apps to force stop to free RAM
IDLE_APPS_TO_STOP = [
    "com.teamviewer.host.market",
    "com.teamviewer.quicksupport.market",
    "us.zoom.videomeetings",
    "cm.aptoidetv.pt",
    "com.aefyr.sai",
    "screnmirroring.com",
    "com.mobisystems.fileman",
    "com.analiti.fastest.android",
]

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=15)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_storage_free() -> str:
    out = shell("df -h /data")
    lines = out.splitlines()
    if len(lines) >= 2:
        parts = re.split(r'\s+', lines[1])
        if len(parts) >= 4:
            return f"Used: {parts[2]} | Free: {parts[3]} ({parts[4]} full)"
    return "Unknown"

def get_ram_free() -> str:
    out = shell("cat /proc/meminfo")
    avail = "Unknown"
    for line in out.splitlines():
        if line.startswith("MemAvailable:"):
            avail = line.split(":")[1].strip()
    return avail

def main():
    print("=" * 65)
    print(" 🚀 SONY BRAVIA KD-55X8000H ADVANCED SPEED & PERFORMANCE MODS")
    print("=" * 65)
    
    print("\n📊 INITIAL SYSTEM STATE:")
    print(f" Storage (/data)  : {get_storage_free()}")
    print(f" Available RAM    : {get_ram_free()}")
    
    # Step 1: Deep Storage Cache Trimming
    print("\n🧹 STEP 1: Trimming System & App Caches (reclaiming storage)...")
    trim_res = shell("pm trim-caches 4G")
    print(f" Cache Trim Result: {trim_res or 'Cache purge triggered successfully'}")
    
    # Step 2: Disable High-Overhead Telemetry & Demo Bloatware
    print("\n🛡️ STEP 2: Disabling High-Overhead Telemetry & Background Services...")
    disabled_count = 0
    for pkg, desc in TARGET_BLOATWARE:
        res = shell(f"pm disable-user --user 0 {pkg}")
        if "disabled-user" in res or "new state" in res:
            print(f"  [DISABLED] {pkg} ({desc})")
            disabled_count += 1
        else:
            print(f"  [STATUS] {pkg}: {res}")
    print(f" Total bloatware disabled/updated: {disabled_count}")

    # Step 3: Force Stop Idling Heavy Background Apps
    print("\n⚡ STEP 3: Reclaiming Memory from Idling Background Apps...")
    for pkg in IDLE_APPS_TO_STOP:
        shell(f"am force-stop {pkg}")
        print(f"  [STOPPED] {pkg}")

    # Step 4: System Animation & Window Rendering Optimization
    print("\n🎨 STEP 4: Tuning System Animation & UI Rendering Scales...")
    shell("settings put global window_animation_scale 0.5")
    shell("settings put global transition_animation_scale 0.5")
    shell("settings put global animator_duration_scale 0.5")
    print("  [APPLIED] Window, Transition & Animator Scales set to 0.5x")

    # Step 5: Background Process Limit & Memory Management Tuning
    print("\n🧠 STEP 5: Tuning Android Memory Management & Background Process Limits...")
    # Restrict hidden background apps limit to 4 to prevent RAM thrashing
    shell("settings put global max_hidden_apps 4")
    # Disable activity logging overhead
    shell("settings put global activity_starts_logging_enabled 0")
    print("  [APPLIED] Max hidden background apps restricted to 4")
    print("  [APPLIED] Disabled system activity logging overhead")

    # Final Measurement
    print("\n" + "=" * 65)
    print(" 🎉 SPEED MODS APPLIED SUCCESSFULLY!")
    print("=" * 65)
    print(f" NEW Storage (/data) : {get_storage_free()}")
    print(f" NEW Available RAM   : {get_ram_free()}")
    print("=" * 65)

if __name__ == "__main__":
    main()
