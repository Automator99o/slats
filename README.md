# 🎬 Adobe Stock Animation Video Pipeline

Batch-render **config-driven Canvas 2D animations** as Adobe Stock-ready MP4/MOV videos using headless Chromium (Playwright) + FFmpeg — all inside Docker.

---

## 🚀 Quick Start

```bash
# 1. Build the Docker image
docker compose build

# 2. Render all clips from batch.csv → ./output/
docker compose up
```

That's it. Videos appear in `./output/`.

---

## 🎨 Animation Modes

| Mode | Description | Reference Style |
|------|-------------|-----------------|
| `diagonal` | Diagonal glass bars sweeping corner to corner | Teal/blue glass panels at 45° |
| `curved` | Curved glass elements with bezier paths | Purple/indigo curved ribbons |
| `light_reveal` | Moving light source illuminating glass bars | Blue/orange glow behind vertical bars |
| `fiber_optics` | Fiber optic strands with glowing tips | Flowing purple/cyan light strands |
| `glass_wave` | Glass blinds with flowing gradient refraction | Blue gradient seen through vertical blinds |

---

## 📝 Editing `batch.csv`

Each row in `batch.csv` is one video clip. Key columns:

| Column | Values | Description |
|--------|--------|-------------|
| `id` | string | Unique clip ID (becomes filename) |
| `mode` | `diagonal` / `curved` / `light_reveal` / `fiber_optics` / `glass_wave` | Animation type |
| `bar_count` | 15–60 | Number of glass bars/slats |
| `bar_angle` | 0–90 | Bar angle in degrees (diagonal/curved) |
| `curve_amount` | 0–2.0 | Curvature strength (curved mode) |
| `glass_color1/2` | hex | Glass bar colours |
| `glass_opacity` | 0.05–0.3 | Glass transparency |
| `speed` | 0.1–3.0 | Animation speed multiplier |
| `fiber_count` | 100–300 | Number of fiber strands (fiber mode) |
| `wave_intensity` | 0.5–2.0 | Refraction strength (wave mode) |
| `duration` | seconds | Clip length |
| `fps` | 30 / 60 | Frame rate |
| `width` × `height` | pixels | Resolution (1920×1080 or 3840×2160) |
| `title` | string | Adobe Stock title |
| `keywords` | comma-sep | Adobe Stock keywords |

**Tip:** You can hot-swap `batch.csv` without rebuilding the Docker image.

---

## 🖥️ CLI Options

```bash
# Preview first clip in your browser before rendering
docker compose run renderer python engine.py --preview

# Resume a failed batch (skip first 10 clips)
docker compose run renderer python engine.py --start-from 10

# Explicitly set output format
docker compose run renderer python engine.py --format mp4
docker compose run renderer python engine.py --format mov

# Custom batch file
docker compose run renderer python engine.py --batch my_clips.csv
```

---

## 🔄 Resume a Failed Batch

The engine **automatically skips clips that already exist** in the output folder. If rendering crashes at clip 15 of 25:

```bash
# Just run again — clips 1-14 are skipped automatically
docker compose up
```

Or jump straight to a specific row:

```bash
docker compose run renderer python engine.py --start-from 14
```

---

## 📦 MP4 vs MOV

| Format | Codec | Use Case |
|--------|-------|----------|
| **MP4** | H.264 @ 45 Mbps, BT.709 | Adobe Stock uploads, web delivery |
| **MOV** | ProRes 422 HQ @ 45 Mbps | Post-production, maximum quality |

Both use fixed 45 Mbps bitrate for consistent Adobe Stock quality.

---

## 📁 Folder Structure

```
project/
├── animation.html      ← Canvas 2D renderer (5 modes)
├── engine.py           ← Playwright batch render engine
├── batch.csv           ← Clip configurations (hot-swappable)
├── Dockerfile          ← Container definition
├── docker-compose.yml  ← Orchestration + usage examples
├── README.md           ← This file
├── output/             ← Rendered MP4/MOV files
│   ├── diag_teal_01.mp4
│   ├── curv_purple_01.mp4
│   └── ...
└── /tmp/frames/        ← Temporary PNGs (auto-deleted)
    └── clip_id/
        ├── frame_00001.png
        └── ...
```

---

## 🛠️ Local Development (without Docker)

```bash
# Install dependencies
pip install playwright
playwright install chromium

# Preview animation directly
# Open animation.html in your browser

# Render batch
python engine.py --batch batch.csv --format mp4

# Preview + render
python engine.py --preview --format mp4
```

Requires FFmpeg installed and available in PATH.

---

## 💡 Tips

- **4K clips** take ~4× longer to render than 1080p
- **60fps clips** take 2× longer than 30fps
- **ProRes MOV** files are ~5-10× larger than H.264 MP4
- Use `--preview` to check your animation looks right before committing to a full batch
- The engine reuses a single Chromium instance for all clips — no restart overhead
