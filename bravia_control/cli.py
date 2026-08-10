"""
BRAVIA Control CLI Entrypoint
-----------------------------
Supports CLI commands:
- bravia-control serve --port 8888 --target 192.168.2.122:5555
- bravia-control audit
- bravia-control debloat
"""

import argparse
import sys
from bravia_control.adb import run_adb_timeout, DEFAULT_TARGET

def main():
    parser = argparse.ArgumentParser(description="BRAVIA Control Center v3.0 Ultra")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Launch BRAVIA Control Center HTTP Web Console")
    serve_parser.add_argument("--port", type=int, default=8888, help="Port to serve web console (default: 8888)")
    serve_parser.add_argument("--target", type=str, default=DEFAULT_TARGET, help="Target TV IP address (default: 192.168.2.122:5555)")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run deep hardware audit over ADB")
    audit_parser.add_argument("--target", type=str, default=DEFAULT_TARGET, help="Target TV IP address")

    # Debloat command
    debloat_parser = subparsers.add_parser("debloat", help="Apply 20-package safe debloat profile over ADB")
    debloat_parser.add_argument("--target", type=str, default=DEFAULT_TARGET, help="Target TV IP address")

    args = parser.parse_args()

    if args.command == "serve" or args.command is None:
        port = getattr(args, "port", 8888)
        target = getattr(args, "target", DEFAULT_TARGET)
        from bravia_control.server import start_server
        start_server(port=port, target=target)
    elif args.command == "audit":
        from bravia_control.core.metrics import get_full_audit
        res = get_full_audit(args.target)
        import json
        print(json.dumps(res, indent=2))
    elif args.command == "debloat":
        from bravia_control.core.debloat import apply_safe_debloat
        res = apply_safe_debloat(args.target)
        print("Debloat Results:", res)

if __name__ == "__main__":
    main()
