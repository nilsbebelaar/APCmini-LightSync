# MIDI test: `scripts/midi_test.py`

Install dependencies (prefer a venv):

```bash
python -m pip install -r requirements.txt
```

List available MIDI outputs:

```bash
python scripts/midi_test.py --list
```

Send test bytes (defaults to `loopback Midi`):

```bash
python scripts/midi_test.py --port "loopback Midi" --send
```

If your device name differs, set the `DEVICE_NAME` at the top of `scripts/midi_test.py` or pass `--port`.

# Jingle Palette color capture: `scripts/jingle_palette_colors.py`

Capture the Jingle Palette Reloaded window and print sampled button colors.

```bash
python scripts/jingle_palette_colors.py --window "Jingle Pallette Reloaded" --rows 4 --cols 8 --colors
```

If the window title differs, pass `--window "<window title substring>"`.
