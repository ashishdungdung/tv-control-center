#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Wireless ADB Toolkit & Developer Suite
---------------------------------------------------------------
Features:
- Wireless ADB Connection & Auto-Discovery
- Full System & Hardware Auditing
- Safe Sony-Specific Debloating Engine (with strict safety guards)
- Performance & UI Animation Tweaker
- One-Click Launcher & App Sideloader
- Virtual Remote Controller for laptop keyboard control
- Live Logcat Developer Stream
"""

import sys
import os
import subprocess
import shutil
import json
import re
import socket, time
from typing import List, Dict, Tuple, Optional

# Package Safety Database for Sony BRAVIA Android 10 (X80H / X8000H Series)
SAFE_TO_DISABLE = {
    # Demo & Unused Factory Bloat
    "com.sony.dtv.demoapp": "Sony Demo Mode App",
    "com.sony.dtv.bravialifehack": "Sony Lifehack App",
    "com.sony.dtv.promotionalcustom launcher": "Sony Promo Launcher Assets",
    "com.samba.tv": "Samba TV Interactive Tracking/Telemetry",
    "com.google.android.videos": "Google Play Movies & TV",
    "com.google.android.youtube.tvunplugged": "YouTube TV (if unused)",
    "com.google.android.play.games": "Google Play Games TV",
    "com.amazon.amazonvideo.livingroom": "Prime Video Stub (Disable if not using Prime)",
    "com.netflix.ninja": "Netflix (Disable ONLY if you don't use Netflix)",
    
    # Non-essential Google / Sony Services
    "com.sony.dtv.smarthelp": "Sony Help / Manual App",
    "com.sony.dtv.bravia.voice.guidance": "Sony TalkBack Voice Guidance (if unused)",
    "com.sony.dtv.feedback": "Sony User Feedback Collector",
    "com.sony.dtv.app.pip": "Sony PIP Guide (if unused)",
}

CAUTION_PACKAGES = {
    "com.google.android.katniss": "Google Assistant Voice Search (Disabling breaks voice remote search)",
    "com.google.android.tvlauncher": "Stock Android TV Launcher (ONLY disable AFTER installing FLauncher/Projectivy!)",
    "com.sony.dtv.tvx": "Sony TV Home / Channel Bar",
    "com.sony.dtv.sonyselect": "Sony Select App Store / Recommendations",
}

CRITICAL_DO_NOT_TOUCH = {
    "com.sony.dtv.hardware": "Sony TV Hardware Abstraction Layer",
    "com.sony.dtv.tvinput.hdmi": "Sony HDMI Input Manager",
    "com.sony.dtv.cec": "Bravia Sync / HDMI-CEC Control",
    "com.sony.dtv.sound": "Sony Audio / Sound Processing Engine",
    "com.sony.dtv.picture": "Sony X1 Picture Processing Engine",
    "com.sony.dtv.remote": "Sony Bluetooth / IR Remote Control Service",
    "com.sony.dtv.braviasync": "Bravia Sync Core",
    "com.sony.dtv.tvinput.tuner": "Sony Digital/Analog TV Tuner",
    "com.sony.dtv.firmwareupdate": "Sony System Firmware Updater",
    "android": "Android OS Core System",
    "com.android.systemui": "Android System UI Bar",
    "com.android.settings": "Android System Settings",
    "com.google.android.gms": "Google Play Services (Core system requirement)",
}

def get_adb_binary() -> str:
    """Find adb binary path on macOS / Linux."""
    # Check PATH
    adb_path = shutil.which("adb")
    if adb_path:
        return adb_path
    
    # Common macOS Homebrew / Android SDK locations
    candidates = [
        "/opt/homebrew/bin/adb",
        "/usr/local/bin/adb",
        os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")
    ]
    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
            
    print("❌ Error: ADB command not found.")
    print("Please install android-platform-tools or add ADB to your PATH.")
    sys.exit(1)

def run_adb(args: List[str], target_device: Optional[str] = None) -> Tuple[int, str, str]:
    """Execute an ADB command and return stdout/stderr."""
    adb_bin = get_adb_binary()
    cmd = [adb_bin]
    if target_device:
        cmd.extend(["-s", target_device])
    cmd.extend(args)
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def list_connected_devices() -> List[Dict[str, str]]:
    """Return list of connected ADB devices."""
    code, stdout, _ = run_adb(["devices", "-l"])
    devices = []
    if code == 0:
        lines = stdout.splitlines()
        for line in lines[1:]:
            if line.strip():
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 2:
                    dev_id = parts[0]
                    status = parts[1]
                    details = " ".join(parts[2:])
                    devices.append({"id": dev_id, "status": status, "details": details})
    return devices

def scan_local_network_for_adb(subnet: str = "192.168.1", port: int = 5555, timeout: float = 0.3) -> List[str]:
    """Scan local Wi-Fi subnet for open port 5555 (ADB)."""
    print(f"🔍 Scanning local subnet {subnet}.0/24 for active ADB TV on port {port}...")
    found_ips = []
    
    def check_ip(ip: str):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                found_ips.append(ip)
        except Exception:
            pass

    import concurrent.futures
    ips = [f"{subnet}.{i}" for i in range(1, 255)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(check_ip, ips)
        
    return found_ips

def get_device_info(target_device: str) -> Dict[str, str]:
    """Fetch system properties from TV."""
    props = {}
    
    def get_prop(name: str) -> str:
        _, out, _ = run_adb(["shell", "getprop", name], target_device)
        return out if out else "Unknown"

    props["Model"] = get_prop("ro.product.model")
    props["Device Code"] = get_prop("ro.product.device")
    props["Brand"] = get_prop("ro.product.brand")
    props["Android Version"] = get_prop("ro.build.version.release")
    props["SDK Level"] = get_prop("ro.build.version.sdk")
    props["Build ID"] = get_prop("ro.build.display.id")
    props["Software Version"] = get_prop("ro.build.version.incremental")
    props["CPU Architecture"] = get_prop("ro.product.cpu.abi")
    
    # Resolution & Density
    _, wm_size, _ = run_adb(["shell", "wm", "size"], target_device)
    _, wm_density, _ = run_adb(["shell", "wm", "density"], target_device)
    props["Screen Size"] = wm_size.replace("Physical size: ", "") if wm_size else "Unknown"
    props["Screen Density"] = wm_density.replace("Physical density: ", "") if wm_density else "Unknown"
    
    # Memory Info
    _, meminfo, _ = run_adb(["shell", "cat", "/proc/meminfo"], target_device)
    for line in meminfo.splitlines():
        if line.startswith("MemTotal:"):
            props["Total RAM"] = line.split(":")[1].strip()
        elif line.startswith("MemAvailable:"):
            props["Available RAM"] = line.split(":")[1].strip()
            
    # Storage Info
    _, df_out, _ = run_adb(["shell", "df", "-h", "/data"], target_device)
    lines = df_out.splitlines()
    if len(lines) >= 2:
        parts = re.split(r'\s+', lines[1])
        if len(parts) >= 4:
            props["Internal Storage (Data)"] = f"Total: {parts[1]}, Used: {parts[2]}, Free: {parts[3]}"
            
    return props

def audit_packages(target_device: str) -> Dict[str, List[Dict[str, str]]]:
    """Categorize all installed packages on the TV."""
    _, stdout, _ = run_adb(["shell", "pm", "list", "packages", "-u"], target_device)
    packages = [line.replace("package:", "").strip() for line in stdout.splitlines() if line.startswith("package:")]
    
    # Get disabled packages
    _, disabled_out, _ = run_adb(["shell", "pm", "list", "packages", "-d"], target_device)
    disabled_pkgs = set([line.replace("package:", "").strip() for line in disabled_out.splitlines() if line.startswith("package:")])
    
    result = {
        "safe_to_disable": [],
        "caution": [],
        "critical": [],
        "other": []
    }
    
    for pkg in sorted(packages):
        status = "Disabled" if pkg in disabled_pkgs else "Enabled"
        pkg_data = {"package": pkg, "status": status}
        
        if pkg in SAFE_TO_DISABLE:
            pkg_data["desc"] = SAFE_TO_DISABLE[pkg]
            result["safe_to_disable"].append(pkg_data)
        elif pkg in CAUTION_PACKAGES:
            pkg_data["desc"] = CAUTION_PACKAGES[pkg]
            result["caution"].append(pkg_data)
        elif pkg in CRITICAL_DO_NOT_TOUCH or pkg.startswith("com.sony.dtv.hardware") or pkg.startswith("com.sony.dtv.sound") or pkg.startswith("com.sony.dtv.picture"):
            pkg_data["desc"] = CRITICAL_DO_NOT_TOUCH.get(pkg, "Critical Sony Core Hardware/Processing")
            result["critical"].append(pkg_data)
        else:
            pkg_data["desc"] = "General/Third-party Package"
            result["other"].append(pkg_data)
            
    return result

def set_animation_scales(target_device: str, scale: float = 0.5) -> bool:
    """Tune UI animation scales for smoother/snappier performance."""
    scale_str = str(scale)
    code1, _, _ = run_adb(["shell", "settings", "put", "global", "window_animation_scale", scale_str], target_device)
    code2, _, _ = run_adb(["shell", "settings", "put", "global", "transition_animation_scale", scale_str], target_device)
    code3, _, _ = run_adb(["shell", "settings", "put", "global", "animator_duration_scale", scale_str], target_device)
    return code1 == 0 and code2 == 0 and code3 == 0

def send_key_event(target_device: str, key_code: int) -> bool:
    """Send keypress event to Android TV."""
    code, _, _ = run_adb(["shell", "input", "keyevent", str(key_code)], target_device)
    return code == 0

# Keycode map for Virtual Remote
KEYCODES = {
    "up": 19,
    "down": 20,
    "left": 21,
    "right": 22,
    "select": 66,  # Enter
    "enter": 66,
    "back": 4,     # ESC or Back
    "home": 3,
    "menu": 82,
    "volup": 24,
    "voldown": 25,
    "mute": 164,
    "playpause": 85
}

def interactive_cli():
    print("=" * 60)
    print(" SONY BRAVIA KD-55X8000H WIRELESS ADB TOOLKIT (Android 10)")
    print("=" * 60)
    
    devices = list_connected_devices()
    target_device = None
    
    if devices:
        print("\nConnected Devices:")
        for idx, dev in enumerate(devices):
            print(f" [{idx + 1}] {dev['id']} ({dev['status']}) - {dev['details']}")
        sel = input("\nSelect device number (or press Enter for device 1): ").strip()
        idx = int(sel) - 1 if sel.isdigit() and 1 <= int(sel) <= len(devices) else 0
        target_device = devices[idx]["id"]
    else:
        print("\nNo ADB devices connected directly yet.")
        tv_ip = input("Enter TV IP Address (e.g. 192.168.1.50) or press [S] to scan network: ").strip()
        if tv_ip.upper() == 'S':
            local_ip = "192.168.1"
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                my_ip = s.getsockname()[0]
                s.close()
                local_ip = ".".join(my_ip.split(".")[:3])
            except Exception:
                pass
            found = scan_local_network_for_adb(subnet=local_ip)
            if found:
                print(f"\nFound potential TV IP(s): {', '.join(found)}")
                tv_ip = found[0]
            else:
                print("No active ADB devices found automatically. Make sure Developer Options & Network Debugging are enabled on TV.")
                return

        if tv_ip:
            print(f"Connecting to {tv_ip}:5555 ...")
            code, out, err = run_adb(["connect", f"{tv_ip}:5555"])
            print(out or err)
            devices = list_connected_devices()
            if devices:
                target_device = devices[0]["id"]
            else:
                print("⚠️ Connection pending authorization on TV screen. Check your TV and select 'Always allow from this computer'.")
                return

    if not target_device:
        print("No active device target selected.")
        return

    print(f"\n✅ Active TV Target: {target_device}")
    
    while True:
        print("\n--- MENU ---")
        print("1. View TV System & Hardware Audit")
        print("2. Package Debloater Audit & Manager (Safe Sony Profiles)")
        print("3. Apply UI Speedup Mod (Set animation scale to 0.5x)")
        print("4. Virtual Keyboard Remote Controller")
        print("5. Sideload APK / App Installer")
        print("6. Live Developer Logcat Stream")
        print("0. Exit")
        
        choice = input("\nSelect option [0-6]: ").strip()
        
        if choice == "1":
            print("\nFetching Hardware & System Props...")
            info = get_device_info(target_device)
            print("-" * 50)
            for k, v in info.items():
                print(f" {k:<25}: {v}")
            print("-" * 50)
            
        elif choice == "2":
            print("\nAuditing installed packages against Sony BRAVIA safe rules...")
            audit = audit_packages(target_device)
            print(f"\n🟢 Safe to Disable ({len(audit['safe_to_disable'])} packages):")
            for item in audit["safe_to_disable"]:
                print(f"  [{item['status']}] {item['package']} - {item['desc']}")
                
            print(f"\n🟡 Caution Required ({len(audit['caution'])} packages):")
            for item in audit["caution"]:
                print(f"  [{item['status']}] {item['package']} - {item['desc']}")

            print(f"\n🔴 Critical Sony System Components ({len(audit['critical'])} packages protected):")
            for item in audit["critical"][:5]:
                print(f"  [PROTECTED] {item['package']} - {item['desc']}")
            print("  ... and more core system services.")

            action = input("\nType 'disable-safe' to disable recommended safe bloatware, or 'enable-all' to restore: ").strip()
            if action == "disable-safe":
                for item in audit["safe_to_disable"]:
                    pkg = item["package"]
                    print(f"Disabling {pkg}...")
                    run_adb(["shell", "pm", "disable-user", "--user", "0", pkg], target_device)
                print("✅ Safe debloating applied.")
            elif action == "enable-all":
                for item in audit["safe_to_disable"]:
                    pkg = item["package"]
                    print(f"Enabling {pkg}...")
                    run_adb(["shell", "pm", "enable", pkg], target_device)
                print("✅ Packages re-enabled.")
                
        elif choice == "3":
            print("\nApplying UI speedup tweaks (window, transition & duration animation scales = 0.5x)...")
            if set_animation_scales(target_device, 0.5):
                print("✅ UI Speedup applied! Menu transitions will feel twice as fast.")
            else:
                print("❌ Failed to set animation scales.")

        elif choice == "4":
            print("\n🎮 Virtual Keyboard Remote Control Active!")
            print("Controls: W/A/S/D or Arrow keys = Navigate | Enter = Select | ESC = Back | H = Home | M = Menu | + / - = Volume")
            print("Type 'q' and press Enter to exit remote mode.")
            try:
                while True:
                    cmd = input("Remote Key > ").strip().lower()
                    if cmd == 'q':
                        break
                    elif cmd in ['w', 'up']:
                        send_key_event(target_device, KEYCODES["up"])
                    elif cmd in ['s', 'down']:
                        send_key_event(target_device, KEYCODES["down"])
                    elif cmd in ['a', 'left']:
                        send_key_event(target_device, KEYCODES["left"])
                    elif cmd in ['d', 'right']:
                        send_key_event(target_device, KEYCODES["right"])
                    elif cmd in ['', 'enter', 'e']:
                        send_key_event(target_device, KEYCODES["select"])
                    elif cmd in ['esc', 'b', 'back']:
                        send_key_event(target_device, KEYCODES["back"])
                    elif cmd in ['h', 'home']:
                        send_key_event(target_device, KEYCODES["home"])
                    elif cmd in ['m', 'menu']:
                        send_key_event(target_device, KEYCODES["menu"])
                    elif cmd in ['+', 'volup']:
                        send_key_event(target_device, KEYCODES["volup"])
                    elif cmd in ['-', 'voldown']:
                        send_key_event(target_device, KEYCODES["voldown"])
            except KeyboardInterrupt:
                pass

        elif choice == "5":
            apk_path = input("Enter path to APK file on your laptop: ").strip()
            if os.path.isfile(apk_path):
                print(f"Installing {apk_path} on TV...")
                code, out, err = run_adb(["install", "-r", apk_path], target_device)
                print(out or err)
            else:
                print("❌ File not found.")

        elif choice == "6":
            pkg = input("Filter by Package Name (optional, e.g. com.example.myapp, or press Enter for all): ").strip()
            print("Starting Logcat stream (Press Ctrl+C to stop)...")
            cmd = ["shell", "logcat"]
            if pkg:
                # Get PID for package
                _, pid_out, _ = run_adb(["shell", "pidof", pkg], target_device)
                if pid_out:
                    cmd.extend(["--pid", pid_out.split()[0]])
            try:
                adb_bin = get_adb_binary()
                full_cmd = [adb_bin, "-s", target_device] + cmd
                proc = subprocess.Popen(full_cmd)
                proc.wait()
            except KeyboardInterrupt:
                proc.terminate()
                print("\nLogcat stopped.")

        elif choice == "0":
            print("Exiting toolkit. Happy tinkering!")
            break

if __name__ == "__main__":
    interactive_cli()
