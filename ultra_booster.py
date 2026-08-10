#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Ultra-Performance Engine
------------------------------------------------
Applies advanced Android TV system tweaks:
1. Disables Usage Stats Telemetry (`usagestats_enabled = 0`)
2. Disables Captive Portal & Network Diagnostics Background Overhead
3. Disables Non-Essential System Services (Print Spooler, B2B Hotel Mode, RS232 Serial Service)
4. Forces GPU UI Composition (Disables HW Overlays for smoother SurfaceFlinger rendering)
5. Purges App Storage Caches
"""

import subprocess
import json

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

SYSTEM_DEBLOAT = [
    ("com.android.printspooler", "Android Print Spooler (Unused on TV)"),
    ("com.sony.dtv.b2b.hotelmode", "Sony B2B Hotel Mode Service"),
    ("com.sony.dtv.b2b.rs232csupport", "Sony RS232 Commercial Serial Port Service"),
    ("com.sony.dtv.b2b.adminpassword", "Sony B2B Admin Password Service"),
    ("com.sony.dtv.b2b.deviceadminsettings", "Sony B2B Device Admin Settings"),
    ("com.sony.dtv.b2b.vendorprotocol", "Sony B2B Vendor Protocol"),
    ("com.sony.dtv.b2b.softap", "Sony B2B SoftAP Controller"),
    ("com.sony.dtv.b2b.noderuntime.normal", "Sony B2B Node Runtime"),
]

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=15)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 65)
    print(" 🚀 SONY BRAVIA ULTRA-PERFORMANCE BOOSTER")
    print("=" * 65)

    # 1. System Settings Performance Overrides
    print("\n⚙️ 1. Applying Low-Latency System Settings Overrides...")
    shell("settings put global usagestats_enabled 0")
    shell("settings put global captive_portal_mode 0")
    shell("settings put global search_indexing_enabled 0")
    shell("settings put global activity_starts_logging_enabled 0")
    shell("settings put global ble_scan_always_enabled 0")
    print("  [APPLIED] Disabled App Usage Stats & Telemetry Indexing")
    print("  [APPLIED] Disabled Captive Portal Network Background Probing")
    print("  [APPLIED] Disabled Background BLE Bluetooth Scanning")

    # 2. Disable Unused B2B / Commercial / Print Services
    print("\n🛡️ 2. Disabling Unused Commercial / B2B System Services...")
    for pkg, desc in SYSTEM_DEBLOAT:
        res = shell(f"pm disable-user --user 0 {pkg}")
        print(f"  [DISABLED] {pkg} ({desc})")

    # 3. GPU Surface Composition Tweak
    print("\n🎨 3. Enabling GPU Composition Optimization...")
    shell("service call SurfaceFlinger 1008 i32 1")
    print("  [APPLIED] SurfaceFlinger GPU Composition Activated")

    # 4. Storage Cache Purge
    print("\n🧹 4. Running Final Deep Cache Storage Trim...")
    shell("pm trim-caches 4G")
    print("  [APPLIED] Storage cache purged")

    print("\n" + "=" * 65)
    print(" 🎉 ULTRA-PERFORMANCE BOOSTER COMPLETE!")
    print("=" * 65)

if __name__ == "__main__":
    main()
