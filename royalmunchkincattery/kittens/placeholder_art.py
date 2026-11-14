"""Procedural kitten illustrations used for demo data, the social-share image
and app icons. Real photos should replace these via the dashboard: the seed
command is for local development and design review only.

Pure Pillow, no network, deterministic output.
"""

import math
import random
from io import BytesIO

from PIL import Image, ImageChops, ImageDraw, ImageFilter

PALETTE = {
    "black": ((46, 42, 56), (28, 25, 36)),
    "white": ((250, 247, 244), (226, 220, 222)),
    "blue": ((142, 150, 170), (110, 118, 140)),
    "cream": ((242, 222, 188), (222, 196, 156)),
    "red": ((226, 142, 72), (190, 104, 44)),
    "chocolate": ((118, 80, 66), (88, 58, 48)),
    "lilac": ((186, 170, 186), (152, 136, 156)),
    "silver": ((190, 192, 200), (140, 142, 154)),
    "brown": ((150, 112, 78), (96, 68, 46)),
    "tricolor": ((250, 247, 244), (226, 220, 222)),
}
EYES = {
    "gold": (232, 178, 52), "green": (118, 178, 96), "copper": (196, 118, 52),
    "blue": (96, 162, 220), "hazel": (160, 140, 70), "odd": (96, 162, 220),
}
BACKGROUNDS = [
    ((236, 228, 250), (248, 218, 226)),
    ((226, 238, 250), (236, 226, 250)),
    ((250, 234, 222), (240, 224, 246)),
    ((222, 244, 238), (232, 230, 252)),
]
SS = 2  # supersampling factor


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size, top)
    px = ImageDraw.Draw(img)
    for y in range(h):
        px.line([(0, y), (w, y)], fill=_lerp(top, bottom, y / max(1, h - 1)))
    return img


def _ellipse_mask(size, box):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    return m


def _poly_mask(size, pts):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def draw_kitten(
    size=1000, color="red", pattern="tabby", eye="gold", longhair=False,
    bg_index=0, seed=1, pose="portrait", tint_ears=True,
):
    rnd = random.Random(seed)
    W = H = size * SS
    fur, shade = PALETTE.get(color, PALETTE["cream"])
    eye_rgb = EYES.get(eye, EYES["gold"])
    bg_top, bg_bot = BACKGROUNDS[bg_index % len(BACKGROUNDS)]

    img = _gradient((W, H), bg_top, bg_bot).convert("RGBA")

    # soft bokeh
    bokeh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bokeh)
    for _ in range(9):
        r = rnd.randint(int(W * 0.04), int(W * 0.11))
        x, y = rnd.randint(0, W), rnd.randint(0, int(H * 0.6))
        bd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(40, 90)))
    img = Image.alpha_composite(img, bokeh.filter(ImageFilter.GaussianBlur(W * 0.004)))

    zoom = 1.28 if pose == "close" else 1.0
    cx, cy = W * 0.5, H * (0.50 if pose == "close" else 0.47)
    head_w, head_h = W * 0.50 * zoom, H * 0.40 * zoom

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # ---- body (low-slung, short legs) -----------------------------------
    if pose != "close":
        body_box = [cx - W * 0.30, cy + head_h * 0.15, cx + W * 0.30, cy + H * 0.46]
        d.ellipse(body_box, fill=fur)
        # tail curling up behind (tapering circles read as a soft, plumed tail)
        n = 46
        for i in range(n):
            t = i / (n - 1)
            x = cx + W * 0.24 + math.sin(t * 2.3) * W * 0.06 + t * W * 0.10
            y = cy + H * 0.33 - t * H * 0.30
            r = W * (0.040 - 0.012 * t) * (1.35 if longhair else 1.0)
            col = fur if t < 0.86 else shade
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        # tiny front legs and paws: the Munchkin signature
        leg_y = cy + H * 0.36
        for dx in (-0.12, 0.12):
            d.rounded_rectangle([cx + W * dx - W * 0.055, leg_y - H * 0.02, cx + W * dx + W * 0.055, leg_y + H * 0.09], radius=W * 0.05, fill=fur)
            d.ellipse([cx + W * dx - W * 0.065, leg_y + H * 0.05, cx + W * dx + W * 0.065, leg_y + H * 0.11], fill=fur if pattern != "bicolor" else (250, 247, 244))
            for k in (-1, 0, 1):
                d.line([(cx + W * dx + k * W * 0.02, leg_y + H * 0.085), (cx + W * dx + k * W * 0.02, leg_y + H * 0.105)], fill=shade, width=max(2, int(W * 0.004)))

    # ---- ears -----------------------------------------------------------
    ear_h = head_h * 0.62
    for side in (-1, 1):
        base_x = cx + side * head_w * 0.30
        pts = [
            (cx + side * head_w * 0.52, cy - head_h * 0.20),
            (cx + side * head_w * 0.46, cy - head_h * 0.20 - ear_h),
            (cx + side * head_w * 0.10, cy - head_h * 0.45),
        ]
        d.polygon(pts, fill=fur)
        inner = [
            (cx + side * head_w * 0.44, cy - head_h * 0.26),
            (cx + side * head_w * 0.42, cy - head_h * 0.20 - ear_h * 0.70),
            (cx + side * head_w * 0.20, cy - head_h * 0.42),
        ]
        d.polygon(inner, fill=(236, 168, 176) if tint_ears else shade)

    # ---- head (with fluffy cheek ruff for longhair) ---------------------
    head_box = [cx - head_w / 2, cy - head_h / 2, cx + head_w / 2, cy + head_h / 2]
    d.ellipse(head_box, fill=fur)
    if longhair:
        for side in (-1, 1):
            for j in range(5):
                ry = cy + head_h * (0.10 + j * 0.07)
                d.polygon([
                    (cx + side * head_w * 0.42, ry - head_h * 0.07),
                    (cx + side * head_w * (0.60 - j * 0.02), ry + head_h * 0.02),
                    (cx + side * head_w * 0.40, ry + head_h * 0.07),
                ], fill=fur)

    head_mask = _ellipse_mask((W, H), head_box)
    silhouette = layer.split()[3]
    head_and_ears = ImageChops.lighter(head_mask, silhouette)

    # ---- patterns, clipped to the silhouette ----------------------------
    pat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pat)
    stripe = shade + (235,)
    if pattern in ("tabby", "smoke"):
        for i, dx in enumerate((-0.12, 0.0, 0.12)):
            x = cx + head_w * dx
            pd.line([(x, cy - head_h * 0.50), (x + head_w * dx * 0.3, cy - head_h * 0.20)], fill=stripe, width=int(W * 0.018))
        for side in (-1, 1):
            for k in range(3):
                y = cy + head_h * (0.02 + k * 0.09)
                pd.line([(cx + side * head_w * 0.50, y), (cx + side * head_w * 0.30, y + head_h * 0.03)], fill=stripe, width=int(W * 0.014))
        if pose != "close":
            for k in range(5):
                y = cy + head_h * 0.35 + k * H * 0.055
                pd.arc([cx - W * 0.28, y, cx + W * 0.28, y + H * 0.10], 200, 340, fill=stripe, width=int(W * 0.014))
    elif pattern in ("calico", "tortie"):
        patches = [((0.30, 0.18), (28, 25, 36), 0.30), ((0.72, 0.30), (222, 138, 66), 0.26), ((0.58, 0.82), (28, 25, 36), 0.30), ((0.20, 0.62), (222, 138, 66), 0.22)]
        if pattern == "tortie":
            patches += [((0.45, 0.40), (222, 138, 66), 0.30), ((0.60, 0.15), (28, 25, 36), 0.22)]
        for (px, py), col, rr in patches:
            bx, by = cx - head_w * 0.5 + head_w * px, cy - head_h * 0.5 + head_h * py
            r = head_w * rr * 0.55
            pd.ellipse([bx - r, by - r * 0.85, bx + r, by + r * 0.85], fill=col + (255,))
        pd.ellipse([cx - head_w * 0.12, cy - head_h * 0.34, cx + head_w * 0.12, cy + head_h * 0.20], fill=(250, 247, 244, 255))
    elif pattern == "bicolor":
        pd.ellipse([cx - head_w * 0.30, cy - head_h * 0.02, cx + head_w * 0.30, cy + head_h * 0.52], fill=(250, 247, 244, 255))
        pd.polygon([(cx, cy - head_h * 0.50), (cx - head_w * 0.07, cy), (cx + head_w * 0.07, cy)], fill=(250, 247, 244, 255))
        if pose != "close":
            pd.ellipse([cx - W * 0.17, cy + H * 0.14, cx + W * 0.17, cy + H * 0.40], fill=(250, 247, 244, 255))
    elif pattern == "colorpoint":
        pd.ellipse([cx - head_w * 0.28, cy - head_h * 0.02, cx + head_w * 0.28, cy + head_h * 0.46], fill=shade + (255,))
        for side in (-1, 1):
            pd.polygon([
                (cx + side * head_w * 0.52, cy - head_h * 0.20),
                (cx + side * head_w * 0.46, cy - head_h * 0.20 - ear_h),
                (cx + side * head_w * 0.10, cy - head_h * 0.45),
            ], fill=shade + (255,))
    elif pattern == "solid" and color == "black":
        pass

    clipped = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    clipped.paste(pat, (0, 0), head_and_ears)
    layer = Image.alpha_composite(layer, clipped)
    d = ImageDraw.Draw(layer)

    # ---- face ------------------------------------------------------------
    eye_r = head_w * 0.095
    for side in (-1, 1):
        ex, ey = cx + side * head_w * 0.22, cy - head_h * 0.02
        e_rgb = eye_rgb if not (eye == "odd" and side == 1) else EYES["gold"]
        d.ellipse([ex - eye_r, ey - eye_r * 1.12, ex + eye_r, ey + eye_r * 1.12], fill=(255, 255, 255))
        d.ellipse([ex - eye_r * 0.92, ey - eye_r * 1.02, ex + eye_r * 0.92, ey + eye_r * 1.02], fill=e_rgb)
        d.ellipse([ex - eye_r * 0.30, ey - eye_r * 0.92, ex + eye_r * 0.30, ey + eye_r * 0.92], fill=(24, 20, 30))
        d.ellipse([ex - eye_r * 0.50, ey - eye_r * 0.62, ex - eye_r * 0.08, ey - eye_r * 0.20], fill=(255, 255, 255))
    ny = cy + head_h * 0.14
    nose_col = (226, 138, 152) if color not in ("black",) else (170, 110, 124)
    d.polygon([(cx - head_w * 0.035, ny), (cx + head_w * 0.035, ny), (cx, ny + head_h * 0.045)], fill=nose_col)
    mouth = (80, 60, 70)
    lw = max(3, int(W * 0.004))
    d.line([(cx, ny + head_h * 0.045), (cx, ny + head_h * 0.095)], fill=mouth, width=lw)
    d.arc([cx - head_w * 0.085, ny + head_h * 0.05, cx, ny + head_h * 0.15], 20, 160, fill=mouth, width=lw)
    d.arc([cx, ny + head_h * 0.05, cx + head_w * 0.085, ny + head_h * 0.15], 20, 160, fill=mouth, width=lw)
    for side in (-1, 1):
        for k, dy in enumerate((-0.015, 0.02, 0.055)):
            y0 = ny + head_h * (0.06 + dy)
            d.line([(cx + side * head_w * 0.14, y0), (cx + side * head_w * 0.42, y0 + (k - 1) * head_h * 0.03)], fill=(255, 255, 255, 200), width=lw)

    # soft ground shadow sits under the kitten
    if pose != "close":
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([cx - W * 0.32, H * 0.90, cx + W * 0.32, H * 0.96], fill=(60, 30, 90, 56))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(W * 0.012)))
    img = Image.alpha_composite(img, layer)

    return img.convert("RGB").resize((size, size), Image.LANCZOS)


def to_jpeg_bytes(img, quality=86):
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue()


def og_image(path, width=1200, height=630):
    """Branded social-share card: crown mark, wordmark and price promise."""
    from PIL import ImageFont

    img = _gradient((width, height), (43, 22, 66), (91, 58, 154)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for i in range(7):
        r = 120 + i * 70
        d.ellipse([width - 260 - r, -140 - r // 3, width - 260 + r, -140 + r], outline=(255, 255, 255, 14), width=2)
    kitten = draw_kitten(520, color="red", pattern="tabby", eye="green", seed=11, bg_index=1)
    mask = Image.new("L", kitten.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, kitten.size[0], kitten.size[1]], radius=260, fill=255)
    arch = Image.new("L", kitten.size, 0)
    ad = ImageDraw.Draw(arch)
    ad.ellipse([0, 0, kitten.size[0], kitten.size[0]], fill=255)
    ad.rectangle([0, kitten.size[0] // 2, kitten.size[0], kitten.size[1]], fill=255)
    ad.rounded_rectangle([0, kitten.size[0] // 2, kitten.size[0], kitten.size[1]], radius=36, fill=255)
    img.paste(kitten, (width - 590, 55), arch)

    def font(size, bold=False):
        for name in ("/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf" if bold else "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    gold = (222, 178, 74)
    # crown with cat ears
    cx, cy = 118, 150
    d.polygon([(cx - 56, cy + 34), (cx - 62, cy - 34), (cx - 28, cy - 4), (cx, cy - 46), (cx + 28, cy - 4), (cx + 62, cy - 34), (cx + 56, cy + 34)], fill=gold)
    d.rectangle([cx - 56, cy + 34, cx + 56, cy + 48], fill=(244, 206, 112))
    for dx in (-30, 0, 30):
        d.ellipse([cx + dx - 6, cy + 10, cx + dx + 6, cy + 22], fill=(43, 22, 66))
    d.text((60, 235), "Royal Munchkin", font=font(66, True), fill=(255, 255, 255))
    d.text((60, 325), "Cattery", font=font(66, True), fill=gold)
    d.text((62, 440), "Home-raised Munchkin kittens", font=font(34), fill=(226, 214, 246))
    d.rounded_rectangle([60, 505, 330, 565], radius=30, fill=gold)
    d.text((86, 517), "$800 - $1,000", font=font(32, True), fill=(43, 22, 66))
    img.convert("RGB").save(path, "PNG", optimize=True)


def apple_icon(path, size=180):
    img = Image.new("RGB", (size, size), (43, 22, 66))
    d = ImageDraw.Draw(img)
    s = size / 180
    gold = (222, 178, 74)
    cx, cy = 90 * s, 92 * s
    d.polygon([(cx - 46 * s, cy + 28 * s), (cx - 52 * s, cy - 30 * s), (cx - 22 * s, cy - 4 * s), (cx, cy - 40 * s), (cx + 22 * s, cy - 4 * s), (cx + 52 * s, cy - 30 * s), (cx + 46 * s, cy + 28 * s)], fill=gold)
    d.rectangle([cx - 46 * s, cy + 28 * s, cx + 46 * s, cy + 42 * s], fill=(244, 206, 112))
    img.save(path, "PNG", optimize=True)
