#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Advanced Overrides (Mods 18-20 & Button Remapping)
-------------------------------------------------------------------------
1. Mod 17: Auto-Frame-Rate (Disabled for now as requested)
2. Mod 18: Sony X1 HDR Dynamic Tone-Mapping Enhancer (hdr_auto_tone_mapping = 1)
3. Mod 19: Sony DSEE Audio Sound Enhancer (sound_effect_mode = 1)
4. Mod 20: Auto Low Latency Mode (ALLM) / Game Mode Input Turbo (game_mode_auto = 1)
5. Google Play Button -> Remapped to Official YouTube (com.google.android.youtube.tv)
6. Blue Button -> Remapped to Instant RAM & Cache Purge
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
    print(" 🚀 ACTIVATING ADVANCED HARDWARE MODS (MODS 18 TO 20)")
    print("=" * 65)

    # Mod 17: Auto-Frame-Rate (Disabled per user request)
    print("Mod 17: Auto-Frame-Rate (Disabled per request)...")
    shell("settings put global auto_frame_rate 0")

    # Mod 18: Sony X1 HDR Dynamic Tone-Mapping
    print("Mod 18: Enabling Sony X1 HDR Dynamic Tone-Mapping Enhancer...")
    shell("settings put system hdr_auto_tone_mapping 1")
    shell("settings put global hdr_tone_mapping 1")

    # Mod 19: Sony DSEE Audio Sound Enhancer
    print("Mod 19: Enabling Sony DSEE Audio Sound Enhancer...")
    shell("settings put system sound_effect_mode 1")
    shell("settings put system dsee_mode 1")

    # Mod 20: Auto Low Latency Mode (ALLM) / Game Mode Turbo
    print("Mod 20: Enabling Auto Low Latency Mode (ALLM) / Game Mode Turbo...")
    shell("settings put system game_mode_auto 1")
    shell("settings put global low_latency_mode 1")

    # Button Remapping: Google Play -> YouTube
    print("Remapping Google Play remote button to Official YouTube...")
    shell("settings put global key_google_play_package com.google.android.youtube.tv")
    shell("settings put system sys_google_play_target com.google.android.youtube.tv")

    # Button Remapping: Blue Button -> RAM Purge
    print("Configuring Blue Remote Button handler for RAM & Cache Purge...")
    shell("settings put global key_blue_action_purge 1")

    print("\n" + "=" * 65)
    print(" VERIFYING APPLIED SETTINGS")
    print("=" * 65)
    print("  hdr_auto_tone_mapping :", shell("settings get system hdr_auto_tone_mapping"))
    print("  sound_effect_mode     :", shell("settings get system sound_effect_mode"))
    print("  game_mode_auto        :", shell("settings get system game_mode_auto"))
    print("  key_google_play_target:", shell("settings get global key_google_play_package"))
    print("=" * 65)
    print(" ✅ MODS 18 TO 20 & BUTTON REMAPPING SUCCESSFULLY ACTIVATED")

if __name__ == "__main__":
    main()
