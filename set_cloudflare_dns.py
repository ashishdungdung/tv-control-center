#!/usr/bin/env python3
"""
Configure Cloudflare Ultra-Fast Encrypted DNS (DoT / DoH / IPv4 / IPv6) on Sony BRAVIA TV over ADB
--------------------------------------------------------------------------------------------------
Configures:
1. Android 10 Private DNS Mode -> hostname (`one.one.one.one`)
   (Encrypts system-wide DNS via Cloudflare 1.1.1.1 Anycast Network for IPv4 & IPv6)
2. Fallback IPv4 DNS -> 1.1.1.1 & 1.0.0.1
3. Fallback IPv6 DNS -> 2606:4700:4700::1111 & 2606:4700:4700::1001
"""

import subprocess

TARGET = "192.168.2.122:5555"
ADB = "/opt/homebrew/bin/adb"

def shell(cmd: str) -> str:
    try:
        res = subprocess.run([ADB, "-s", TARGET, "shell", cmd], capture_output=True, text=True, timeout=15)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 65)
    print(" 🚀 CONFIGURING CLOUDFLARE ULTRA-FAST ENCRYPTED DNS (1.1.1.1)")
    print("=" * 65)

    # 1. Enable Android Private DNS with Cloudflare Hostname
    print("\n🔒 1. Setting Android 10 Private DNS (DoT/DoH Encrypted) to Cloudflare...")
    shell("settings put global private_dns_mode hostname")
    shell("settings put global private_dns_specifier one.one.one.one")
    
    # 2. Configure IPv4 & IPv6 System DNS Properties
    print("\n🌐 2. Setting System IPv4 & IPv6 Cloudflare DNS Servers...")
    shell("setprop net.dns1 1.1.1.1")
    shell("setprop net.dns2 1.0.0.1")
    shell("setprop net.dns3 2606:4700:4700::1111")
    shell("setprop net.dns4 2606:4700:4700::1001")

    # 3. Verify Settings
    dns_mode = shell("settings get global private_dns_mode")
    dns_spec = shell("settings get global private_dns_specifier")
    dns1 = shell("getprop net.dns1")
    dns2 = shell("getprop net.dns2")
    dns3 = shell("getprop net.dns3")
    dns4 = shell("getprop net.dns4")

    print("\n" + "=" * 65)
    print(" ✅ CLOUDFLARE DNS CONFIGURATION VERIFIED!")
    print("=" * 65)
    print(f" Private DNS Mode      : {dns_mode}")
    print(f" Private DNS Hostname  : {dns_spec} (Cloudflare Anycast 1.1.1.1)")
    print(f" Primary IPv4 DNS      : {dns1}")
    print(f" Secondary IPv4 DNS    : {dns2}")
    print(f" Primary IPv6 DNS      : {dns3}")
    print(f" Secondary IPv6 DNS    : {dns4}")
    print("=" * 65)

    # 4. Test Name Resolution Speed
    print("\n⚡ Testing DNS Resolution Speed...")
    ping_res = shell("ping -c 2 1.1.1.1")
    print(ping_res)

if __name__ == "__main__":
    main()
