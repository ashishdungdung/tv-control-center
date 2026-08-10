#!/usr/bin/env python3
"""
Downloads a stunning 3840x2160 Ultra HD Unsplash 4K landscape photo
and pushes it directly to /sdcard/Pictures/wallpaper.jpg on the Sony TV over ADB.
This gives you FREE 4K Unsplash wallpapers in Projectivy Launcher without paying for Premium!
"""

import urllib.request
import subprocess
import os

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

UNSPLASH_4K_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=3840&auto=format&fit=crop"

def main():
    print("📸 Downloading 3840x2160 Ultra HD Unsplash 4K Wallpaper...")
    local_file = "unsplash_4k.jpg"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(UNSPLASH_4K_URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp, open(local_file, "wb") as f:
            f.write(resp.read())
        print(f"✅ Downloaded 4K Wallpaper! Size: {os.path.getsize(local_file)} bytes")
        
        # Ensure /sdcard/Pictures exists on TV
        subprocess.run([ADB, "-s", TARGET, "shell", "mkdir -p /sdcard/Pictures"], check=True)
        
        # Push file to TV
        print("🚀 Pushing 4K Unsplash Wallpaper to TV /sdcard/Pictures/wallpaper.jpg ...")
        res = subprocess.run([ADB, "-s", TARGET, "push", local_file, "/sdcard/Pictures/wallpaper.jpg"], capture_output=True, text=True)
        print(res.stdout.strip())
        print("🎉 FREE 4K Unsplash Wallpaper is ready on your TV!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
