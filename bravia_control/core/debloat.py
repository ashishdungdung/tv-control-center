"""
Safe Package Debloater Subsystem Module
"""
from typing import Dict, List
from bravia_control.adb import run_adb_timeout, DEFAULT_TARGET

SAFE_TO_DISABLE = {
    "tv.samba.ssm": "Samba TV Automatic Content Recognition (ACR) Telemetry",
    "com.samba.tv": "Samba TV Interactive Tracking/Telemetry",
    "com.sony.dtv.sonybugreportsys": "Sony Bug Report System Collector",
    "com.google.android.tv.bugreportsender": "Google TV Bug Report Sender",
    "com.google.android.feedback": "Google TV User Feedback Collector",
    "com.google.android.partnersetup": "Google TV Partner OEM Ads Setup",
    "com.google.android.tvrecommendations": "Stock Android TV Home Video Ads Channel",
    "com.sony.dtv.demoapp": "Sony Store Demo Mode App",
    "com.sony.dtv.bravialifehack": "Sony Lifehack Ambient Wallpaper Engine",
    "com.sony.dtv.promos": "Sony Promotional Banners Channel",
    "com.sony.dtv.livingfit": "Sony LivingFit Ambient Service",
    "com.sony.dtv.multiscreendemo": "Sony Multi-Screen Demo Engine",
    "com.sony.dtv.smarthelp": "Sony Interactive User Help Manual",
    "com.sony.dtv.feedback": "Sony Telemetry Feedback Collector",
    "com.sony.dtv.demosupport": "Sony Demo Support Assets",
    "com.sony.dtv.demosystemsupport": "Sony Demo System Engine",
    "com.google.android.videos": "Google Play Movies & TV",
    "com.google.android.youtube.tvunplugged": "YouTube TV Stub",
    "com.google.android.play.games": "Google Play Games TV",
    "com.android.printspooler": "Android Print Spooler (Unused on TV)",
}

CAUTION_PACKAGES = {
    "com.google.android.katniss": "Google Assistant Voice Search (Keep enabled for mic search)",
    "com.google.android.tvlauncher": "Stock Android TV Launcher (Install FLauncher/Projectivy FIRST before disabling)",
    "com.sony.dtv.tvx": "Sony TV Home / Channel Bar",
    "com.sony.dtv.sonyselect": "Sony Select App Store & Recommendations",
    "com.vewd.core.service": "Vewd Web Browser Engine",
}

CRITICAL_DO_NOT_TOUCH = {
    "com.sony.dtv.hardware": "Sony TV Hardware Abstraction Layer",
    "com.sony.dtv.tvinput.hdmi": "Sony HDMI Input Switching Manager",
    "com.sony.dtv.cec": "Bravia Sync / HDMI-CEC Control",
    "com.sony.dtv.sound": "Sony Audio Engine & Sound Processing",
    "com.sony.dtv.picture": "Sony X1 4K HDR Picture Processing Engine",
    "com.sony.dtv.remote": "Sony Bluetooth Remote Controller Service",
    "com.sony.dtv.firmwareupdate": "Sony System Firmware Updater",
}

def apply_safe_debloat(target: str = DEFAULT_TARGET) -> List[str]:
    results = []
    for pkg in SAFE_TO_DISABLE:
        res = run_adb_timeout(["shell", "pm", "disable-user", "--user", "0", pkg], target, timeout=3.0)
        results.append(f"{pkg}: {res}")
    return results

def toggle_package(pkg: str, action: str, target: str = DEFAULT_TARGET) -> str:
    if action == "disable":
        return run_adb_timeout(["shell", "pm", "disable-user", "--user", "0", pkg], target, timeout=4.0)
    else:
        return run_adb_timeout(["shell", "pm", "enable", pkg], target, timeout=4.0)
