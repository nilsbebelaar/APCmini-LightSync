#!/usr/bin/env python3
"""Simple MIDI test tool to list outputs and send raw bytes.

Usage:
  python scripts/midi_test.py --list
  python scripts/midi_test.py --port "loopback Midi" --send

Set DEVICE_NAME at top to change default.
"""
from __future__ import annotations

import argparse
import sys
from typing import List

try:
    import mido
except Exception:
    print("Missing dependency 'mido'. Install with: pip install mido python-rtmidi")
    raise

# Default device name (override via --port)
DEVICE_NAME = "loopMIDI Port 1"


def list_outputs() -> List[str]:
    return mido.get_output_names()


def send_raw_bytes(port_name: str, data: bytes) -> None:
    outputs = list_outputs()
    if port_name not in outputs:
        raise ValueError(f"Port '{port_name}' not found. Available: {outputs}")

    with mido.open_output(port_name) as out:
        msg = mido.Message.from_bytes(data)
        out.send(msg)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MIDI test: list ports and send raw MIDI bytes")
    parser.add_argument("--list", action="store_true", help="List available MIDI output ports")
    parser.add_argument("--port", type=str, default=DEVICE_NAME, help="MIDI output port name")
    parser.add_argument("--send", action="store_true", help="Send test bytes to the selected port")
    args = parser.parse_args(argv)

    if args.list:
        for p in list_outputs():
            print(p)
        return 0

    if args.send:
        data = bytes([0x9b, 0x38, 84])
        try:
            send_raw_bytes(args.port, data)
            print(f"Sent bytes {data.hex(' ')} to '{args.port}'")
        except Exception as e:
            print("Error sending MIDI bytes:", e)
            return 2
    else:
        print("No action specified. Use --list or --send. Use --help for details.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
