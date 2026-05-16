# APCmini LightSync

Automatically sync Jingle Palette Reloaded button colors to APC mini lights via MIDI.

## Setup

Install dependencies (preferably in a virtual environment):

```bash
python -V 3.11 -m venv .venv311
.venv311\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Run once

Capture the current state of Jingle Palette and send colors to the APC mini:

```bash
python .\lightsync.py
```

### Run continuously

Sync colors every 0.5 seconds (APC mini will update in real-time as you change sounds):

```bash
python .\lightsync.py --interval 0.5
```

Other interval examples:

```bash
# Update every second
python .\lightsync.py --interval 1

# Update every 2 seconds
python .\lightsync.py --interval 2

# Update every 100ms (10 times per second)
python .\lightsync.py --interval 0.1
```

Press **Ctrl+C** to stop the continuous loop.

### Custom MIDI port

If your loopMIDI port has a different name:

```bash
python .\lightsync.py --port "My Custom Port" --interval 1
```

### Custom window title

If your Jingle Palette window has a different title:

```bash
python .\lightsync.py --window "My Jingle Window" --interval 1
```

### Verbose output

See detailed MIDI messages being sent:

```bash
python .\lightsync.py --interval 1 --verbose
```

Example output:
```
Running every 1 seconds (Ctrl+C to stop)...
  row  1 col  1: color #c0ffc0 → status 0x9c note 0x38 velocity 127 (PLAYING)
  row  1 col  2: color #ff0000 → note 0x39 velocity 127
  ...
Sent 64 MIDI messages (0 colors unmapped)
```

### APC mini button grid

The script assumes an 8x8 button grid (64 buttons total). If your Jingle Palette has a different button layout, adjust with `--rows` and `--cols`:

```bash
python .\lightsync.py --rows 4 --cols 8 --interval 1
```

### Full options

```
python .\lightsync.py --help
```

Options:
- `--window TITLE` - Jingle Palette window title substring (default: "Jingle Palette Reloaded")
- `--port PORT` - MIDI output port name (default: "loopMIDI Port 1")
- `--rows ROWS` - Number of button rows (default: 4)
- `--cols COLS` - Number of button columns (default: 4)
- `--button-gap GAP` - Gap between buttons in pixels (default: 8)
- `--interval SEC` - Run every X seconds (0 = run once) (default: 0)
- `--verbose` - Print details for each button

## Special Colors

- **Light green (#c0ffc0)**: Detected as "currently playing" - sends blink command (status 0x9C) with red (velocity from #ff0000 mapping)
- **Other colors**: Mapped to MIDI velocity values via the color mapping in `scripts/color_to_midi.py`

## Architecture

- `lightsync.py` - Main orchestrator
- `scripts/jingle_palette_colors.py` - Captures Jingle Palette window and samples button colors
- `scripts/color_to_midi.py` - Maps colors (hex) to MIDI velocity values
- `scripts/apc_mini_layout.py` - Maps button row/col positions to APC mini MIDI note numbers
- `scripts/midi_test.py` - Low-level MIDI testing utility

See [README.midi.md](README.midi.md) for advanced usage and testing utilities.
