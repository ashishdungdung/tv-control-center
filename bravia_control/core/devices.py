"""
Universal Multi-TV & Device Profiles Database
----------------------------------------------
Hardware definitions, panel types, SoC profiles, and capabilities matrix
for Sony BRAVIA, NVIDIA SHIELD, TCL, Hisense, Xiaomi, and Chromecast devices.
"""

from typing import Dict, Any, List

DEVICE_PROFILES = {
    # ── SONY BRAVIA SERIES ────────────────────────────────────────
    "sony_x80h": {
        "brand": "Sony",
        "series": "BRAVIA X80H / X8000H",
        "models": ["KD-43X8000H", "KD-49X8000H", "KD-55X8000H", "KD-65X8000H", "KD-75X8000H", "KD-85X8000H"],
        "processor": "Sony X1 4K HDR Processor (MediaTek MT5893 Quad-Core @ 1.5 GHz)",
        "panel_type": "Direct LED VA LCD (60Hz)",
        "audio_engine": "Sony DSEE + Voice Zoom + Dolby Atmos",
        "os": "Android 10 Q",
        "has_oled": False,
        "has_fald": False,
        "has_120hz": False,
    },
    "sony_x90h": {
        "brand": "Sony",
        "series": "BRAVIA X90H / X9000H / X90J / X90K / X90L",
        "models": ["KD-55X9000H", "KD-65X9000H", "KD-75X9000H", "XR-55X90J", "XR-65X90K", "XR-75X90L"],
        "processor": "Sony Cognitive Processor XR / X1 Ultimate (MediaTek MT5895 / Pentonic 1000)",
        "panel_type": "Full Array Local Dimming (FALD) VA LCD (120Hz VRR)",
        "audio_engine": "Acoustic Multi-Audio + Dolby Atmos + DTS:X",
        "os": "Android 10 / Google TV",
        "has_oled": False,
        "has_fald": True,
        "has_120hz": True,
    },
    "sony_a8h_oled": {
        "brand": "Sony",
        "series": "BRAVIA OLED A8H / A80J / A80K / A80L / A95L",
        "models": ["KD-55A8H", "KD-65A8H", "XR-55A80J", "XR-65A80K", "XR-77A80L", "XR-65A95L QD-OLED"],
        "processor": "Sony Cognitive Processor XR (Master Series)",
        "panel_type": "OLED / QD-OLED (120Hz Self-Emissive)",
        "audio_engine": "Acoustic Surface Audio+ (Screen Vibrating Actuators)",
        "os": "Android 10 / Google TV",
        "has_oled": True,
        "has_fald": False,
        "has_120hz": True,
    },

    # ── NVIDIA SHIELD TV ──────────────────────────────────────────
    "nvidia_shield_pro": {
        "brand": "NVIDIA",
        "series": "SHIELD TV / SHIELD TV Pro (2017 / 2019)",
        "models": ["P2897", "P3430"],
        "processor": "NVIDIA Tegra X1+ (256-core Maxwell GPU)",
        "panel_type": "External Streaming Console",
        "audio_engine": "Dolby TrueHD Atmos / DTS-HD Master Audio Passthrough",
        "os": "Android 11 (SHIELD Experience 9.1)",
        "has_oled": False,
        "has_fald": False,
        "has_120hz": True,
    },

    # ── TCL SMART TV ──────────────────────────────────────────────
    "tcl_qled_c835": {
        "brand": "TCL",
        "series": "TCL Mini-LED QLED C835 / C845 / QM8",
        "models": ["55C835", "65C835", "75C845", "65QM850G"],
        "processor": "AiPQ Engine 3.0 (MediaTek MT9615 / Realtek RTD2851)",
        "panel_type": "Mini-LED QLED (144Hz VRR)",
        "audio_engine": "Onkyo 2.1 Soundbar + Dolby Atmos",
        "os": "Google TV (Android 11 / 12)",
        "has_oled": False,
        "has_fald": True,
        "has_120hz": True,
    },

    # ── HISENSE SMART TV ──────────────────────────────────────────
    "hisense_u8k": {
        "brand": "Hisense",
        "series": "Hisense U6K / U7K / U8K / U8N ULED",
        "models": ["55U8K", "65U8K", "75U8K", "65U8N"],
        "processor": "Hi-View Engine Pro (Amlogic S905X4)",
        "panel_type": "Mini-LED ULED (144Hz VRR)",
        "audio_engine": "Subwoofer Integrated 2.1.2ch Dolby Atmos",
        "os": "Google TV (Android 11)",
        "has_oled": False,
        "has_fald": True,
        "has_120hz": True,
    },

    # ── CHROMECAST & GOOGLE TV ─────────────────────────────────────
    "chromecast_google_tv": {
        "brand": "Google",
        "series": "Chromecast with Google TV (HD/4K) & Google TV Streamer 4K",
        "models": ["GA01919-US", "Google TV Streamer"],
        "processor": "Amlogic S905X3 / MediaTek MT8696",
        "panel_type": "Streaming Dongle / Hub",
        "audio_engine": "Dolby Digital Plus / Atmos Passthrough",
        "os": "Google TV (Android 12 / 14)",
        "has_oled": False,
        "has_fald": False,
        "has_120hz": False,
    },

    # ── XIAOMI TV ──────────────────────────────────────────────────
    "xiaomi_mi_box": {
        "brand": "Xiaomi",
        "series": "Mi Box S 4K / Mi TV Stick 4K / Xiaomi TV Q2",
        "models": ["MDZ-22-AB", "MDZ-27-AA", "Xiaomi TV Q2 55"],
        "processor": "Amlogic S905X2 / S905Y4",
        "panel_type": "Streaming Dongle / QLED TV",
        "audio_engine": "Dolby Audio + DTS HD",
        "os": "Android TV 11",
        "has_oled": False,
        "has_fald": False,
        "has_120hz": False,
    },

    # ── PHILIPS AMBILIGHT TV ───────────────────────────────────────
    "philips_ambilight_oled": {
        "brand": "Philips",
        "series": "Philips Ambilight OLED807 / OLED808 / PUS8808 (The One)",
        "models": ["55OLED807", "65OLED808", "55PUS8808"],
        "processor": "P5 AI Perfect Picture Engine (MediaTek MT9970)",
        "panel_type": "OLED / 120Hz DLED (Ambilight 4-sided)",
        "audio_engine": "Bowers & Wilkins 2.1 Sound + Dolby Atmos",
        "os": "Google TV (Android 12)",
        "has_oled": True,
        "has_fald": False,
        "has_120hz": True,
    },

    # ── PANASONIC SMART TV ─────────────────────────────────────────
    "panasonic_hcx_oled": {
        "brand": "Panasonic",
        "series": "Panasonic Master OLED LZ1500 / MZ2000 / MX950 Mini-LED",
        "models": ["TX-55LZ1500", "TX-65MZ2000", "55MX950"],
        "processor": "HCX Pro AI Processor (MediaTek MT9612)",
        "panel_type": "Master OLED Pro Cinema (120Hz)",
        "audio_engine": "360° Soundscape Pro Tuned by Technics",
        "os": "Google TV (Android 11)",
        "has_oled": True,
        "has_fald": True,
        "has_120hz": True,
    },

    # ── SHARP AQUOS TV ─────────────────────────────────────────────
    "sharp_aquos_4k": {
        "brand": "Sharp",
        "series": "Sharp AQUOS 4K EQ1 / DN1 Series",
        "models": ["4T-C50DN1", "4T-C65EQ1"],
        "processor": "X4 Revelation Processor",
        "panel_type": "Deep Chroma Display VA LCD (60Hz / 120Hz)",
        "audio_engine": "HARMAN/KARDON Sound System",
        "os": "Android TV 11",
        "has_oled": False,
        "has_fald": False,
        "has_120hz": False,
    },

    # ── VU GLOLED & MASTERPIECE TV ────────────────────────────────
    "vu_glo_led": {
        "brand": "Vu",
        "series": "Vu GloLED 4K / Masterpiece QLED Series",
        "models": ["55GloLED", "65GloLED", "55Masterpiece"],
        "processor": "Vu Glo Processor 400 nits Brightness",
        "panel_type": "Glo Panel (84% NTSC Wide Color)",
        "audio_engine": "Built-in 104W DJ Subwoofer Soundbar",
        "os": "Google TV (Android 11)",
        "has_oled": False,
        "has_fald": False,
        "has_120hz": False,
    },

    # ── AMAZON FIRE TV CUBE & STICK ────────────────────────────────
    "amazon_fire_tv_cube": {
        "brand": "Amazon",
        "series": "Fire TV Cube (3rd Gen) / Fire TV Stick 4K Max",
        "models": ["Amulet", "KFTTR", "KFAUWI"],
        "processor": "Octa-Core 2.0 GHz (Amlogic POP1-G / MediaTek MT8696T)",
        "panel_type": "Streaming Media Player Hub",
        "audio_engine": "Dolby Atmos / DTS-HD Passthrough",
        "os": "Fire OS 7 / 8 (Android 9/11 Base)",
        "has_oled": False,
        "has_fald": False,
        "has_120hz": False,
    },

    # ── SOUTH KOREA & MIDDLE EAST EXPANSION ───────────────────────
    "lg_oled_companion": {
        "brand": "LG",
        "series": "LG OLED C2 / C3 / G3 / G4 & Android TV Companion",
        "models": ["OLED55C2", "OLED65C3", "OLED77G4"],
        "processor": "LG Alpha 9 Gen 6 / Gen 7 AI Processor",
        "panel_type": "WOLED / MLA OLED (120Hz / 144Hz VRR)",
        "audio_engine": "AI Sound Pro 9.1.2 Virtual Surround",
        "os": "webOS / Android ADB Bridge",
        "has_oled": True,
        "has_fald": False,
        "has_120hz": True,
    },
    "arab_me_bravia": {
        "brand": "Sony Middle East & North Africa",
        "series": "Sony BRAVIA KSA / UAE / Egypt Special Edition",
        "models": ["KD-65X85K-MENA", "XR-75X90K-ME"],
        "processor": "Sony Cognitive Processor XR (Arabic Subtitles & OS Native)",
        "panel_type": "FALD / OLED 120Hz",
        "audio_engine": "Acoustic Surface Audio+ / Atmos",
        "os": "Google TV (Arabic / MENA Regional Build)",
        "has_oled": False,
        "has_fald": True,
        "has_120hz": True,
    }
}

def detect_device_profile(model_name: str, brand_name: str) -> Dict[str, Any]:
    """Detects matching device profile or creates dynamic profile."""
    model_upper = model_name.upper()
    brand_upper = brand_name.upper()

    for key, prof in DEVICE_PROFILES.items():
        if prof["brand"].upper() in brand_upper:
            for m in prof["models"]:
                if m.upper() in model_upper or model_upper in m.upper():
                    return prof

    # Fallback dynamic profile
    return {
        "brand": brand_name or "Android TV",
        "series": f"Generic {brand_name} {model_name}",
        "models": [model_name],
        "processor": "Generic Android TV ARM Processor",
        "panel_type": "Standard Display Panel",
        "audio_engine": "Android Audio HAL",
        "os": "Android TV OS",
        "has_oled": "OLED" in model_upper,
        "has_fald": False,
        "has_120hz": False,
    }
