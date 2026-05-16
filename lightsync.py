#!/usr/bin/env python3
"""Main sync script: capture Jingle Palette, map colors to MIDI, and send to APC mini."""
from __future__ import annotations

import argparse
import sys
import time
from typing import List, Tuple

try:
    import mido
except ImportError:
    print("Missing dependency 'mido'. Install with: pip install mido python-rtmidi")
    sys.exit(1)

from scripts.jingle_palette_colors import find_window, capture_window, sample_button_colors
from scripts.color_to_midi import get_midi_value
from scripts.apc_mini_layout import get_midi_note

# Configuration
JINGLE_WINDOW_TITLE = "Jingle Palette Reloaded"
BUTTON_ROWS = 4
BUTTON_COLS = 4
LEFT_PAD = 15
TOP_PAD = 15
BOTTOM_PAD = 235
RIGHT_PAD = 75
BUTTON_GAP = 8
SAMPLE_OFFSET_FROM_BOTTOM = 10

# MIDI output device name
MIDI_OUTPUT_PORT = "loopMIDI Port 1"

# MIDI status byte for note-on message (channel 1)
NOTE_ON = 0x96


def get_button_colors(
    window_title: str = JINGLE_WINDOW_TITLE,
    rows: int = BUTTON_ROWS,
    cols: int = BUTTON_COLS,
    button_gap: int = BUTTON_GAP,
) -> List[Tuple[int, int, Tuple[int, int, int]]]:
    """Capture and sample button colors from the Jingle Palette window.
    
    Returns:
        List of (row, col, (r, g, b)) tuples.
    """
    hwnd = find_window(window_title)
    if not hwnd:
        raise RuntimeError(f"Window not found: {window_title}")

    image = capture_window(hwnd)
    samples = sample_button_colors(
        image=image,
        rows=rows,
        cols=cols,
        left_pad=LEFT_PAD,
        top_pad=TOP_PAD,
        right_pad=RIGHT_PAD,
        bottom_pad=BOTTOM_PAD,
        sample_offset_from_bottom=SAMPLE_OFFSET_FROM_BOTTOM,
        button_gap=button_gap,
    )
    return samples


def sync_apc_lights(
    port_name: str = MIDI_OUTPUT_PORT,
    window_title: str = JINGLE_WINDOW_TITLE,
    rows: int = BUTTON_ROWS,
    cols: int = BUTTON_COLS,
    button_gap: int = BUTTON_GAP,
    verbose: bool = False,
) -> None:
    """Capture colors from Jingle Palette and send MIDI commands to APC mini.
    
    Args:
        port_name: Name of the MIDI output port.
        window_title: Window title substring to find the Jingle Palette.
        rows: Number of button rows.
        cols: Number of button columns.
        button_gap: Gap between buttons in pixels.
        verbose: Print details for each button.
    """
    # Get button colors from screenshot
    samples = get_button_colors(window_title, rows, cols, button_gap)

    # Open MIDI output port
    try:
        midi_out = mido.open_output(port_name)
    except OSError as e:
        raise RuntimeError(f"Failed to open MIDI port '{port_name}': {e}")

    # Map and send colors
    unmapped_count = 0
    sent_count = 0

    try:
        for row, col, (r, g, b) in samples:
            # Format color as hex
            color_hex = "{:02x}{:02x}{:02x}".format(r, g, b)

            # Get MIDI note for this button position
            midi_note = get_midi_note(row, col)

            # Special case: if button is playing (c0ffc0), use status byte 0x9c with red (ff0000)
            if color_hex.lower() == "c0ffc0":
                status_byte = 0x9c
                midi_value = get_midi_value("ff0000")
                if midi_value is None:
                    midi_value = 127  # fallback to max brightness for red if not mapped
            else:
                # Look up MIDI value for this color
                status_byte = NOTE_ON
                midi_value = get_midi_value(color_hex)
                if midi_value is None:
                    if verbose:
                        print(f"  row {row} col {col}: color #{color_hex} → (no mapping)")
                    unmapped_count += 1
                    continue

            # Send MIDI message as raw bytes
            data = bytes([status_byte, midi_note, midi_value])
            msg = mido.Message.from_bytes(data)
            midi_out.send(msg)
            sent_count += 1

            if verbose:
                if color_hex.lower() == "c0ffc0":
                    print(f"  row {row} col {col}: color #{color_hex} → status {hex(status_byte)} note {hex(midi_note)} velocity {midi_value} (PLAYING)")
                else:
                    print(f"  row {row} col {col}: color #{color_hex} → note {hex(midi_note)} velocity {midi_value}")
    finally:
        midi_out.close()

    # print(f"Sent {sent_count} MIDI messages ({unmapped_count} colors unmapped)")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Jingle Palette colors to APC mini lights")
    parser.add_argument("--window", type=str, default=JINGLE_WINDOW_TITLE, help="Jingle Palette window title")
    parser.add_argument("--port", type=str, default=MIDI_OUTPUT_PORT, help="MIDI output port name")
    parser.add_argument("--rows", type=int, default=BUTTON_ROWS, help="Number of button rows")
    parser.add_argument("--cols", type=int, default=BUTTON_COLS, help="Number of button columns")
    parser.add_argument("--button-gap", type=int, default=BUTTON_GAP, help="Gap between buttons in pixels")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print details for each button")
    parser.add_argument("--interval", type=float, default=0, help="Run every X seconds in background (0 = run once)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.interval > 0:
            # Run in a loop at specified interval
            print(f"Running every {args.interval} seconds (Ctrl+C to stop)...")
            try:
                while True:
                    sync_apc_lights(
                        port_name=args.port,
                        window_title=args.window,
                        rows=args.rows,
                        cols=args.cols,
                        button_gap=args.button_gap,
                        verbose=args.verbose,
                    )
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nStopped.")
                return 0
        else:
            # Run once
            sync_apc_lights(
                port_name=args.port,
                window_title=args.window,
                rows=args.rows,
                cols=args.cols,
                button_gap=args.button_gap,
                verbose=args.verbose,
            )
            return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
