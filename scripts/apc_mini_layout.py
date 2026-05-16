#!/usr/bin/env python3
"""APC mini button layout and MIDI note mapping."""
from __future__ import annotations

from typing import Tuple

# APC mini button layout: 8 rows × 8 columns
# Each row has a base MIDI note address, and columns are offsets within that row.
APC_MINI_ROWS = 8
APC_MINI_COLS = 8

# Row base addresses (MIDI note values in hex).
# Rows are numbered top-to-bottom: row 0 is the top row.
APC_MINI_ROW_BASES = [
    0x38,  # row 0: 0x38 - 0x3f
    0x30,  # row 1: 0x30 - 0x37
    0x28,  # row 2: 0x28 - 0x2f
    0x20,  # row 3: 0x20 - 0x27
    0x18,  # row 4: 0x18 - 0x1f
    0x10,  # row 5: 0x10 - 0x17
    0x08,  # row 6: 0x08 - 0x0f
    0x00,  # row 7: 0x00 - 0x07
]


def get_midi_note(row: int, col: int) -> int:
    """Get the MIDI note (0-127) for a button at (row, col).
    
    Args:
        row: Row index (0-7, top-to-bottom).
        col: Column index (0-7, left-to-right).
    
    Returns:
        MIDI note value (0-127).
    
    Raises:
        IndexError: If row or col is out of bounds.
    """
    if not (0 <= row < APC_MINI_ROWS):
        raise IndexError(f"Row {row} out of range [0, {APC_MINI_ROWS-1}]")
    if not (0 <= col < APC_MINI_COLS):
        raise IndexError(f"Column {col} out of range [0, {APC_MINI_COLS-1}]")
    
    base = APC_MINI_ROW_BASES[row]
    note = base + col
    return note


def get_row_col_from_note(note: int) -> Tuple[int, int]:
    """Reverse lookup: get (row, col) from a MIDI note.
    
    Args:
        note: MIDI note value (0-127).
    
    Returns:
        Tuple of (row, col).
    
    Raises:
        ValueError: If the note is not a valid APC mini button address.
    """
    for row, base in enumerate(APC_MINI_ROW_BASES):
        if base <= note < base + APC_MINI_COLS:
            col = note - base
            return (row, col)
    raise ValueError(f"MIDI note {note} is not a valid APC mini button address")


if __name__ == "__main__":
    print("APC mini button MIDI note mapping:")
    for row in range(APC_MINI_ROWS):
        notes = [get_midi_note(row, col) for col in range(APC_MINI_COLS)]
        print(f"  row {row}: {[hex(n) for n in notes]}")
