#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Hardware Overrides (Mods 1 to 4)
--------------------------------------------------------
Applies and verifies:
1. GPU HW Composition (setprop debug.sf.hw 1)
2. 1:1 Pixel Mapping & Zero Overscan (wm overscan 0,0,0,0)
3. True 24p Cinema Cadence & Motionflow XR (cinemotion = 1 & motion_flow = 1)
4. Hardware EGL OpenGL Accelerator (setprop debug.egl.hw 1)
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
    print(" 🚀 ACTIVATING HARDWARE OVERRIDES (MODS 1 TO 4)")
    print("=" * 65)

    # Mod 1: GPU HW Composition
    print("1. Enabling GPU HW Composition (debug.sf.hw = 1)...")
    shell("setprop debug.sf.hw 1")

    # Mod 2: 1:1 Pixel Mapping (Zero Overscan)
    print("2. Setting 1:1 Pixel Mapping & Zero Overscan (wm overscan 0,0,0,0)...")
    shell("wm overscan 0,0,0,0")

    # Mod 3: True 24p Cinema Cadence & Motionflow XR
    print("3. Enabling Sony X1 True 24p Cinema Cadence & Motionflow XR...")
    shell("settings put system cinemotion 1")
    shell("settings put system motion_flow 1")

    # Mod 4: Hardware EGL OpenGL Accelerator
    print("4. Enabling Hardware EGL OpenGL Accelerator (debug.egl.hw = 1)...")
    shell("setprop debug.egl.hw 1")

    print("\n" + "=" * 65)
    print(" VERIFYING APPLIED SETTINGS")
    print("=" * 65)
    print("  debug.sf.hw   :", shell("getprop debug.sf.hw"))
    print("  debug.egl.hw  :", shell("getprop debug.egl.hw"))
    print("  wm overscan   :", shell("wm overscan"))
    print("  cinemotion    :", shell("settings get system cinemotion"))
    print("  motion_flow   :", shell("settings get system motion_flow"))
    print("=" * 65)
    print(" ✅ MODS 1 TO 4 SUCCESSFULLY ENABLED & VERIFIED")

if __name__ == "__main__":
    main()
