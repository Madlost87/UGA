from __future__ import annotations

import random
import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    return (*hex_to_rgb(hex_color), alpha)


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = image.size
    target_w, target_h = size
    scale = max(target_w / width, target_h / height)
    resized = image.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def fit_cover_center_crop(image: Image.Image, size: tuple[int, int], crop_ratio: float = 0.68) -> Image.Image:
    width, height = image.size
    crop_w = int(width * crop_ratio)
    crop_h = int(height * crop_ratio)
    left = (width - crop_w) // 2
    top = (height - crop_h) // 2
    return fit_cover(image.crop((left, top, left + crop_w, top + crop_h)), size)


def blend_external_paper(base: Image.Image, texture_path: Path, opacity: float) -> None:
    if not texture_path.exists() or opacity <= 0:
        return
    texture = Image.open(texture_path).convert("RGB")
    texture = fit_cover_center_crop(texture, base.size)
    texture = texture.convert("RGBA")
    overlay = Image.blend(base.convert("RGBA"), texture, opacity)
    base.alpha_composite(overlay)


def jitter_color(base: tuple[int, int, int], amount: int, rng: random.Random) -> tuple[int, int, int]:
    return tuple(max(0, min(255, channel + rng.randint(-amount, amount))) for channel in base)


def draw_soft_line(
    layer: Image.Image,
    points: Iterable[tuple[int, int]],
    fill: tuple[int, int, int, int],
    width: int,
) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.line(list(points), fill=fill, width=width, joint="curve")


def add_wash(
    layer: Image.Image,
    center: tuple[int, int],
    radius: tuple[int, int],
    color: tuple[int, int, int, int],
    blur: int,
) -> None:
    wash = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(wash, "RGBA")
    x, y = center
    rx, ry = radius
    draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=color)
    wash = wash.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(wash)


def draw_leaf(
    layer: Image.Image,
    center: tuple[int, int],
    size: tuple[int, int],
    angle: float,
    color: tuple[int, int, int, int],
) -> None:
    leaf = Image.new("RGBA", (size[0] * 3, size[1] * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(leaf, "RGBA")
    box = (size[0], size[1], size[0] * 2, size[1] * 2)
    draw.ellipse(box, fill=color)
    draw.line(
        (size[0] * 1.08, size[1] * 1.5, size[0] * 1.92, size[1] * 1.5),
        fill=(70, 75, 48, max(20, color[3] - 20)),
        width=max(1, size[0] // 18),
    )
    leaf = leaf.filter(ImageFilter.GaussianBlur(max(0.6, size[0] / 35)))
    leaf = leaf.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    x = center[0] - leaf.width // 2
    y = center[1] - leaf.height // 2
    layer.alpha_composite(leaf, (x, y))


def draw_berry(
    layer: Image.Image,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int, int],
) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    draw.ellipse(
        (x - radius // 3, y - radius // 3, x, y),
        fill=(255, 235, 210, max(10, color[3] // 3)),
    )


def draw_stone(
    layer: Image.Image,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
    rng: random.Random,
) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x1, y1, x2, y2 = box
    points = []
    steps = 14
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    rx = (x2 - x1) / 2
    ry = (y2 - y1) / 2
    for i in range(steps):
        angle = 6.2831853 * i / steps
        wobble = rng.uniform(0.86, 1.08)
        points.append((int(cx + rx * wobble * math.cos(angle)), int(cy + ry * wobble * math.sin(angle))))
    draw.polygon(points, fill=color)
    draw.line(points + [points[0]], fill=(72, 68, 57, max(10, color[3] - 18)), width=2)


def add_paper_texture(base: Image.Image, style: dict, rng: random.Random) -> None:
    paper = style["paper"]
    base_rgb = hex_to_rgb(paper["base_color"])
    width, height = base.size
    pixels = base.load()

    wash_scale = paper["wash_scale"]
    low_w = max(32, width // wash_scale)
    low_h = max(32, height // wash_scale)
    low_noise = Image.new("L", (low_w, low_h))
    low_pixels = low_noise.load()
    for y in range(low_h):
        for x in range(low_w):
            low_pixels[x, y] = 128 + rng.randint(-paper["wash_strength"], paper["wash_strength"])
    low_noise = low_noise.resize((width, height), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(10))
    noise_pixels = low_noise.load()

    for y in range(height):
        edge_y = min(y, height - 1 - y) / height
        for x in range(width):
            edge_x = min(x, width - 1 - x) / width
            edge = min(edge_x, edge_y)
            darken = 0
            if paper["edge_aging"]:
                darken = int(max(0, paper["edge_darkening_strength"] * (1 - edge / paper["edge_width_ratio"])))
            large_variation = int((noise_pixels[x, y] - 128) * 0.42)
            fine_variation = rng.randint(-paper["noise"], paper["noise"])
            variation = large_variation + fine_variation - darken
            pixels[x, y] = tuple(max(0, min(255, channel + variation)) for channel in base_rgb)

    draw = ImageDraw.Draw(base, "RGBA")
    if paper["fibers"]:
        for _ in range(paper["fiber_count"]):
            x = rng.randrange(width)
            y = rng.randrange(height)
            length = rng.randint(width // 140, width // 60)
            color = rgba(paper["fiber_color"], rng.randint(3, 7))
            draw.line((x, y, x + length, y + rng.randint(-2, 2)), fill=color, width=1)

    if paper["speckles"]:
        for _ in range(paper["speckle_count"]):
            x = rng.randrange(width)
            y = rng.randrange(height)
            radius = rng.choice([1, 1, 1, 1, 2])
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(paper["speckle_color"], rng.randint(3, 8)))

    if paper["stains"]:
        stain_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        stain_draw = ImageDraw.Draw(stain_layer, "RGBA")
        for _ in range(paper["stain_count"]):
            x = rng.randrange(width)
            y = rng.randrange(height)
            rx = rng.randint(width // 45, width // 14)
            ry = rng.randint(height // 55, height // 18)
            stain_draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=rgba(paper["stain_color"], rng.randint(8, 18)))
        base.alpha_composite(stain_layer.filter(ImageFilter.GaussianBlur(18)))


def draw_modern_background(base: Image.Image, style: dict) -> None:
    paper = style["paper"]
    if not paper.get("modern_graphics"):
        return

    width, height = base.size
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    grid_color = rgba(paper["grid_color"], paper["grid_opacity"])
    step = 120
    for x in range(0, width + step, step):
        draw.line((x, 0, x, height), fill=grid_color, width=1)
    for y in range(0, height + step, step):
        draw.line((0, y, width, y), fill=grid_color, width=1)

    accents = [
        (paper["accent_blue"], (0, 0, 780, 175), 110),
        (paper["accent_orange"], (width - 760, 0, width, 160), 95),
        (paper["accent_green"], (0, height - 165, 720, height), 90),
        (paper["accent_purple"], (width - 690, height - 150, width, height), 85),
    ]
    for color, box, alpha in accents:
        draw.rounded_rectangle(box, radius=0, fill=rgba(color, alpha))

    draw.polygon(
        [(width - 520, 250), (width - 210, 250), (width - 380, 520)],
        fill=rgba(paper["accent_blue"], 45),
    )
    draw.polygon(
        [(170, height - 460), (470, height - 290), (115, height - 160)],
        fill=rgba(paper["accent_orange"], 42),
    )
    draw.line((0, 210, width, 210), fill=rgba("#CBD5E1", 140), width=5)
    draw.line((0, height - 205, width, height - 205), fill=rgba("#CBD5E1", 120), width=4)

    base.alpha_composite(layer)


def draw_watercolor(base: Image.Image, style: dict, rng: random.Random) -> None:
    if not style["watercolor"]["enabled"]:
        return

    wc = style["watercolor"]
    width, height = base.size
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))

    twig = rgba(wc["twig_color"], wc["corner_opacity"])
    leaf = rgba(wc["leaf_color"], wc["corner_opacity"] - 10)
    berry = rgba(wc["berry_color"], wc["corner_opacity"] + 8)
    stone = rgba(wc["stone_color"], wc["corner_opacity"] - 8)

    draw_soft_line(layer, [(70, 135), (145, 92), (250, 82), (365, 120)], twig, 8)
    for x, y, angle in [(145, 91, -28), (185, 88, 24), (245, 89, -18), (306, 105, 28)]:
        draw_leaf(layer, (x, y), (54, 22), angle, leaf)
    for x, y in [(205, 118), (230, 76), (280, 119)]:
        draw_berry(layer, (x, y), 12, berry)

    for box in [
        (width - 325, 70, width - 235, 128),
        (width - 260, 116, width - 160, 176),
        (width - 380, 130, width - 292, 186),
    ]:
        draw_stone(layer, box, stone, rng)

    draw_soft_line(layer, [(85, height - 135), (170, height - 105), (285, height - 115), (395, height - 85)], twig, 9)
    draw_soft_line(layer, [(115, height - 88), (205, height - 150), (320, height - 155)], rgba(wc["twig_color"], wc["opacity"]), 5)

    draw_soft_line(layer, [(width - 360, height - 88), (width - 260, height - 145), (width - 145, height - 118)], rgba(wc["twig_color"], wc["opacity"]), 6)
    for x, y, angle in [(width - 310, height - 120, 30), (width - 235, height - 150, -22), (width - 185, height - 120, 18)]:
        draw_leaf(layer, (x, y), (48, 20), angle, rgba(wc["leaf_color"], wc["opacity"]))
    draw_berry(layer, (width - 250, height - 93), 10, rgba(wc["berry_color"], wc["opacity"] + 8))

    add_wash(layer, (width // 2 - 260, height // 2 - 80), (260, 120), rgba(wc["leaf_color"], wc["central_opacity"]), 52)
    draw_leaf(layer, (width // 2 - 310, height // 2 - 85), (70, 26), -24, rgba(wc["leaf_color"], wc["central_opacity"] + 4))
    draw_leaf(layer, (width // 2 - 185, height // 2 - 35), (58, 22), 18, rgba(wc["leaf_color"], wc["central_opacity"] + 2))
    draw_soft_line(
        layer,
        [(690, 1130), (815, 1088), (970, 1115), (1125, 1074)],
        rgba(wc["twig_color"], wc["central_opacity"] + 6),
        5,
    )
    for x, y, angle in [(775, 1096, -22), (915, 1110, 20), (1045, 1084, -16)]:
        draw_leaf(layer, (x, y), (54, 20), angle, rgba(wc["leaf_color"], wc["central_opacity"] + 8))
    for x, y in [(860, 1076), (1005, 1122)]:
        draw_berry(layer, (x, y), 8, rgba(wc["berry_color"], wc["central_opacity"] + 8))

    add_wash(layer, (1680, 1490), (230, 110), rgba(wc["stone_color"], wc["central_opacity"] - 6), 48)
    for box in [
        (1605, 1435, 1678, 1482),
        (1680, 1462, 1765, 1510),
        (1560, 1494, 1640, 1544),
    ]:
        draw_stone(layer, box, rgba(wc["stone_color"], wc["central_opacity"] + 4), rng)
    draw_stone(
        layer,
        (width // 2 + 430, height // 2 + 205, width // 2 + 520, height // 2 + 258),
        rgba(wc["stone_color"], wc["central_opacity"] + 10),
        rng,
    )

    for _ in range(wc["margin_marks"]):
        side = rng.choice(["left", "right", "top", "bottom"])
        if side == "left":
            x, y = rng.randint(20, 70), rng.randint(250, height - 260)
        elif side == "right":
            x, y = rng.randint(width - 75, width - 20), rng.randint(250, height - 260)
        elif side == "top":
            x, y = rng.randint(430, width - 430), rng.randint(25, 80)
        else:
            x, y = rng.randint(430, width - 430), rng.randint(height - 80, height - 25)
        draw_leaf(layer, (x, y), (32, 13), rng.randint(-50, 50), rgba(wc["leaf_color"], wc["opacity"] // 2))

    layer = layer.filter(ImageFilter.GaussianBlur(wc["blur_radius"]))
    base.alpha_composite(layer)


def tint_to_paper(asset: Image.Image, alpha: int) -> Image.Image:
    asset = asset.convert("RGBA")
    bg_samples = [
        asset.getpixel((0, 0)),
        asset.getpixel((asset.width - 1, 0)),
        asset.getpixel((0, asset.height - 1)),
        asset.getpixel((asset.width - 1, asset.height - 1)),
    ]
    bg = tuple(sum(sample[i] for sample in bg_samples) // len(bg_samples) for i in range(3))
    pixels = asset.load()
    for y in range(asset.height):
        for x in range(asset.width):
            r, g, b, a = pixels[x, y]
            distance = ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5
            brightness = (r + g + b) / 3
            if distance < 28 or brightness > 246:
                pixels[x, y] = (255, 255, 255, 0)
                continue
            new_alpha = int(min(alpha, max(0, distance - 18) * alpha / 95))
            pixels[x, y] = (r, g, b, new_alpha)
    return asset.filter(ImageFilter.GaussianBlur(0.45))


def paste_watercolor_asset(
    base: Image.Image,
    asset_path: Path,
    center: tuple[int, int],
    height: int,
    opacity: int,
    angle: float = 0,
) -> None:
    if not asset_path.exists() or opacity <= 0:
        return
    asset = Image.open(asset_path)
    ratio = height / asset.height
    asset = asset.resize((int(asset.width * ratio), height), Image.Resampling.LANCZOS)
    asset = tint_to_paper(asset, opacity)
    if angle:
        asset = asset.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    x = center[0] - asset.width // 2
    y = center[1] - asset.height // 2
    base.alpha_composite(asset, (x, y))


def draw_external_watercolors(base: Image.Image, style: dict, botanical_path: Path) -> None:
    wc = style["watercolor"]
    if not wc["enabled"] or not wc["external_assets_enabled"]:
        return
    width, height = base.size
    opacity = wc["external_asset_opacity"]

    pattern_opacity = wc["external_pattern_opacity"]
    pattern_height = wc["external_pattern_height"]
    pattern_positions = [
        (700, 360, -18, 0.78),
        (1280, 455, 24, 0.68),
        (1960, 410, -34, 0.72),
        (2740, 390, 22, 0.76),
        (560, 1020, 28, 0.70),
        (1180, 1120, -42, 0.62),
        (1880, 1030, 18, 0.66),
        (2580, 1090, -24, 0.68),
        (840, 1720, -28, 0.68),
        (1540, 1780, 34, 0.62),
        (2260, 1690, -16, 0.68),
        (2960, 1775, 31, 0.64),
    ]
    for x, y, angle, scale in pattern_positions:
        paste_watercolor_asset(
            base,
            botanical_path,
            (x, y),
            int(pattern_height * scale),
            pattern_opacity,
            angle,
        )

    paste_watercolor_asset(base, botanical_path, (235, 178), 620, opacity, -28)
    paste_watercolor_asset(base, botanical_path, (width - 245, 188), 560, opacity - 18, 35)
    paste_watercolor_asset(base, botanical_path, (260, height - 165), 520, opacity - 8, 72)
    paste_watercolor_asset(base, botanical_path, (width - 275, height - 155), 520, opacity - 6, -66)


def generate_paper_artwork(path: Path, style: dict, external_paper: Path | None = None, botanical: Path | None = None) -> Path:
    paper = style["paper"]
    width = int(paper["width_px"])
    height = int(paper["height_px"])
    rng = random.Random(style["random_seed"])

    image = Image.new("RGBA", (width, height), (*hex_to_rgb(paper["base_color"]), 255))
    add_paper_texture(image, style, rng)
    draw_modern_background(image, style)
    if paper["external_texture_enabled"] and external_paper:
        blend_external_paper(image, external_paper, paper["external_texture_opacity"])
    draw_watercolor(image, style, rng)
    if botanical:
        draw_external_watercolors(image, style, botanical)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, quality=92, optimize=True)
    return path


def draw_sword_icon(draw: ImageDraw.ImageDraw, color: tuple[int, int, int, int]) -> None:
    draw.polygon([(30, 8), (35, 13), (20, 31), (17, 28)], fill=color)
    draw.line((13, 32, 25, 20), fill=color, width=4)
    draw.line((12, 24, 24, 36), fill=color, width=4)
    draw.ellipse((8, 34, 15, 41), fill=color)


def draw_movement_icon(draw: ImageDraw.ImageDraw, color: tuple[int, int, int, int]) -> None:
    draw.line((8, 28, 28, 28), fill=color, width=5)
    draw.polygon([(28, 17), (42, 28), (28, 39)], fill=color)
    draw.arc((9, 8, 35, 34), start=200, end=330, fill=color, width=4)


def draw_draw_icon(draw: ImageDraw.ImageDraw, color: tuple[int, int, int, int]) -> None:
    draw.ellipse((10, 10, 38, 38), outline=color, width=5)
    draw.ellipse((18, 18, 30, 30), fill=color)


def draw_defense_icon(draw: ImageDraw.ImageDraw, color: tuple[int, int, int, int]) -> None:
    draw.polygon([(24, 7), (40, 14), (36, 35), (24, 43), (12, 35), (8, 14)], fill=color)
    draw.polygon([(24, 12), (34, 17), (31, 32), (24, 37), (17, 32), (14, 17)], fill=(238, 221, 176, 255))


def draw_special_icon(draw: ImageDraw.ImageDraw, color: tuple[int, int, int, int]) -> None:
    cx, cy = 24, 24
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        draw.line((cx, cy, cx + math.cos(rad) * 17, cy + math.sin(rad) * 17), fill=color, width=3)
    draw.ellipse((18, 18, 30, 30), fill=color)


def draw_range_icon(draw: ImageDraw.ImageDraw, color: tuple[int, int, int, int]) -> None:
    draw.ellipse((8, 8, 40, 40), outline=color, width=3)
    draw.ellipse((16, 16, 32, 32), outline=color, width=3)
    draw.line((24, 4, 24, 44), fill=color, width=2)
    draw.line((4, 24, 44, 24), fill=color, width=2)


def draw_accessory_icon(draw: ImageDraw.ImageDraw, color: tuple[int, int, int, int]) -> None:
    draw.arc((8, 10, 40, 38), start=25, end=325, fill=color, width=5)
    draw.ellipse((7, 20, 17, 30), fill=color)
    draw.ellipse((31, 20, 41, 30), fill=color)
    draw.line((17, 25, 31, 25), fill=color, width=4)


def ensure_legend_icons(icons_dir: Path, style: dict) -> None:
    icons_dir.mkdir(parents=True, exist_ok=True)
    colors = style["colors"]
    specs = {
        "use.png": ("@", colors["legend_use"]),
        "attack.png": ("attack", colors["legend_attack"]),
        "movement.png": ("movement", colors["legend_movement"]),
        "draw.png": ("draw", colors["legend_draw"]),
        "defense.png": ("defense", colors["legend_defense"]),
        "special.png": ("special", colors["legend_special"]),
        "range.png": ("range", colors["legend_range"]),
        "accessory.png": ("accessory", colors["legend_accessory"]),
    }
    for filename, (kind, hex_color) in specs.items():
        path = icons_dir / filename
        if path.exists():
            continue
        image = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, "RGBA")
        color = rgba(hex_color, 255)
        if kind == "@":
            draw.ellipse((7, 7, 41, 41), outline=color, width=4)
            draw.arc((15, 12, 35, 35), start=80, end=345, fill=color, width=4)
            draw.line((25, 24, 39, 38), fill=color, width=4)
        elif kind == "attack":
            draw_sword_icon(draw, color)
        elif kind == "movement":
            draw_movement_icon(draw, color)
        elif kind == "draw":
            draw_draw_icon(draw, color)
        elif kind == "defense":
            draw_defense_icon(draw, color)
        elif kind == "special":
            draw_special_icon(draw, color)
        elif kind == "range":
            draw_range_icon(draw, color)
        elif kind == "accessory":
            draw_accessory_icon(draw, color)
        image = image.filter(ImageFilter.GaussianBlur(0.2))
        image.save(path)
