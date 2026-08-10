# [OC] I built BRAVIA Control Center — an open-source desktop console to debloat, speed up, and tune Sony BRAVIA Android TVs wirelessly over ADB

Hey r/bravia & r/AndroidTV!

If you own a Sony BRAVIA TV (especially models like the X800H, X900H, X85J, X90J, etc.), you might have noticed the stock launcher getting laggy, recommendation video ads taking up RAM, or Samba TV background tracking running silently.

To solve this, I built **BRAVIA Control Center v3.0 Ultra** — an open-source, zero-cloud desktop web console that connects wirelessly to your TV over ADB and lets you manage, tune, and optimize everything from your laptop browser.

### 🎬 What it does:

1. **🚀 1-Click Optimizations:**
   - Purge RAM & trim caches without rebooting.
   - Force 60fps GPU Hardware SurfaceFlinger composition (`debug.sf.hw = 1`).
   - Enable 1:1 Pixel Mapping (removes ugly overscan scaling).
   - Enable True 24p Cinema Cadence (smooth 5:5 pulldown for movies).
   - Enable Sony X1 Dynamic HDR Tone Mapping & DSEE Audio Harmonics Recovery.

2. **🛡️ Safe Telemetry & Ads Debloater:**
   - 1-click disable for Samba TV ACR tracking (`tv.samba.ssm`), Sony bug report collectors, Google partner ad setup, and store demo stubs.
   - Live PSS Memory Telemetry for all 52+ installed apps so you can see which apps are hogging RAM.

3. **🚀 Launcher Switcher:**
   - Automatically switch to Projectivy Launcher or FLauncher as default and disable stock Google TV launcher ads (reclaiming ~150–200 MB RAM).

4. **🌐 4K Network & TCP Tuning:**
   - Boost TCP Window Buffers to 4.0 MB for 0% buffering on 4K streams.
   - Set Cloudflare 1.1.1.1 Encrypted DNS (DoT) to eliminate DNS tracking and drops.
   - Suppress background Wi-Fi/BLE location probes.

5. **🎮 Virtual Remote & Keyboard Shortcuts:**
   - Desktop D-Pad, Volume, Home, Back controls + `⌘K` Command Palette.

6. **📸 Multi-Tier Snapshot & Restore:**
   - Backup TV settings locally to your laptop, browser, or directly to TV flash storage (`/data/local/tmp/`).

---

### 💻 How to try it out:

You can launch it via Pip:
```bash
pip install bravia-control
bravia-control serve --port 8888
```

Or via Docker / Unraid:
```bash
docker run -d --name bravia-control -p 8888:8888 anumac/bravia-control-center:latest
```

Or run the Python code directly:
```bash
git clone https://github.com/anumac/SonyTV.git
cd SonyTV && python3 dashboard.py
```
Open **`http://localhost:8888`** in your browser!

### 📄 Links & Open Source
- **GitHub Repo:** https://github.com/anumac/SonyTV (MIT Licensed)
- Feedback, bug reports, and PRs are super welcome! Let me know how it works on your BRAVIA model!

---

### ⚖️ Legal, Warranty & Liability Disclaimer
**No Warranty & Limitation of Liability:** This tool is provided "AS IS" and "AS AVAILABLE" under the MIT License without warranty of any kind. Under no circumstances shall the author or contributors be held liable for any direct, indirect, incidental, or consequential damages (including boot-loops, soft-bricking, device malfunction, data loss, or warranty voidance). All ADB overrides and package modifications are executed at your sole risk and discretion.

*Trademark Release: BRAVIA® is a registered trademark of Sony Group Corporation. Android TV™, Google Play™, and YouTube™ are trademarks of Google LLC. This project is an independent open-source utility and is not affiliated with, endorsed by, or sponsored by Sony or Google.*
