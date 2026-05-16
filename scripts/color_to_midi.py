#!/usr/bin/env python3
"""Map Jingle Palette colors to MIDI note/CC values."""
from __future__ import annotations

from typing import Optional

# Color to MIDI value mapping.
# Colors are in hex format (lowercase, without '#' prefix).
COLOR_TO_MIDI = {
    "ff00ff": 53,
    "ff9acd": 56,
    "cc9aff": 52,
    "999aff": 116,
    "3366ff": 45,
    "00cdff": 37,
    "00ffff": 33,
    "33cdcd": 36,
    "339a66": 64,
    "99cd00": 111,
    "00ff00": 17,
    "ffff00": 13,
    "ffffff": 8,
    "ccffcd": 73,
    "ffcd9a": 9,
    "ff9a00": 84,
    "ffcd00": 96,
    "ffff9a": 109,
    "ccffff": 3,
    "99cdff": 36,
    "cccdff": 115,
    "f0f0f0": 0,
    "ff8181": 4,
    "ff0000": 5,
    "ff6600": 84,
}


def normalize_color(color: str) -> str:
    """Normalize a color string to lowercase hex without '#'."""
    color = color.strip()
    if color.startswith("#"):
        color = color[1:]
    return color.lower()


def get_midi_value(color: str) -> Optional[int]:
    """Look up the MIDI value for a given color.
    
    Args:
        color: Hex color string (e.g., "#ff00ff" or "ff00ff").
    
    Returns:
        The MIDI value (0-127) or None if not found.
    """
    normalized = normalize_color(color)
    return COLOR_TO_MIDI.get(normalized)


def get_midi_value_strict(color: str) -> int:
    """Look up the MIDI value for a given color, raising if not found.
    
    Args:
        color: Hex color string (e.g., "#ff00ff" or "ff00ff").
    
    Returns:
        The MIDI value (0-127).
    
    Raises:
        KeyError: If the color is not in the mapping.
    """
    normalized = normalize_color(color)
    return COLOR_TO_MIDI[normalized]


if __name__ == "__main__":
    print("Color to MIDI mapping:")
    for color, midi in sorted(COLOR_TO_MIDI.items()):
        print(f"  {color} -> {midi}")
