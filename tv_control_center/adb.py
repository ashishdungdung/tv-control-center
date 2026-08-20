"""
ADB Execution Engine & Discovery Bridge
---------------------------------------
Handles non-blocking, multi-threaded ADB communication, dynamic target
pairing, device verification, and subnet auto-discovery for Smart TVs.
"""

import subprocess
import shutil
import socket
import concurrent.futures
import os
from typing import List, Dict, Optional, Any

ADB_BIN = shutil.which("adb") or "/opt/homebrew/bin/adb"
DEFAULT_TARGET = "192.168.2.122:5555"
_active_target = DEFAULT_TARGET

def get_active_target() -> str:
    """Returns the currently active ADB target."""
    global _active_target
    return _active_target

def set_active_target(target: str) -> None:
    """Sets the active ADB target."""
    global _active_target
    if target:
        if ":" not in target:
            target = f"{target}:5555"
        _active_target = target

def run_adb_timeout(args: List[str], target: Optional[str] = None, timeout: float = 8.0) -> str:
    """Runs ADB command with strict execution timeout."""
    tgt = target or get_active_target()
    cmd = [ADB_BIN]
    if tgt:
        cmd.extend(["-s", tgt])
    cmd.extend(args)
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = res.stdout.strip()
        err = res.stderr.strip()
        if res.returncode != 0 and err:
            return f"Error: {err}"
        return out if out else ("Success" if res.returncode == 0 else "No Output")
    except subprocess.TimeoutExpired:
        return f"Error: ADB command '{' '.join(args)}' timed out after {timeout}s"
    except Exception as e:
        return f"Error executing ADB: {str(e)}"

def get_devices() -> List[str]:
    """Returns connected and authorized ADB devices."""
    try:
        res = subprocess.run([ADB_BIN, "devices"], capture_output=True, text=True, timeout=4.0)
        lines = res.stdout.strip().splitlines()
        devs = []
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                devs.append(parts[0])
        return devs
    except Exception:
        return []

def get_device_info(target: Optional[str] = None) -> Dict[str, Any]:
    """Fetches detailed product info for a target device."""
    tgt = target or get_active_target()
    model = run_adb_timeout(["shell", "getprop", "ro.product.model"], tgt, timeout=2.5)
    brand = run_adb_timeout(["shell", "getprop", "ro.product.brand"], tgt, timeout=2.5)
    manufacturer = run_adb_timeout(["shell", "getprop", "ro.product.manufacturer"], tgt, timeout=2.5)
    android_ver = run_adb_timeout(["shell", "getprop", "ro.build.version.release"], tgt, timeout=2.5)
    sdk_ver = run_adb_timeout(["shell", "getprop", "ro.build.version.sdk"], tgt, timeout=2.5)

    is_valid = not ("Error" in model or not model or model == "No Output")
    return {
        "target": tgt,
        "connected": is_valid,
        "model": model if is_valid else "Unknown Model",
        "brand": brand if is_valid else "Smart TV",
        "manufacturer": manufacturer if is_valid else "Generic",
        "android_version": android_ver if is_valid else "Unknown",
        "sdk_version": sdk_ver if is_valid else "Unknown"
    }

def connect_adb(ip: str, port: int = 5555) -> Dict[str, Any]:
    """Connects to a remote TV via ADB over Wi-Fi/LAN and validates connection."""
    target = f"{ip}:{port}"
    try:
        res = subprocess.run([ADB_BIN, "connect", target], capture_output=True, text=True, timeout=6.0)
        out = res.stdout.strip()
        
        # Check authorization and status
        devs_raw = subprocess.run([ADB_BIN, "devices"], capture_output=True, text=True, timeout=4.0).stdout
        if "unauthorized" in devs_raw and target in devs_raw:
            return {
                "status": "unauthorized",
                "target": target,
                "message": "Authorization pending. Please accept the RSA key prompt on your TV screen ('Always allow from this computer')."
            }
        
        info = get_device_info(target)
        if info["connected"]:
            set_active_target(target)
            return {
                "status": "connected",
                "target": target,
                "message": f"Successfully connected to {info['brand']} {info['model']} ({target})",
                "device": info
            }
        else:
            return {
                "status": "failed",
                "target": target,
                "message": out if out else f"Failed to connect to {target}. Verify TV IP & ADB Debugging are turned ON."
            }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "target": target, "message": f"Connection to {target} timed out after 6.0s."}
    except Exception as e:
        return {"status": "error", "target": target, "message": str(e)}

def disconnect_adb(target: Optional[str] = None) -> Dict[str, Any]:
    """Disconnects from a remote TV ADB session."""
    tgt = target or get_active_target()
    try:
        res = subprocess.run([ADB_BIN, "disconnect", tgt], capture_output=True, text=True, timeout=4.0)
        return {"status": "disconnected", "target": tgt, "result": res.stdout.strip()}
    except Exception as e:
        return {"status": "error", "target": tgt, "message": str(e)}

def get_local_ip() -> str:
    """Detects local machine IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '192.168.1.100'
    finally:
        s.close()
    return ip

def check_socket_port(ip: str, port: int = 5555, timeout: float = 0.25) -> Optional[str]:
    """Checks if an ADB port (5555) is open on target IP."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.close()
        return ip
    except Exception:
        return None

def scan_network_devices(port: int = 5555) -> List[Dict[str, Any]]:
    """Fast concurrent subnet scanner to auto-discover active Android TVs on port 5555."""
    local_ip = get_local_ip()
    prefix = '.'.join(local_ip.split('.')[:3]) + '.'
    ips = [f"{prefix}{i}" for i in range(1, 255)]
    
    open_ips = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        futures = {executor.submit(check_socket_port, ip, port, 0.3): ip for ip in ips}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                open_ips.append(res)
    
    # Check currently connected ADB devices
    connected_devs = get_devices()
    for d in connected_devs:
        ip_only = d.split(':')[0]
        if ip_only not in open_ips and "." in ip_only:
            open_ips.append(ip_only)
    
    devices = []
    for ip in open_ips:
        tgt = f"{ip}:{port}"
        info = get_device_info(tgt)
        devices.append({
            "ip": ip,
            "port": port,
            "target": tgt,
            "brand": info.get("brand", "Smart TV"),
            "model": info.get("model", f"Android TV ({ip})"),
            "connected": info.get("connected", False)
        })
    
    return devices
