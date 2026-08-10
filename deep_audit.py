#!/usr/bin/env python3
"""
Sony BRAVIA KD-55X8000H Deep System Audit Script
Gathers comprehensive hardware, OS, kernel, CPU, RAM, storage, display, audio, network, and package specs over ADB.
"""

import subprocess
import json
import re
import os

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=20)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def prop(p: str) -> str:
    return shell(f"getprop {p}")

def main():
    audit_data = {}

    print("Gathering Device & Hardware Identifiers...")
    audit_data["hardware"] = {
        "Brand": prop("ro.product.brand"),
        "Model": prop("ro.product.model"),
        "Market Name": prop("ro.product.display"),
        "Device Name": prop("ro.product.device"),
        "Board": prop("ro.product.board"),
        "Platform / SoC": prop("ro.board.platform"),
        "Hardware": prop("ro.hardware"),
        "Manufacturer": prop("ro.product.manufacturer"),
        "Serial": prop("ro.serialno") or "Protected",
    }

    print("Gathering OS & Firmware Details...")
    audit_data["os"] = {
        "Android Version": prop("ro.build.version.release"),
        "SDK / API Level": prop("ro.build.version.sdk"),
        "Build ID": prop("ro.build.display.id"),
        "Incremental Build / Firmware": prop("ro.build.version.incremental"),
        "Security Patch Level": prop("ro.build.version.security_patch"),
        "Build Type / Tags": f"{prop('ro.build.type')} / {prop('ro.build.tags')}",
        "Kernel Version": shell("uname -r -v"),
        "Uptime": shell("uptime"),
    }

    print("Gathering CPU & Architecture Specs...")
    cpuinfo = shell("cat /proc/cpuinfo")
    cores = len(re.findall(r"^processor", cpuinfo, re.MULTILINE))
    model_name = re.search(r"Hardware\s*:\s*(.*)", cpuinfo)
    audit_data["cpu"] = {
        "Architecture": prop("ro.product.cpu.abi"),
        "Supported ABIs": prop("ro.product.cpu.abilist"),
        "CPU Cores": cores,
        "Hardware Model": model_name.group(1) if model_name else prop("ro.hardware"),
        "CPU Frequencies": shell("cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq") or "Dynamic",
    }

    print("Gathering Memory (RAM) Statistics...")
    meminfo = shell("cat /proc/meminfo")
    mem = {}
    for line in meminfo.splitlines():
        parts = line.split(":")
        if len(parts) == 2:
            mem[parts[0].strip()] = parts[1].strip()
    audit_data["ram"] = {
        "Total RAM": mem.get("MemTotal", "Unknown"),
        "Free RAM": mem.get("MemFree", "Unknown"),
        "Available RAM": mem.get("MemAvailable", "Unknown"),
        "Cached": mem.get("Cached", "Unknown"),
        "Buffers": mem.get("Buffers", "Unknown"),
        "Swap Total": mem.get("SwapTotal", "0 kB"),
        "Swap Free": mem.get("SwapFree", "0 kB"),
    }

    print("Gathering Storage & Filesystem Layout...")
    df = shell("df -h")
    audit_data["storage"] = {
        "Raw DF": df,
        "Internal Data Partition (/data)": shell("df -h /data"),
        "System Partition (/system)": shell("df -h /system"),
        "Vendor Partition (/vendor)": shell("df -h /vendor"),
    }

    print("Gathering Display & Resolution Specs...")
    wm_size = shell("wm size")
    wm_density = shell("wm density")
    sf_dump = shell("dumpsys SurfaceFlinger | grep -E 'Display|refresh|HDR'")
    audit_data["display"] = {
        "Physical Resolution": wm_size.replace("Physical size: ", ""),
        "Physical Density": wm_density.replace("Physical density: ", ""),
        "SurfaceFlinger Info": sf_dump[:500],
    }

    print("Gathering Network & Interfaces...")
    ifconfig = shell("ip addr show")
    net_props = {
        "Hostname": prop("net.hostname"),
        "Active IP / Network Interfaces": ifconfig,
        "Wi-Fi Link": shell("dumpsys wifi | grep -i 'mNetworkInfo\|Link speed\|SSID' | head -n 10"),
    }
    audit_data["network"] = net_props

    print("Auditing Installed Packages & Sony Services...")
    all_packages_raw = shell("pm list packages -u")
    all_pkgs = [p.replace("package:", "").strip() for p in all_packages_raw.splitlines() if p.startswith("package:")]
    disabled_raw = shell("pm list packages -d")
    disabled_pkgs = set([p.replace("package:", "").strip() for p in disabled_raw.splitlines() if p.startswith("package:")])
    enabled_pkgs = [p for p in all_pkgs if p not in disabled_pkgs]

    sony_pkgs = [p for p in all_pkgs if "sony" in p]
    google_pkgs = [p for p in all_pkgs if "google" in p]
    third_party_pkgs = [p for p in all_pkgs if not p.startswith("com.android") and not p.startswith("com.google") and not p.startswith("com.sony") and not p.startswith("android")]

    audit_data["packages"] = {
        "Total Installed Packages": len(all_pkgs),
        "Enabled Packages": len(enabled_pkgs),
        "Disabled Packages": len(disabled_pkgs),
        "Sony Specific Packages Count": len(sony_pkgs),
        "Google Specific Packages Count": len(google_pkgs),
        "Third-Party Apps": third_party_pkgs,
        "Disabled Package List": list(disabled_pkgs),
        "Sony Package List": sony_pkgs,
    }

    print("Gathering CPU & Process Footprint...")
    top = shell("top -n 1 -b | head -n 25")
    audit_data["performance"] = {
        "Top Active Processes": top,
        "Window Animation Scale": shell("settings get global window_animation_scale"),
        "Transition Animation Scale": shell("settings get global transition_animation_scale"),
        "Animator Duration Scale": shell("settings get global animator_duration_scale"),
    }

    # Save to JSON file for report generator
    with open("audit_results.json", "w") as f:
        json.dump(audit_data, f, indent=2)
    print("✅ Audit complete! Saved raw results to audit_results.json")

if __name__ == "__main__":
    main()
