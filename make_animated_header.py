from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "siushah-header-animated.gif"
W, H = 1200, 390
FRAMES = 18

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
title_font = ImageFont.truetype(font_path, 58)
subtitle_font = ImageFont.truetype(regular_path, 16)
small_font = ImageFont.truetype(regular_path, 12)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def bezier(points: list[tuple[float, float]], steps: int = 100) -> list[tuple[float, float]]:
    result = []
    for index in range(steps + 1):
        t = index / steps
        u = 1 - t
        x = u**3 * points[0][0] + 3 * u**2 * t * points[1][0] + 3 * u * t**2 * points[2][0] + t**3 * points[3][0]
        y = u**3 * points[0][1] + 3 * u**2 * t * points[1][1] + 3 * u * t**2 * points[2][1] + t**3 * points[3][1]
        result.append((x, y))
    return result


def frame(frame_index: int) -> Image.Image:
    image = Image.new("RGB", (W, H), "#070b1e")
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(H):
        t = y / H
        color = (5 + int(16 * t), 8 + int(4 * t), 24 + int(20 * t))
        draw.line((0, y, W, y), fill=color + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    phase = frame_index / FRAMES * math.tau
    for cx, cy, radius, color in ((180 + math.sin(phase) * 100, 95 + math.cos(phase * .8) * 42, 180, (34, 211, 238, 75)), (1030 + math.cos(phase * .7) * 100, 295 + math.sin(phase) * 34, 210, (167, 139, 250, 70))):
        gd.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
    image = Image.alpha_composite(image.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(42)))
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(0, W, 36):
        draw.line((x, 20, x, H - 20), fill=(103, 232, 249, 22), width=1)
    for y in range(20, H - 20, 36):
        draw.line((20, y, W - 20, y), fill=(103, 232, 249, 22), width=1)
    path = bezier([(-40, 275), (210, 40), (400, 60), (610, 230)], 100)
    path += bezier([(610, 230), (840, 390), (990, 390), (1240, 80)], 100)[1:]
    draw.line(path, fill=(103, 232, 249, 150), width=2)
    orbit = [(600 + 430 * math.cos(t), 195 + 105 * math.sin(t)) for t in [i * math.tau / 120 for i in range(121)]]
    draw.line(orbit, fill=(103, 232, 249, 55), width=1)
    orbit2 = [(600 + 360 * math.cos(t), 195 + 75 * math.sin(t)) for t in [i * math.tau / 120 for i in range(121)]]
    draw.line(orbit2, fill=(167, 139, 250, 45), width=1)
    for x, y in ((170, 150), (430, 285), (830, 120), (1030, 285)):
        pulse = 2 + int((math.sin(phase * 1.7 + x) + 1) * 1.2)
        draw.ellipse((x - pulse, y - pulse, x + pulse, y + pulse), fill=(103, 232, 249, 220))
    title_angle = phase
    tx = 600 + 240 * math.cos(title_angle)
    ty = 195 + 76 * math.sin(title_angle)
    title_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(title_layer, "RGBA")
    bbox = td.textbbox((0, 0), "SIUShah", font=title_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    td.text((W // 2 - tw // 2, H // 2 - th // 2 - 9), "SIUShah", font=title_font, fill=(248, 250, 252, 255), stroke_width=1, stroke_fill=(103, 232, 249, 80))
    # Rotate the title itself while moving it around the orbit.
    title_layer = title_layer.rotate(-math.degrees(title_angle), center=(W // 2, H // 2), resample=Image.Resampling.BICUBIC)
    # Move the rotated title from center to its orbit position.
    dx, dy = int(tx - W / 2), int(ty - H / 2)
    shifted = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shifted.alpha_composite(title_layer, (dx, dy))
    image = Image.alpha_composite(image, shifted)
    draw = ImageDraw.Draw(image, "RGBA")
    capability = ["FFMPEG · PYSIDE6 · AI · WINDOWS", "PYTHON · SYSTEMS · AUTOMATION", "MULTITRACK MEDIA · KEYFRAMES · AUDIO", "ARCHITECTURE · TESTING · DELIVERY"][frame_index // 5 % 4]
    bbox = draw.textbbox((0, 0), capability, font=subtitle_font)
    draw.text(((W - (bbox[2] - bbox[0])) / 2, 205), capability, font=subtitle_font, fill=(165, 243, 252, 245))
    tagline = "BUILDING PRACTICAL SOFTWARE WITH EVIDENCE"
    bbox = draw.textbbox((0, 0), tagline, font=small_font)
    draw.text(((W - (bbox[2] - bbox[0])) / 2, 242), tagline, font=small_font, fill=(196, 181, 253, 225))
    draw.rounded_rectangle((14, 14, W - 14, H - 14), radius=16, outline=(103, 232, 249, 70), width=1)
    return image.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)


frames = [frame(index) for index in range(FRAMES)]
OUT.parent.mkdir(parents=True, exist_ok=True)
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=140, loop=0, optimize=True, disposal=2)
print(OUT)
