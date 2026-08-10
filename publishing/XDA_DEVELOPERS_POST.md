# [APP][TOOL][4K][OPEN-SOURCE] BRAVIA Control Center v3.0 Ultra – Desktop Power-User Console for Sony BRAVIA Android TVs

Hey XDA Community! 👋

I'm excited to share **BRAVIA Control Center v3.0 Ultra** — an open-source, zero-cloud desktop web application designed to manage, debloat, tune, and optimize Sony BRAVIA Android TVs over wireless ADB.

### 🌟 Why I Built This
Stock Sony BRAVIA Android TVs (especially MediaTek MT5893 / MT5891 series) often suffer from background RAM pressure, Samba TV tracking overhead, stock launcher video ad recommendation lag, and judder on 24fps film playback. BRAVIA Control Center gives you a full desktop hardware console to tune display/audio pipelines and safely debloat unwanted services without touching root.

---

### ⚡ Key Features
- **🗂 Persistent Sidebar Navigation:** Overview, Performance, Display, Audio, Network, Apps, Launcher, Remote, Hardware, Activity Timeline, Settings.
- **🎛 Simple / Advanced Mode Toggle:** Hide complex property tweaks (`debug.sf.hw`, `tcp_window_scaling`) from casual users while retaining full power-user overrides.
- **🔍 Command Palette (`⌘K` / `Ctrl+K`):** Global fuzzy-search modal palette for instant actions.
- **🛡️ 20-Package Safe Debloater:** 1-click disable for Samba TV ACR tracking (`tv.samba.ssm`), Sony bug report collectors, Google TV partner ad setups, and store demo apps.
- **📱 Live App Utilization Telemetry:** Audit all 52+ installed apps, view live PSS memory footprints, and disable idling apps with 1 click.
- **🚀 Hardware & Picture Engine Tweaks:**
  - **Mod 1:** GPU SurfaceFlinger Hardware Composition (`debug.sf.hw = 1`)
  - **Mod 2:** 1:1 Pixel Mapping & Zero Overscan Calibration (`wm overscan 0,0,0,0`)
  - **Mod 3:** True 24p Cinema Cadence Matching (`cinemotion = 1`, `motion_flow = 1`)
  - **Mod 4:** Hardware EGL OpenGL Acceleration (`debug.egl.hw = 1`)
  - **Mod 18:** Sony X1 HDR Dynamic Tone Mapping (`hdr_auto_tone_mapping = 1`)
  - **Mod 19:** Sony DSEE Audio Harmonics Recovery (`sound_effect_mode = 1`)
  - **Mod 20:** ALLM Game Mode Input Lag Turbo (18.5 ms Latency)
- **🌐 Network & TCP Stack Overrides:**
  - Ultra 4.0 MB TCP Receive Buffer Vector (`net.tcp.buffersize.wifi`)
  - TCP Initial Window Boost (`default_init_rwnd = 60` segments)
  - Cloudflare Encrypted DNS (`one.one.one.one` DoT/DoH)
  - Wi-Fi Disconnect Watchdog Suppression (`wifi_watchdog_on = 0`)
- **📸 Multi-Tier Snapshot & Restore System:** Save & restore configuration snapshots across Host JSON, Browser LocalStorage, and On-TV Flash Storage (`/data/local/tmp/`).
- **📦 APK Drag-and-Drop Sideloader:** Sideload APK files directly to your TV by dropping them onto your desktop browser window.

---

### 🚀 How to Install & Run

#### Option 1: Via Pip (PyPI)
```bash
pip install bravia-control
bravia-control serve --port 8888 --target 192.168.2.122:5555
```

#### Option 2: Via Docker / Unraid / TrueNAS
```bash
docker run -d --name tv-control-center -p 8888:8888 ashishdungdung/tv-control-center:latest
```

**Run from Source Code:**
```bash
git clone https://github.com/ashishdungdung/tv-control-center.git
cd tv-control-center
python3 -m bravia_control serve --port 8888
```

[SIZE=4][B]Links & Repository[/B][/SIZE]
* **GitHub Repository:** [URL]https://github.com/ashishdungdung/tv-control-center[/URL]

---

### ⚖️ Legal, Warranty & Liability Disclaimer
**No Warranty & Limitation of Liability:** This tool is provided "AS IS" and "AS AVAILABLE" under the MIT License without warranty of any kind. Under no circumstances shall the author or contributors be liable for any direct, indirect, incidental, or consequential damages (including boot-loops, soft-bricking, device malfunction, data loss, or warranty voidance). All ADB overrides and package modifications are executed at your sole risk and discretion.

*Trademark Release: BRAVIA® is a registered trademark of Sony Group Corporation. Android TV™, Google Play™, and YouTube™ are trademarks of Google LLC. This project is an independent open-source utility and is not affiliated with, endorsed by, or sponsored by Sony or Google.*
