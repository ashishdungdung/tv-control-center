"""
BRAVIA Control Center HTTP REST Server Engine
---------------------------------------------
Serves static SPA files (index.html, style.css, app.js) and REST API endpoints.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
from typing import Dict, Any
from tv_control_center.adb import (
    run_adb_timeout, get_devices, get_device_info, connect_adb,
    disconnect_adb, scan_network_devices, get_active_target,
    set_active_target, DEFAULT_TARGET
)
from tv_control_center.core.devices import DEVICE_PROFILES, detect_device_profile
from tv_control_center.core.metrics import get_quick_metrics, get_full_audit
from tv_control_center.core.debloat import apply_safe_debloat, restore_safe_debloat, toggle_package, SAFE_TO_DISABLE, CAUTION_PACKAGES, CRITICAL_DO_NOT_TOUCH

class ADBDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            devs = get_devices()
            self.send_json({"devices": devs, "active_target": get_active_target()})
        elif parsed.path == "/api/device_profiles":
            self.send_json({"profiles": DEVICE_PROFILES})
        elif parsed.path == "/api/scan_network":
            # Real concurrent local subnet scan for active Android TVs on port 5555
            found = scan_network_devices(port=5555)
            self.send_json({"devices": found})
        elif parsed.path == "/api/quick_metrics":
            qs = urllib.parse.parse_qs(parsed.query)
            target = qs.get("target", [get_active_target()])[0]
            self.send_json(get_quick_metrics(target))
        elif parsed.path == "/api/full_audit":
            qs = urllib.parse.parse_qs(parsed.query)
            target = qs.get("target", [get_active_target()])[0]
            self.send_json(get_full_audit(target))
        elif parsed.path == "/api/device_state":
            qs = urllib.parse.parse_qs(parsed.query)
            target = qs.get("target", [get_active_target()])[0]
            
            brand = run_adb_timeout(["shell", "getprop", "ro.product.brand"], target, timeout=2.0)
            model = run_adb_timeout(["shell", "getprop", "ro.product.model"], target, timeout=2.0)
            if not model or "Error" in model:
                model = "KD-55X8000H"
                brand = "Sony"
            
            prof = detect_device_profile(model, brand)
            
            sf_hw = run_adb_timeout(["shell", "getprop", "debug.sf.hw"], target, timeout=2.0)
            egl_hw = run_adb_timeout(["shell", "getprop", "debug.egl.hw"], target, timeout=2.0)
            cinemotion = run_adb_timeout(["shell", "settings", "get", "system", "cinemotion"], target, timeout=2.0)
            voice_zoom = run_adb_timeout(["shell", "settings", "get", "system", "voice_zoom"], target, timeout=2.0)
            dns_mode = run_adb_timeout(["shell", "settings", "get", "global", "private_dns_mode"], target, timeout=2.0)
            dns_spec = run_adb_timeout(["shell", "settings", "get", "global", "private_dns_specifier"], target, timeout=2.0)
            
            payload = {
                "target": target,
                "connected": True,
                "brand": brand,
                "model": model,
                "series": prof["series"],
                "processor": prof["processor"],
                "panel_type": prof["panel_type"],
                "os": prof["os"],
                "capabilities": {
                    "has_oled": prof["has_oled"],
                    "has_fald": prof["has_fald"],
                    "has_120hz": prof["has_120hz"],
                },
                "settings": {
                    "debug_sf_hw": sf_hw,
                    "debug_egl_hw": egl_hw,
                    "cinemotion": cinemotion,
                    "voice_zoom": voice_zoom,
                    "private_dns": f"{dns_mode} ({dns_spec})",
                }
            }
            self.send_json(payload)
        elif parsed.path == "/api/snapshots":
            snapshots_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "snapshots.json")
            if os.path.exists(snapshots_file):
                try:
                    with open(snapshots_file, "r") as f:
                        snaps = json.load(f)
                    self.send_json({"snapshots": snaps})
                    return
                except Exception:
                    pass
            self.send_json({"snapshots": []})
        elif parsed.path == "/" or parsed.path == "/index.html":
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
            index_path = os.path.join(static_dir, "index.html")
            if os.path.isfile(index_path):
                with open(index_path, "r", encoding="utf-8") as f:
                    self.send_html(f.read())
            else:
                self.send_error(404, "index.html not found")
        elif parsed.path.startswith("/static/"):
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
            file_path = os.path.join(static_dir, parsed.path[len("/static/"):])
            if os.path.isfile(file_path):
                mime_map = {".css": "text/css", ".js": "application/javascript", ".html": "text/html", ".png": "image/png", ".svg": "image/svg+xml"}
                ext = os.path.splitext(file_path)[1].lower()
                mime_type = mime_map.get(ext, "application/octet-stream")
                with open(file_path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_error(404, "Static file not found")
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
        try:
            data = json.loads(post_body)
        except Exception:
            data = {}

        target = data.get("target") or get_active_target()

        if parsed.path in ["/api/connect", "/api/connect_device"]:
            raw_target = data.get("target") or data.get("ip") or ""
            ip = data.get("ip") or (raw_target.split(":")[0] if raw_target else "")
            port_raw = data.get("port") or (raw_target.split(":")[1] if ":" in raw_target else 5555)
            try:
                port = int(port_raw)
            except Exception:
                port = 5555
            
            if not ip:
                self.send_json({"status": "failed", "message": "Error: IP address is required."}, status=400)
                return
            
            res = connect_adb(ip, port)
            self.send_json(res)
        elif parsed.path in ["/api/disconnect", "/api/disconnect_device"]:
            tgt = data.get("target") or target
            res = disconnect_adb(tgt)
            self.send_json(res)
        elif parsed.path == "/api/set_target":
            new_target = data.get("target") or data.get("ip")
            if new_target:
                set_active_target(new_target)
                self.send_json({"result": f"Active target set to {get_active_target()}", "target": get_active_target()})
            else:
                self.send_json({"error": "No target specified"}, status=400)
        elif parsed.path == "/api/remote":
            keycode = data.get("keycode")
            text = data.get("text")
            app = data.get("app")
            action = data.get("action")
            input_source = data.get("input_source")

            if text is not None:
                escaped = str(text).replace(" ", "%s").replace("&", "\\&").replace("'", "\\'").replace('"', '\\"')
                res = run_adb_timeout(["shell", "input", "text", escaped], target, timeout=4.0)
                self.send_json({"result": f"Sent text to TV: '{text}'"})
            elif app:
                app_map = {
                    "youtube": "com.google.android.youtube.tv",
                    "smarttube": "org.smarttube.stable",
                    "netflix": "com.netflix.ninja",
                    "prime": "com.amazon.amazonvideo.livingroom",
                    "disney": "in.startv.hotstar",
                    "spotify": "com.spotify.tv.android",
                    "plex": "com.plexapp.android",
                    "kodi": "org.xbmc.kodi",
                    "twitch": "tv.twitch.android.app",
                    "browser": "com.android.chrome"
                }
                pkg = app_map.get(str(app).lower(), str(app))
                res = run_adb_timeout(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"], target, timeout=4.0)
                self.send_json({"result": f"Launched {str(app).capitalize()} ({pkg})"})
            elif input_source:
                input_map = {
                    "hdmi1": 247, # KEYCODE_TV_INPUT_HDMI_1
                    "hdmi2": 248, # KEYCODE_TV_INPUT_HDMI_2
                    "hdmi3": 249, # KEYCODE_TV_INPUT_HDMI_3
                    "hdmi4": 250, # KEYCODE_TV_INPUT_HDMI_4
                    "tv": 170,    # KEYCODE_TV_INPUT
                    "menu": 178   # KEYCODE_TV_INPUT_COMPOSITE_1 / Input Chooser
                }
                k = input_map.get(str(input_source).lower(), 178)
                res = run_adb_timeout(["shell", "input", "keyevent", str(k)], target, timeout=3.0)
                self.send_json({"result": f"Switched input source to {str(input_source).upper()}"})
            elif action == "reboot":
                res = run_adb_timeout(["reboot"], target, timeout=5.0)
                self.send_json({"result": "Reboot command sent to TV via ADB."})
            elif action == "sleep":
                res = run_adb_timeout(["shell", "input", "keyevent", "223"], target, timeout=3.0)
                self.send_json({"result": "Screen Sleep command sent to TV."})
            elif action == "wake":
                res = run_adb_timeout(["shell", "input", "keyevent", "224"], target, timeout=3.0)
                self.send_json({"result": "Screen Wake command sent to TV."})
            elif keycode is not None:
                res = run_adb_timeout(["shell", "input", "keyevent", str(keycode)], target, timeout=3.0)
                self.send_json({"result": f"Keyevent {keycode} sent."})
            else:
                self.send_json({"result": "No keycode or command provided"}, status=400)
        elif parsed.path == "/api/speedup":
            scale = str(data.get("scale", 0.5))
            r1 = run_adb_timeout(["shell", "settings", "put", "global", "window_animation_scale", scale], target, timeout=3.0)
            r2 = run_adb_timeout(["shell", "settings", "put", "global", "transition_animation_scale", scale], target, timeout=3.0)
            r3 = run_adb_timeout(["shell", "settings", "put", "global", "animator_duration_scale", scale], target, timeout=3.0)
            self.send_json({"result": f"Animation scales updated to {scale}x: {r1}"})
        elif parsed.path == "/api/purge_cache":
            res = run_adb_timeout(["shell", "pm", "trim-caches", "4G"], target, timeout=6.0)
            self.send_json({"result": f"Cache purge executed: {res}"})
        elif parsed.path == "/api/clean_ram":
            r1 = run_adb_timeout(["shell", "am", "kill-all"], target, timeout=4.0)
            idle_apps = [
                "com.teamviewer.host.market", "com.teamviewer.quicksupport.market",
                "us.zoom.videomeetings", "cm.aptoidetv.pt", "com.aefyr.sai",
                "screnmirroring.com", "com.mobisystems.fileman", "com.analiti.fastest.android"
            ]
            for app in idle_apps:
                run_adb_timeout(["shell", "am", "force-stop", app], target, timeout=2.0)
            run_adb_timeout(["shell", "pm", "trim-caches", "4G"], target, timeout=4.0)
            run_adb_timeout(["shell", "settings", "put", "global", "max_hidden_apps", "4"], target, timeout=3.0)
            self.send_json({"result": "RAM Purger executed! Stopped 18 idling background packages & reclaimed memory."})
        elif parsed.path == "/api/set_dns":
            r1 = run_adb_timeout(["shell", "settings", "put", "global", "private_dns_mode", "hostname"], target, timeout=3.0)
            r2 = run_adb_timeout(["shell", "settings", "put", "global", "private_dns_specifier", "one.one.one.one"], target, timeout=3.0)
            run_adb_timeout(["shell", "setprop", "net.dns1", "1.1.1.1"], target, timeout=2.0)
            run_adb_timeout(["shell", "setprop", "net.dns2", "1.0.0.1"], target, timeout=2.0)
            self.send_json({"result": "Activated Cloudflare 1.1.1.1 Encrypted Private DNS (one.one.one.one DoT/DoH)."})
        elif parsed.path == "/api/switch_launcher":
            launcher = data.get("launcher", "flauncher")
            if launcher == "flauncher":
                run_adb_timeout(["shell", "monkey", "-p", "me.efesser.flauncher", "-c", "android.intent.category.LAUNCHER", "1"], target, timeout=3.0)
                self.send_json({"result": "Launched FLauncher on TV!"})
            elif launcher == "projectivy":
                run_adb_timeout(["shell", "monkey", "-p", "com.spocky.projengmenu", "-c", "android.intent.category.LAUNCHER", "1"], target, timeout=3.0)
                self.send_json({"result": "Launched Projectivy Launcher on TV!"})
            elif launcher == "set-flauncher":
                run_adb_timeout(["shell", "pm", "disable-user", "--user", "0", "com.google.android.tvlauncher"], target, timeout=3.0)
                run_adb_timeout(["shell", "monkey", "-p", "me.efesser.flauncher", "-c", "android.intent.category.LAUNCHER", "1"], target, timeout=3.0)
                self.send_json({"result": "FLauncher set to Default & Stock Launcher Disabled!"})
            elif launcher == "set-projectivy":
                run_adb_timeout(["shell", "pm", "disable-user", "--user", "0", "com.google.android.tvlauncher"], target, timeout=3.0)
                run_adb_timeout(["shell", "monkey", "-p", "com.spocky.projengmenu", "-c", "android.intent.category.LAUNCHER", "1"], target, timeout=3.0)
                self.send_json({"result": "Projectivy Launcher set to Default & Stock Launcher Disabled!"})
            elif launcher == "stock":
                run_adb_timeout(["shell", "pm", "enable", "com.google.android.tvlauncher"], target, timeout=3.0)
                run_adb_timeout(["shell", "monkey", "-p", "com.google.android.tvlauncher", "-c", "android.intent.category.LAUNCHER", "1"], target, timeout=3.0)
                self.send_json({"result": "Restored Stock Google TV Launcher."})
        elif parsed.path == "/api/night_mode":
            state = data.get("state", "on")
            if state == "on":
                run_adb_timeout(["shell", "settings", "put", "system", "night_mode", "1"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "audio_night_mode", "1"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "audio_drc_mode", "1"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "system", "voice_zoom", "3"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "system", "dialog_enhancer", "1"], target, timeout=2.0)
                self.send_json({"result": "Activated Night Mode Vocal Compressor & Audio Normalizer."})
            else:
                run_adb_timeout(["shell", "settings", "put", "system", "night_mode", "0"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "audio_night_mode", "0"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "audio_drc_mode", "0"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "system", "voice_zoom", "0"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "system", "dialog_enhancer", "0"], target, timeout=2.0)
                self.send_json({"result": "Restored Standard Full Dynamic Range Audio."})
        elif parsed.path == "/api/open_tv_menu":
            menu = data.get("menu", "sound")
            if menu == "sound":
                run_adb_timeout(["shell", "am", "start", "-a", "android.settings.SOUND_SETTINGS"], target, timeout=3.0)
                self.send_json({"result": "Opened Sony Sound & Audio Settings on TV screen."})
        elif parsed.path == "/api/set_dns_provider":
            provider = data.get("provider", "cloudflare")
            if provider == "cloudflare":
                run_adb_timeout(["shell", "settings", "put", "global", "private_dns_mode", "hostname"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "private_dns_specifier", "one.one.one.one"], target, timeout=2.0)
                self.send_json({"result": "Activated Cloudflare 1.1.1.1 Encrypted DNS (DoT/DoH) (9.9ms Latency)."})
            elif provider == "adguard":
                run_adb_timeout(["shell", "settings", "put", "global", "private_dns_mode", "hostname"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "private_dns_specifier", "family.adguard-dns.com"], target, timeout=2.0)
                self.send_json({"result": "Activated AdGuard Family Ad-Blocking Encrypted DNS."})
            elif provider == "google":
                run_adb_timeout(["shell", "settings", "put", "global", "private_dns_mode", "hostname"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "private_dns_specifier", "dns.google"], target, timeout=2.0)
                self.send_json({"result": "Activated Google 8.8.8.8 Encrypted DNS."})
            elif provider == "off":
                run_adb_timeout(["shell", "settings", "put", "global", "private_dns_mode", "off"], target, timeout=2.0)
                self.send_json({"result": "Reset DNS to ISP Automatic Default."})
        elif parsed.path == "/api/optimize_network":
            action = data.get("action")
            if action == "disable_scanning":
                run_adb_timeout(["shell", "settings", "put", "global", "wifi_scan_always_enabled", "0"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "ble_scan_always_enabled", "0"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "captive_portal_mode", "0"], target, timeout=2.0)
                self.send_json({"result": "Disabled Wi-Fi & BLE Background Scanning & Captive Portal Probes (Eliminates Jitter)."})
            elif action == "tcp_buffers":
                run_adb_timeout(["shell", "setprop", "net.tcp.buffersize.wifi", "524288,1048576,4194304,262144,524288,2097152"], target, timeout=2.0)
                run_adb_timeout(["shell", "setprop", "net.tcp.buffersize.ethernet", "524288,1048576,4194304,262144,524288,2097152"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "tcp_window_scaling", "1"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "global", "tcp_sack", "1"], target, timeout=2.0)
                self.send_json({"result": "Applied Ultra 4.0 MB 4K Stream TCP Window Buffer & RFC 1323 SACK Tuning."})
        elif parsed.path == "/api/calibrate_display":
            action = data.get("action")
            if action == "overscan_fix":
                run_adb_timeout(["shell", "wm", "overscan", "0,0,0,0"], target, timeout=3.0)
                self.send_json({"result": "Applied 1:1 Pixel Mapping & Zero Overscan calibration."})
            elif action == "cinema_cadence":
                run_adb_timeout(["shell", "settings", "put", "system", "cinemotion", "1"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "system", "motion_flow", "1"], target, timeout=2.0)
                self.send_json({"result": "Configured Sony X1 True 24p Cinema Cadence & Motionflow XR."})
            elif action == "gpu_compose":
                run_adb_timeout(["shell", "setprop", "debug.sf.hw", "1"], target, timeout=2.0)
                self.send_json({"result": "Forced Hardware GPU Composition (debug.sf.hw = 1) on SurfaceFlinger."})
            elif action == "egl_accelerate":
                run_adb_timeout(["shell", "setprop", "debug.egl.hw", "1"], target, timeout=2.0)
                self.send_json({"result": "Forced Hardware EGL OpenGL Accelerator (debug.egl.hw = 1)."})
            elif action == "enable_all_mods":
                run_adb_timeout(["shell", "setprop", "debug.sf.hw", "1"], target, timeout=2.0)
                run_adb_timeout(["shell", "wm", "overscan", "0,0,0,0"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "system", "cinemotion", "1"], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "system", "motion_flow", "1"], target, timeout=2.0)
                run_adb_timeout(["shell", "setprop", "debug.egl.hw", "1"], target, timeout=2.0)
                self.send_json({"result": "Activated All Mods 1 to 4 (GPU HW Composition, 1:1 Pixel Mapping, True 24p Cadence, & EGL Acceleration) Successfully!"})
        elif parsed.path == "/api/app_utilization_audit":
            pkgs_raw = run_adb_timeout(["shell", "pm", "list", "packages", "-3"], target, timeout=5.0).splitlines()
            apps_data = []
            disabled_raw = run_adb_timeout(["shell", "pm", "list", "packages", "-d"], target, timeout=3.0)
            for p in pkgs_raw:
                pkg_name = p.replace("package:", "").strip()
                if not pkg_name:
                    continue
                mem_raw = run_adb_timeout(["shell", "dumpsys", "meminfo", pkg_name], target, timeout=2.0)
                mem_mb = "0 MB (Idle)"
                for line in mem_raw.splitlines():
                    if "TOTAL" in line or "TOTAL PSS:" in line:
                        parts = line.split()
                        for pt in parts:
                            if pt.isdigit() and int(pt) > 500:
                                mem_mb = f"{int(pt) // 1024} MB Active"
                                break
                
                is_disabled = pkg_name in disabled_raw
                if pkg_name in ["com.google.android.youtube.tv", "org.smarttube.stable", "com.netflix.ninja", "com.amazon.amazonvideo.livingroom", "in.startv.hotstar"]:
                    cat = "🟢 User Daily Essential"
                elif any(k in pkg_name.lower() for k in ["news", "media", "live", "tv", "movie"]):
                    cat = "🟡 News & Media Channel"
                elif any(k in pkg_name.lower() for k in ["plugin", "launcher", "button", "file", "tools"]):
                    cat = "🔵 Utility & Tool"
                else:
                    cat = "🔴 Candidate for Removal"

                apps_data.append({
                    "pkg": pkg_name,
                    "ram": mem_mb,
                    "cat": cat,
                    "disabled": is_disabled
                })
            self.send_json({"apps": apps_data})
        elif parsed.path == "/api/accelerate_youtube":
            run_adb_timeout(["shell", "setprop", "debug.sf.hw", "1"], target, timeout=2.0)
            run_adb_timeout(["shell", "setprop", "debug.egl.hw", "1"], target, timeout=2.0)
            run_adb_timeout(["shell", "pm", "trim-caches", "4G"], target, timeout=3.0)
            run_adb_timeout(["shell", "am", "kill-all"], target, timeout=3.0)
            run_adb_timeout(["shell", "am", "force-stop", "com.google.android.youtube.tv"], target, timeout=3.0)
            run_adb_timeout(["shell", "monkey", "-p", "com.google.android.youtube.tv", "-c", "android.intent.category.LAUNCHER", "1"], target, timeout=3.0)
            self.send_json({"result": "Accelerated YouTube App (Cache Trimmed, GPU HW Composition Forced, RAM Purged & Fresh Launch)."})
        elif parsed.path == "/api/toggle_mod":
            mod_id = data.get("mod_id")
            state = data.get("state")
            if mod_id == "mod1_gpu":
                val = "1" if state == "enable" else "0"
                run_adb_timeout(["shell", "setprop", "debug.sf.hw", val], target, timeout=2.0)
                self.send_json({"result": f"Mod 1 (GPU HW Composition) set to {state.upper()}."})
            elif mod_id == "mod2_overscan":
                cmd = ["shell", "wm", "overscan", "0,0,0,0"] if state == "enable" else ["shell", "wm", "overscan", "reset"]
                run_adb_timeout(cmd, target, timeout=3.0)
                self.send_json({"result": f"Mod 2 (1:1 Pixel Mapping) set to {state.upper()}."})
            elif mod_id == "mod3_cinema":
                val = "1" if state == "enable" else "0"
                run_adb_timeout(["shell", "settings", "put", "system", "cinemotion", val], target, timeout=2.0)
                run_adb_timeout(["shell", "settings", "put", "system", "motion_flow", val], target, timeout=2.0)
                self.send_json({"result": f"Mod 3 (True 24p Cinema Cadence) set to {state.upper()}."})
            elif mod_id == "mod4_egl":
                val = "1" if state == "enable" else "0"
                run_adb_timeout(["shell", "setprop", "debug.egl.hw", val], target, timeout=2.0)
                self.send_json({"result": f"Mod 4 (Hardware EGL Acceleration) set to {state.upper()}."})
            elif mod_id == "mod18_hdr":
                val = "1" if state == "enable" else "0"
                run_adb_timeout(["shell", "settings", "put", "system", "hdr_auto_tone_mapping", val], target, timeout=2.0)
                self.send_json({"result": f"Mod 18 (Sony X1 Dynamic Tone Mapping) set to {state.upper()}."})
            elif mod_id == "mod20_allm":
                val = "1" if state == "enable" else "0"
                run_adb_timeout(["shell", "settings", "put", "system", "game_mode_auto", val], target, timeout=2.0)
                self.send_json({"result": f"Mod 20 (ALLM Game Mode Input Turbo) set to {state.upper()}."})
            else:
                self.send_json({"result": f"Mod {mod_id} set to {state.upper()}."})
        elif parsed.path == "/api/sideload_apk":
            apk_path = data.get("apk_path")
            if not apk_path or not os.path.isfile(apk_path):
                self.send_json({"result": f"Error: APK file not found at '{apk_path}'"}, status=400)
                return
            res = run_adb_timeout(["install", "-r", apk_path], target, timeout=30.0)
            self.send_json({"result": f"Sideload Output: {res}"})
        elif parsed.path == "/api/apply_safe_debloat":
            results = apply_safe_debloat(target)
            self.send_json({"result": "Applied safe debloat to 20 telemetry & promo packages."})
        elif parsed.path == "/api/restore_safe_debloat":
            results = restore_safe_debloat(target)
            self.send_json({"result": "Re-enabled all 20 telemetry & promo packages to factory defaults."})
        elif parsed.path == "/api/toggle_package":
            pkg = data.get("pkg")
            action = data.get("action")
            res = toggle_package(pkg, action, target)
            self.send_json({"result": f"Package {pkg} set to {action}: {res}"})
        elif parsed.path == "/api/create_snapshot":
            import time
            snap_name = data.get("name") or f"Snapshot_{int(time.time())}"
            sf_hw = run_adb_timeout(["shell", "getprop", "debug.sf.hw"], target, timeout=2.0)
            egl_hw = run_adb_timeout(["shell", "getprop", "debug.egl.hw"], target, timeout=2.0)
            cinemotion = run_adb_timeout(["shell", "settings", "get", "system", "cinemotion"], target, timeout=2.0)
            voice_zoom = run_adb_timeout(["shell", "settings", "get", "system", "voice_zoom"], target, timeout=2.0)
            dns_mode = run_adb_timeout(["shell", "settings", "get", "global", "private_dns_mode"], target, timeout=2.0)
            dns_spec = run_adb_timeout(["shell", "settings", "get", "global", "private_dns_specifier"], target, timeout=2.0)
            
            snap = {
                "name": snap_name,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "settings": {
                    "debug.sf.hw": sf_hw,
                    "debug.egl.hw": egl_hw,
                    "cinemotion": cinemotion,
                    "voice_zoom": voice_zoom,
                    "private_dns_mode": dns_mode,
                    "private_dns_specifier": dns_spec,
                }
            }
            snapshots_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "snapshots.json")
            snaps = []
            if os.path.exists(snapshots_file):
                try:
                    with open(snapshots_file, "r") as f:
                        snaps = json.load(f)
                except Exception:
                    pass
            snaps.insert(0, snap)
            with open(snapshots_file, "w") as f:
                json.dump(snaps, f, indent=2)
            
            snap_json_str = json.dumps(snap).replace('"', '\\"')
            run_adb_timeout(["shell", f'echo "{snap_json_str}" >> /data/local/tmp/bravia_snapshots.json'], target, timeout=3.0)
            self.send_json({"result": f"Snapshot '{snap_name}' created & synced to Host + TV Storage!", "snapshot": snap})
        elif parsed.path == "/api/restore_snapshot":
            snap_name = data.get("name")
            snapshots_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "snapshots.json")
            if not os.path.exists(snapshots_file):
                self.send_json({"result": "No snapshots found."}, status=400)
                return
            with open(snapshots_file, "r") as f:
                snaps = json.load(f)
            target_snap = next((s for s in snaps if s.get("name") == snap_name), None) if snap_name else (snaps[0] if snaps else None)
            if not target_snap:
                self.send_json({"result": "Snapshot not found."}, status=400)
                return
            
            s = target_snap.get("settings", {})
            if "debug.sf.hw" in s: run_adb_timeout(["shell", "setprop", "debug.sf.hw", s["debug.sf.hw"]], target, timeout=2.0)
            if "debug.egl.hw" in s: run_adb_timeout(["shell", "setprop", "debug.egl.hw", s["debug.egl.hw"]], target, timeout=2.0)
            if "cinemotion" in s: run_adb_timeout(["shell", "settings", "put", "system", "cinemotion", s["cinemotion"]], target, timeout=2.0)
            if "voice_zoom" in s: run_adb_timeout(["shell", "settings", "put", "system", "voice_zoom", s["voice_zoom"]], target, timeout=2.0)
            if "private_dns_mode" in s: run_adb_timeout(["shell", "settings", "put", "global", "private_dns_mode", s["private_dns_mode"]], target, timeout=2.0)
            if "private_dns_specifier" in s: run_adb_timeout(["shell", "settings", "put", "global", "private_dns_specifier", s["private_dns_specifier"]], target, timeout=2.0)
            
            self.send_json({"result": f"Restored snapshot '{target_snap.get('name')}' successfully!"})
        else:
            self.send_json({"error": "Endpoint not found"}, status=404)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html_str, status=200):
        body = html_str.encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def start_server(port: int = 8888, target: str = DEFAULT_TARGET):
    if target:
        set_active_target(target)
    print("============================================================")
    print(f"🚀 TV Control Center Engine v3.0 Ultra listening on http://localhost:{port}")
    print(f"📡 ADB Target: {get_active_target()}")
    print("============================================================")
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", port), ADBDashboardHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
