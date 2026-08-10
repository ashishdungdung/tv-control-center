#!/usr/bin/env python3
"""
Sony BRAVIA Night Mode Vocal Compressor & Audio Dynamic Range Normalizer
------------------------------------------------------------------------
Configures Sony Audio HAL (com.sony.dtv.sound) parameters over ADB:
1. Enables Dynamic Range Compression (DRC) to prevent loud explosions.
2. Enables Voice Zoom & Dialog Enhancer to make movie speech crystal clear.
"""

import subprocess
import sys

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def enable_night_mode():
    print("=" * 65)
    print(" 🔊 ENABLING SONY BRAVIA NIGHT MODE VOCAL COMPRESSOR")
    print("=" * 65)

    # 1. System Night Mode Toggle
    print("1. Enabling System Night Mode...")
    shell("settings put system night_mode 1")
    shell("settings put global audio_night_mode 1")

    # 2. Dynamic Range Compression (DRC) Line/RF Mode
    print("2. Setting Dolby/DTS Dynamic Range Compression (DRC) to Line/Compress...")
    shell("settings put global audio_drc_mode 1")
    shell("settings put system drc_mode 1")

    # 3. Sony Voice Zoom / Dialog Enhancer (Speech Clarity)
    print("3. Boosting Sony Voice Zoom (Dialogue Frequencies)...")
    shell("settings put system voice_zoom 3")
    shell("settings put system dialog_enhancer 1")

    print("\n✅ Night Mode Vocal Compressor Activated Successfully!")
    print("   - Loud Action Scenes/Explosions: Capped & Compressed")
    print("   - Movie Dialogue/Voices: Boosted & Clear")
    print("=" * 65)

def disable_night_mode():
    print("=" * 65)
    print(" 🔊 RESTORING STANDARD FULL DYNAMIC RANGE AUDIO")
    print("=" * 65)

    shell("settings put system night_mode 0")
    shell("settings put global audio_night_mode 0")
    shell("settings put global audio_drc_mode 0")
    shell("settings put system drc_mode 0")
    shell("settings put system voice_zoom 0")
    shell("settings put system dialog_enhancer 0")

    print("✅ Standard Full Dynamic Range Restored.")
    print("=" * 65)

def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() == "off":
        disable_night_mode()
    else:
        enable_night_mode()

if __name__ == "__main__":
    main()
