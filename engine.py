#!/usr/bin/env python3
"""
Batch render engine for Adobe Stock animation videos.
Uses Playwright (headless Chromium) to capture frames from animation.html,
then assembles them into MP4 or MOV using FFmpeg.
"""

import argparse
import csv
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FRAMES_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")

HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "animation.html")

# Fields that should be converted to int
INT_FIELDS = {"width", "height", "fps", "bar_count", "fiber_count"}

# Fields that should be converted to float
FLOAT_FIELDS = {
    "duration", "bar_width", "bar_angle", "curve_amount",
    "glass_opacity", "glass_highlight", "speed",
    "light_size", "light_speed",
    "fiber_spread", "fiber_length", "fiber_glow",
    "wave_intensity", "vignette",
}

# Fields that should be converted to bool
BOOL_FIELDS = set()  # none currently, but ready for future use

# Fields that stay as strings
STR_FIELDS = {
    "mode", "bg_color1", "bg_color2", "bg_style",
    "glass_color1", "glass_color2",
    "light_color1", "light_color2",
    "fiber_color1", "fiber_color2",
    "wave_color1", "wave_color2", "wave_color3",
}

# Metadata-only columns (not passed to animation config)
META_FIELDS = {"id", "title", "keywords"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_config(row: dict) -> dict:
    """Convert a CSV row (all strings) into a typed config dict."""
    config = {}
    for key, val in row.items():
        if key in META_FIELDS:
            continue
        val = val.strip()
        if not val:
            continue
        if key in INT_FIELDS:
            config[key] = int(val)
        elif key in FLOAT_FIELDS:
            config[key] = float(val)
        elif key in BOOL_FIELDS:
            config[key] = val.lower() in ("true", "1", "yes")
        elif key in STR_FIELDS:
            config[key] = val
        else:
            # Unknown field — try numeric, fall back to string
            try:
                config[key] = float(val) if "." in val else int(val)
            except ValueError:
                config[key] = val
    return config


def build_ffmpeg_cmd(frames_dir: str, output_path: str, fps: int, fmt: str) -> list:
    """Build the FFmpeg command with FIXED bitrate settings."""
    inp = os.path.join(frames_dir, "frame_%05d.png")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-start_number", "1",
        "-i", inp,
    ]

    if fmt == "mp4":
        cmd.extend([
            "-c:v", "libx264",
            "-b:v", "100M",
            "-minrate", "100M",
            "-maxrate", "100M",
            "-bufsize", "200M",
            "-preset", "slow",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
            "-colorspace", "bt709",
        ])
    elif fmt == "mov":
        cmd.extend([
            "-c:v", "prores_ks",
            "-profile:v", "3",
            "-b:v", "45M",
            "-pix_fmt", "yuv422p10le",
            "-movflags", "+faststart",
        ])

    cmd.append(output_path)
    return cmd


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PREVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def preview_clip(config: dict, html_path: str):
    """Open animation in default browser with the given config."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    script = f"<script>window.ANIMATION_CONFIG={json.dumps(config)};</script>"
    html = html.replace("<head>", f"<head>{script}", 1)

    preview_path = os.path.join(os.path.dirname(html_path), "_preview.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html)

    url = Path(preview_path).as_uri()
    print(f"\n  ▸ Preview opened: {url}")
    webbrowser.open(url)

    input("\n  Press ENTER to start rendering (Ctrl+C to cancel)...\n")

    try:
        os.remove(preview_path)
    except OSError:
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  RENDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_clip(page, config: dict, clip_id: str, output_path: str, fmt: str, html_path: str) -> bool:
    """Render a single clip: capture frames → FFmpeg → cleanup."""
    frames_dir = os.path.join(FRAMES_BASE, clip_id)
    os.makedirs(frames_dir, exist_ok=True)

    # Navigate & inject config
    page.goto(Path(html_path).as_uri(), wait_until="domcontentloaded")
    page.evaluate(f"window.resetRenderer({json.dumps(config)})")
    page.wait_for_function("window.animationReady === true", timeout=15000)

    # Viewport must match canvas
    page.set_viewport_size({"width": config["width"], "height": config["height"]})

    # Total frames
    progress = page.evaluate("window.getProgress()")
    total = progress["total"]

    # Frame capture loop
    canvas = page.locator("#viewport")
    frame_num = 0
    while True:
        result = page.evaluate("window.stepFrame()")
        frame_num += 1
        frame_path = os.path.join(frames_dir, f"frame_{frame_num:05d}.png")
        canvas.screenshot(path=frame_path, type="png")
        print(f"\r  Frame {frame_num}/{total}", end="", flush=True)
        if not result:
            break

    print()

    # Assemble video with FFmpeg
    print(f"  ▸ Assembling {fmt.upper()} with FFmpeg …")
    cmd = build_ffmpeg_cmd(frames_dir, output_path, config["fps"], fmt)
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        print(f"  ✗ FFmpeg error:\n{proc.stderr[:500]}")
        return False

    # Cleanup temp frames
    shutil.rmtree(frames_dir, ignore_errors=True)

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  ✓ Saved: {output_path}  ({file_size:.1f} MB)")
    return True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    parser = argparse.ArgumentParser(
        description="Batch render animation clips for Adobe Stock"
    )
    parser.add_argument("--batch", default="batch.csv", help="Path to CSV file (default: batch.csv)")
    parser.add_argument("--output", default="./output", help="Output folder (default: ./output)")
    parser.add_argument("--preview", action="store_true", help="Open browser preview before rendering")
    parser.add_argument("--start-from", type=int, default=0, dest="start_from",
                        help="Skip the first N rows (resume support)")
    parser.add_argument("--format", choices=["mp4", "mov"], default=None,
                        help="Output format: mp4 or mov (prompts if omitted)")
    args = parser.parse_args()

    # ── Read batch CSV ──
    batch_path = os.path.abspath(args.batch)
    if not os.path.exists(batch_path):
        print(f"✗ Batch file not found: {batch_path}")
        sys.exit(1)

    with open(batch_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("✗ Batch file is empty")
        sys.exit(1)

    print(f"  Loaded {len(rows)} clips from {batch_path}")

    # ── Determine format ──
    fmt = args.format
    if fmt is None:
        try:
            while True:
                choice = input("\n  Output format — (1) MP4  or  (2) MOV/ProRes?  [1]: ").strip()
                if choice in ("", "1", "mp4"):
                    fmt = "mp4"
                    break
                elif choice in ("2", "mov"):
                    fmt = "mov"
                    break
                print("  Please enter 1 or 2.")
        except EOFError:
            print("  ▸ Non-interactive environment detected: Defaulting format to MP4")
            fmt = "mp4"

    # ── Output directory ──
    out_dir = os.path.abspath(args.output)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(FRAMES_BASE, exist_ok=True)

    # ── HTML path ──
    if not os.path.exists(HTML_FILE):
        print(f"✗ animation.html not found: {HTML_FILE}")
        sys.exit(1)

    html_path = os.path.abspath(HTML_FILE)

    # ── Preview ──
    if args.preview and rows:
        first_config = build_config(rows[0])
        preview_clip(first_config, html_path)

    # ── Batch render ──
    from playwright.sync_api import sync_playwright

    print(f"\n{'━' * 56}")
    print(f"  Starting batch render — {len(rows)} clips → {fmt.upper()}")
    print(f"  Output: {out_dir}")
    print(f"{'━' * 56}\n")

    success = 0
    skipped = 0
    failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        )
        page = browser.new_page()

        for idx, row in enumerate(rows):
            # Resume support
            if idx < args.start_from:
                continue

            clip_id = row.get("id", f"clip_{idx+1:03d}").strip()
            title = row.get("title", clip_id).strip()
            output_file = os.path.join(out_dir, f"{clip_id}.{fmt}")

            # Skip already-rendered
            if os.path.exists(output_file):
                skipped += 1
                print(f"  ⏭  [{idx+1}/{len(rows)}] {clip_id} — already rendered, skipping")
                continue

            print(f"\n  🎬 Rendering clip {idx+1}/{len(rows)}: {title}")
            config = build_config(row)

            ok = render_clip(page, config, clip_id, output_file, fmt, html_path)
            if ok:
                success += 1
            else:
                failed += 1

        browser.close()

    # ── Summary ──
    print(f"\n{'━' * 56}")
    print(f"  DONE  ✓ {success} rendered  ⏭ {skipped} skipped  ✗ {failed} failed")
    print(f"{'━' * 56}\n")


if __name__ == "__main__":
    main()
