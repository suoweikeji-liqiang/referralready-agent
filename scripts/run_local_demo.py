#!/usr/bin/env python3
"""Run a local ReferralReady demo without MCP."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.tools import build_referral_packet

def main() -> int:
    parser = argparse.ArgumentParser(description="ReferralReady local demo")
    parser.add_argument("--patient", default="SYN-CKD-001", help="Synthetic patient ID")
    parser.add_argument("--specialty", default="nephrology", help="Referral specialty")
    parser.add_argument("--reason", default=None, help="Optional referral reason override")
    args = parser.parse_args()
    packet = build_referral_packet(args.patient, args.specialty, args.reason)
    print(packet["markdown"])
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
