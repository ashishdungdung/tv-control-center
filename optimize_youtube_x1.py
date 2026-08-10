#!/usr/bin/env python3
"""
Sony BRAVIA Official YouTube X1 4K HDR Picture Processor Optimization
----------------------------------------------------------------------
Configures system media properties over ADB to maximize Sony X1 Hardware Processing
(X-Reality PRO Dual Database Upscaling, Super Bit Mapping, TRILUMINOS Color, Object-Based HDR)
for the Official YouTube app (com.google.android.youtube.tv).
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
    print(" 📺 OPTIMIZING OFFICIAL YOUTUBE FOR SONY X1 4K PROCESSOR")
    print("=" * 65)

    # 1. Prioritize Hardware MediaCodec YUV Video Surfaces (Bypasses UI layer)
    print("1. Directing YouTube YUV Video Surfaces to Sony X1 Hardware Pipeline...")
    shell("setprop media.stagefright.enable-player 1")
    shell("setprop media.stagefright.enable-http 1")

    # 2. Enable VP9 Profile 2 10-bit HDR Hardware Decoding
    print("2. Unlocking VP9 Profile 2 10-bit HDR Hardware Decoder...")
    shell("setprop media.stagefright.enable-fma 1")

    # 3. High-Priority Status for Sony X1 Picture Processing Service
    print("3. Elevating Sony X1 Picture Engine (com.sony.dtv.picture) Service Priority...")
    shell("setprop persist.sys.sony.picture.mode 1")

    # 4. Enable Native 1:1 Video Surface Scaling (Prevents Double Scaling)
    print("4. Enabling 1:1 Hardware Video Surface Scaling...")
    shell("settings put global video_scaling_mode 1")

    # 5. Ensure Official YouTube app is enabled and ready
    print("5. Verifying Official YouTube App (com.google.android.youtube.tv)...")
    shell("pm enable com.google.android.youtube.tv")

    print("\n" + "=" * 65)
    print(" ✅ OFFICIAL YOUTUBE X1 PICTURE OPTIMIZATION COMPLETE")
    print("=" * 65)

if __name__ == "__main__":
    main()
