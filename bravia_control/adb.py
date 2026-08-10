"""
ADB Execution Engine
-------------------
Handles non-blocking, multi-threaded ADB communication with the Sony BRAVIA TV.
"""

import subprocess
import shutil
import os
from typing import List, Optional

ADB_BIN = shutil.which("adb") or "/opt/homebrew/bin/adb"
DEFAULT_TARGET = "192.168.2.122:5555"

def run_adb_timeout(args: List[str], target: Optional[str] = None, timeout: float = 8.0) -> str:
    """Runs ADB command with strict execution timeout."""
    cmd = [ADB_BIN]
    if target:
        cmd.extend(["-s", target])
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
    """Returns connected ADB devices."""
    res = subprocess.run([ADB_BIN, "devices"], capture_output=True, text=True)
    lines = res.stdout.strip().splitlines()
    devs = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devs.append(parts[0])
    return devs
