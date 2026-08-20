"""
BRAVIA Control CLI Entrypoint
-----------------------------
Supports CLI commands:
- bravia-control serve --port 8888 --target 192.168.2.122:5555
- bravia-control audit
- bravia-control debloat
"""

import argparse
import json
import sys
from tv_control_center.adb import run_adb_timeout, DEFAULT_TARGET

def main():
    parser = argparse.ArgumentParser(description="TV Control Center — Universal Smart TV Management Suite")
    parser.add_argument("command", nargs="?", default="serve", choices=["serve", "audit", "debloat"], help="Command to run (default: serve)")
    parser.add_argument("--port", type=int, default=8888, help="Port for web console (default: 8888)")
    parser.add_argument("--target", type=str, default=DEFAULT_TARGET, help="Target TV IP address")

    args = parser.parse_args()

    if args.command == "serve":
        from tv_control_center.server import start_server
        start_server(port=args.port, target=args.target)
    elif args.command == "audit":
        from tv_control_center.core.metrics import get_full_audit
        res = get_full_audit(args.target)
        print(json.dumps(res, indent=2))
    elif args.command == "debloat":
        from tv_control_center.core.debloat import apply_safe_debloat
        res = apply_safe_debloat(args.target)
        print("Debloat Results:", res)

if __name__ == "__main__":
    main()
