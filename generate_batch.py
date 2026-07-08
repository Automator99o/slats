#!/usr/bin/env python3
import csv
import random

# Color presets containing high-contrast, vibrant combinations
PALETTES = [
    # 1. Cosmic Violet-Teal
    {
        "bg_color1": "#1c0d3a", "bg_color2": "#f97316", "glass_color1": "#06b6d4", "glass_color2": "#2563eb",
        "wave_color1": "#06b6d4", "wave_color2": "#2563eb", "wave_color3": "#f97316",
        "desc": "Cosmic Violet Teal", "keywords": "cyan,blue,purple,orange,refraction,nebula,abstract,loop,space"
    },
    # 2. Emerald Dream
    {
        "bg_color1": "#022c22", "bg_color2": "#fbbf24", "glass_color1": "#10b981", "glass_color2": "#84cc16",
        "wave_color1": "#10b981", "wave_color2": "#84cc16", "wave_color3": "#fbbf24",
        "desc": "Emerald Dream Green", "keywords": "green,lime,emerald,gold,forest,nature,abstract,gradient,loop"
    },
    # 3. Sunset Flare
    {
        "bg_color1": "#450a0a", "bg_color2": "#facc15", "glass_color1": "#f97316", "glass_color2": "#db2777",
        "wave_color1": "#f97316", "wave_color2": "#db2777", "wave_color3": "#facc15",
        "desc": "Sunset Fire Flare", "keywords": "red,orange,pink,yellow,sunset,fire,warm,flare,glowing,abstract"
    },
    # 4. Cyberpunk Velvet
    {
        "bg_color1": "#0f172a", "bg_color2": "#ec4899", "glass_color1": "#db2777", "glass_color2": "#a855f7",
        "wave_color1": "#db2777", "wave_color2": "#a855f7", "wave_color3": "#ec4899",
        "desc": "Cyberpunk Neon Pink", "keywords": "pink,magenta,purple,dark,violet,neon,retro,cyberpunk,futuristic"
    },
    # 5. Luxury Obsidian Gold
    {
        "bg_color1": "#171717", "bg_color2": "#b45309", "glass_color1": "#f59e0b", "glass_color2": "#fbbf24",
        "wave_color1": "#f59e0b", "wave_color2": "#fbbf24", "wave_color3": "#b45309",
        "desc": "Luxury Obsidian Gold", "keywords": "gold,luxury,premium,yellow,amber,black,dark,elegant,exclusive"
    },
    # 6. Ice Lagoon
    {
        "bg_color1": "#0c4a6e", "bg_color2": "#22d3ee", "glass_color1": "#34d399", "glass_color2": "#4f46e5",
        "wave_color1": "#34d399", "wave_color2": "#4f46e5", "wave_color3": "#22d3ee",
        "desc": "Ice Lagoon Blue", "keywords": "cyan,blue,mint,green,teal,glacier,winter,lagoon,abstract,motion"
    },
    # 7. Aurora Magic
    {
        "bg_color1": "#3b0764", "bg_color2": "#a3e635", "glass_color1": "#06b6d4", "glass_color2": "#c084fc",
        "wave_color1": "#06b6d4", "wave_color2": "#c084fc", "wave_color3": "#a3e635",
        "desc": "Aurora Cosmic Green", "keywords": "aurora,northern lights,green,purple,cyan,magical,neon,mystic,glow"
    },
    # 8. Crimson Sapphire
    {
        "bg_color1": "#030712", "bg_color2": "#dc2626", "glass_color1": "#f87171", "glass_color2": "#0ea5e9",
        "wave_color1": "#f87171", "wave_color2": "#0ea5e9", "wave_color3": "#dc2626",
        "desc": "Crimson Sapphire Blue Red", "keywords": "red,blue,navy,ruby,sapphire,contrast,bold,modern,graphics"
    },
    # 9. Orange Obsidian
    {
        "bg_color1": "#09090b", "bg_color2": "#ea580c", "glass_color1": "#f59e0b", "glass_color2": "#ffedd5",
        "wave_color1": "#f59e0b", "wave_color2": "#ffedd5", "wave_color3": "#ea580c",
        "desc": "Obsidian Orange Glow", "keywords": "orange,amber,black,peach,glow,minimal,clean,contrast,sleek"
    },
    # 10. Deep Amethyst
    {
        "bg_color1": "#080710", "bg_color2": "#d946ef", "glass_color1": "#7c3aed", "glass_color2": "#c084fc",
        "wave_color1": "#7c3aed", "wave_color2": "#c084fc", "wave_color3": "#d946ef",
        "desc": "Deep Amethyst Orchid", "keywords": "purple,orchid,magenta,dark,lilac,glow,luxury,elegant,abstract,loop"
    }
]

MODES = ["diagonal", "curved", "glass_wave"]

def main():
    rows = []
    
    # Generate 30 unique rows
    for i in range(1, 31):
        mode = MODES[(i - 1) % len(MODES)]
        palette = PALETTES[(i - 1) % len(PALETTES)]
        
        # Geometry variance
        # Make sure no two configurations have identical counts, angles, or speeds
        bar_count = int(14 + ((i * 7) % 31))  # 14 to 45
        bar_width = round(0.8 + ((i * 0.05) % 0.6), 2)  # 0.8 to 1.4
        
        if mode == "diagonal":
            # Angles from -60 to 60 excluding 0
            angle_choices = [-60, -50, -45, -35, -25, -15, 15, 25, 35, 45, 50, 60]
            bar_angle = angle_choices[i % len(angle_choices)]
            curve_amount = 0.0
        elif mode == "curved":
            bar_angle = int(25 + ((i * 5) % 31))  # 25 to 55
            curve_amount = round(0.6 + ((i * 0.15) % 1.2), 2)  # 0.6 to 1.8
        else:  # glass_wave
            bar_angle = 0
            curve_amount = 0.0
            
        displacement = int(35 + ((i * 9) % 76))  # 35 to 110
        glass_blur = int(16 + ((i * 4) % 25))  # 16 to 40
        glass_highlight = round(0.35 + ((i * 0.04) % 0.4), 2)  # 0.35 to 0.75
        speed = (i % 3) + 1  # Integer speeds 1, 2, or 3 for perfect seamless looping velocity
        
        # All clips rendered in 4K UHD for premium stock asset quality
        width, height = 3840, 2160
        res_label = "4K UHD"
        
        # Formulate unique stock titles
        title_templates = [
            "Abstract {desc} Reeded Glass Refraction Loop",
            "Cinematic {desc} Glass Panels Motion Background",
            "Modernist {desc} Fluted Glass Wall Abstract Graphics",
            "Vibrant {desc} Glass Slats Prism Wave Seamless",
            "Premium {desc} Glassmorphic Geometric Flow Loop"
        ]
        template = title_templates[i % len(title_templates)]
        title = template.format(desc=palette["desc"]) + f" ({res_label})"
        
        # Formulate unique keywords
        base_keywords = "glass,reeded,fluted,refraction,prism,backdrop,motion,background,loop,seamless,"
        unique_kws = base_keywords + palette["keywords"] + f",glassmorphism,{mode},{res_label},slats"
        
        # Clip configuration row
        row = {
            "id": f"{mode[:4]}_{palette['desc'].lower().replace(' ', '_')}_{i:02d}",
            "mode": mode,
            "bar_count": bar_count,
            "bar_width": bar_width,
            "bar_angle": bar_angle,
            "curve_amount": curve_amount,
            "bg_color1": palette["bg_color1"],
            "bg_color2": palette["bg_color2"],
            "bg_style": "radial",
            "glass_color1": palette["glass_color1"],
            "glass_color2": palette["glass_color2"],
            "glass_opacity": 0.12,
            "glass_highlight": glass_highlight,
            "speed": speed,
            "light_color1": "", "light_color2": "", "light_size": "", "light_speed": "",
            "fiber_count": "", "fiber_spread": "", "fiber_length": "", "fiber_glow": "", "fiber_color1": "", "fiber_color2": "",
            "wave_intensity": round(0.8 + ((i * 0.07) % 0.7), 2) if mode == "glass_wave" else "",
            "wave_color1": palette["wave_color1"] if mode == "glass_wave" else "",
            "wave_color2": palette["wave_color2"] if mode == "glass_wave" else "",
            "wave_color3": palette["wave_color3"] if mode == "glass_wave" else "",
            "vignette": 0.50,
            "duration": 10.0,
            "fps": 30,
            "width": width,
            "height": height,
            "title": title,
            "keywords": unique_kws
        }
        rows.append(row)
        
    # Write to batch.csv
    headers = [
        "id", "mode", "bar_count", "bar_width", "bar_angle", "curve_amount",
        "bg_color1", "bg_color2", "bg_style", "glass_color1", "glass_color2",
        "glass_opacity", "glass_highlight", "speed",
        "light_color1", "light_color2", "light_size", "light_speed",
        "fiber_count", "fiber_spread", "fiber_length", "fiber_glow", "fiber_color1", "fiber_color2",
        "wave_intensity", "wave_color1", "wave_color2", "wave_color3",
        "vignette", "duration", "fps", "width", "height", "title", "keywords"
    ]
    
    with open("batch.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"SUCCESS: Generated 30 highly unique stock-ready reeded glass clips inside batch.csv!")

if __name__ == "__main__":
    main()
