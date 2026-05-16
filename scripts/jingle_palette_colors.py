#!/usr/bin/env python3
"""Capture Jingle Palette Reloaded and read button colors from a screenshot."""
from __future__ import annotations

import argparse
import ctypes
import sys
from ctypes import wintypes
from typing import Iterable, List, Tuple

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    print("Missing dependency 'Pillow'. Install with: pip install pillow pywin32")
    raise

try:
    import win32con
    import win32gui
    import win32ui
except ImportError as exc:
    print("Missing dependency 'pywin32'. Install with: pip install pillow pywin32")
    raise

user32 = ctypes.WinDLL("user32", use_last_error=True)
PrintWindow = user32.PrintWindow
PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
PrintWindow.restype = wintypes.BOOL

# Default window title substring to find the Jingle Palette window.
WINDOW_TITLE = "Jingle Palette Reloaded"

# Button layout configuration.
BUTTON_ROWS = 5
BUTTON_COLS = 5

# Paddings around the button grid in the window.
LEFT_PAD = 15
TOP_PAD = 15
BOTTOM_PAD = 235
RIGHT_PAD = 75

# Gap between buttons in pixels.
BUTTON_GAP = 8

# Pixel offset from the bottom of each button where we sample the color.
SAMPLE_OFFSET_FROM_BOTTOM = 10


def find_window(title_substring: str) -> int:
    title_lower = title_substring.lower()
    hwnd_found = 0

    def _enum_handler(hwnd: int, _ctx: int) -> None:
        nonlocal hwnd_found
        if hwnd_found:
            return
        if not win32gui.IsWindowVisible(hwnd):
            return
        text = win32gui.GetWindowText(hwnd) or ""
        if title_lower in text.lower():
            hwnd_found = hwnd

    win32gui.EnumWindows(_enum_handler, 0)
    return hwnd_found


def capture_window(hwnd: int) -> Image.Image:
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(bitmap)

    result = PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
    if not result:
        # fallback if PrintWindow fails
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)
    image = Image.frombuffer("RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1)

    win32gui.DeleteObject(bitmap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    return image


def compute_button_centers(
    image_width: int,
    image_height: int,
    rows: int,
    cols: int,
    left_pad: int,
    top_pad: int,
    right_pad: int,
    bottom_pad: int,
    button_gap: int = BUTTON_GAP,
) -> List[Tuple[int, int]]:
    content_width = image_width - left_pad - right_pad
    content_height = image_height - top_pad - bottom_pad
    if content_width <= 0 or content_height <= 0:
        raise ValueError("Window content area is invalid; check padding values and window size.")

    # Account for gaps between buttons
    total_gap_width = (cols - 1) * button_gap
    total_gap_height = (rows - 1) * button_gap
    button_width = (content_width - total_gap_width) / cols
    button_height = (content_height - total_gap_height) / rows

    centers: List[Tuple[int, int]] = []
    for row in range(rows):
        for col in range(cols):
            center_x = int(round(left_pad + col * (button_width + button_gap) + button_width / 2))
            center_y = int(round(top_pad + row * (button_height + button_gap) + button_height / 2))
            centers.append((center_x, center_y))
    return centers


def compute_sample_points(
    image_width: int,
    image_height: int,
    rows: int,
    cols: int,
    left_pad: int,
    top_pad: int,
    right_pad: int,
    bottom_pad: int,
    sample_offset_from_bottom: int,
    button_gap: int = BUTTON_GAP,
) -> List[Tuple[int, int, int, int]]:
    """Return list of (row, col, sample_x, sample_y) for each button."""
    content_width = image_width - left_pad - right_pad
    content_height = image_height - top_pad - bottom_pad

    total_gap_width = (cols - 1) * button_gap
    total_gap_height = (rows - 1) * button_gap
    button_width = (content_width - total_gap_width) / cols
    button_height = (content_height - total_gap_height) / rows

    points: List[Tuple[int, int, int, int]] = []
    for row in range(rows):
        for col in range(cols):
            button_left = left_pad + col * (button_width + button_gap)
            button_top = top_pad + row * (button_height + button_gap)
            button_right = button_left + button_width
            button_bottom = button_top + button_height

            sample_x = int(round((button_left + button_right) / 2))
            sample_y = int(round(button_bottom - sample_offset_from_bottom))
            sample_x = max(0, min(image_width - 1, sample_x))
            sample_y = max(0, min(image_height - 1, sample_y))

            points.append((row, col, sample_x, sample_y))
    return points


def sample_button_colors(
    image: Image.Image,
    rows: int,
    cols: int,
    left_pad: int,
    top_pad: int,
    right_pad: int,
    bottom_pad: int,
    sample_offset_from_bottom: int,
    button_gap: int = BUTTON_GAP,
) -> List[Tuple[int, int, Tuple[int, int, int]]]:
    width, height = image.size
    content_width = width - left_pad - right_pad
    content_height = height - top_pad - bottom_pad
    
    # Account for gaps between buttons
    total_gap_width = (cols - 1) * button_gap
    total_gap_height = (rows - 1) * button_gap
    button_width = (content_width - total_gap_width) / cols
    button_height = (content_height - total_gap_height) / rows

    samples: List[Tuple[int, int, Tuple[int, int, int]]] = []
    # reuse compute_sample_points to get coords
    points = compute_sample_points(width, height, rows, cols, left_pad, top_pad, right_pad, bottom_pad, sample_offset_from_bottom, button_gap)
    for (row, col, sample_x, sample_y) in points:
        color = image.getpixel((sample_x, sample_y))
        if isinstance(color, tuple) and len(color) >= 3:
            color = color[:3]
        elif isinstance(color, int):
            color = (color, color, color)
        samples.append((row, col, color))

    return samples


def format_color(color: Tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*color)


def print_sample_report(samples: List[Tuple[int, int, Tuple[int, int, int]]]) -> None:
    for row, col, color in samples:
        print(f"row={row+1:>2} col={col+1:>2} color={format_color(color)}")


def annotate_and_save(
    image: Image.Image,
    sample_points: List[Tuple[int, int, int, int]],
    out_path: str,
    dot_radius: int = 4,
    dot_color: Tuple[int, int, int] = (255, 0, 0),
) -> None:
    """Draw red dots at sample points and save image to out_path."""
    # Ensure image is writable RGB
    img = image.convert("RGB")
    draw = ImageDraw.Draw(img)
    for (_row, _col, x, y) in sample_points:
        left = x - dot_radius
        top = y - dot_radius
        right = x + dot_radius
        bottom = y + dot_radius
        draw.ellipse((left, top, right, bottom), fill=dot_color)
    img.save(out_path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read button colors from a Jingle Palette Reloaded screenshot")
    parser.add_argument("--window", type=str, default=WINDOW_TITLE, help="Window title substring")
    parser.add_argument("--rows", type=int, default=BUTTON_ROWS, help="Number of button rows")
    parser.add_argument("--cols", type=int, default=BUTTON_COLS, help="Number of button columns")
    parser.add_argument("--left-pad", type=int, default=LEFT_PAD, help="Left padding inside the window")
    parser.add_argument("--top-pad", type=int, default=TOP_PAD, help="Top padding inside the window")
    parser.add_argument("--right-pad", type=int, default=RIGHT_PAD, help="Right padding inside the window")
    parser.add_argument("--bottom-pad", type=int, default=BOTTOM_PAD, help="Bottom padding inside the window")
    parser.add_argument(
        "--sample-offset", type=int, default=SAMPLE_OFFSET_FROM_BOTTOM,
        help="Pixel distance from the button bottom where the color is sampled",
    )
    parser.add_argument("--button-gap", type=int, default=BUTTON_GAP, help="Gap between buttons in pixels")
    parser.add_argument("--export", type=str, default="", help="Path to save annotated screenshot (PNG)")
    parser.add_argument("--show-window-size", action="store_true", help="Print the captured window size and exit")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    hwnd = find_window(args.window)
    if not hwnd:
        print(f"Window not found: {args.window}")
        return 1

    image = capture_window(hwnd)

    if args.show_window_size:
        print(f"window_size={image.width}x{image.height}")
        return 0

    samples = sample_button_colors(
        image=image,
        rows=args.rows,
        cols=args.cols,
        left_pad=args.left_pad,
        top_pad=args.top_pad,
        right_pad=args.right_pad,
        bottom_pad=args.bottom_pad,
        sample_offset_from_bottom=args.sample_offset,
        button_gap=args.button_gap,
    )
    print_sample_report(samples)

    # Optionally export annotated screenshot with red dots at sample points
    if args.export:
        points = compute_sample_points(image.width, image.height, args.rows, args.cols, args.left_pad, args.top_pad, args.right_pad, args.bottom_pad, args.sample_offset, args.button_gap)
        try:
            annotate_and_save(image, points, args.export)
            print(f"Annotated screenshot saved to: {args.export}")
        except Exception as e:
            print(f"Failed to save annotated image: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
