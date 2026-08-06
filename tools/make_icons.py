#!/usr/bin/env python3
"""Generate all PWA + iOS icons for the Mongolian Bible reader."""
from PIL import Image, ImageDraw
import os

BLUE = (30, 61, 92)        # --blue-deep
PAPER = (246, 247, 245)
EDGE = (200, 212, 226)
CROSS  = (214, 178, 92)    # warm gold, reads on navy and on the white page

OUT = 'site/icons'
os.makedirs(OUT, exist_ok=True)
S = 1024


def draw_mark(bg=True, pad=0.16):
    """Open book in the lower half, large cross rising over it."""
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if bg:
        d.rounded_rectangle([0, 0, S, S], radius=int(S * 0.22), fill=BLUE)

    inner = S * (1 - 2 * pad)
    cx = S / 2
    cy = S / 2 + inner * 0.20          # book sits low, leaving room for the cross
    hw = inner * 0.50
    hh = inner * 0.20
    lift = hh * 0.42

    def curve(t, side):
        x = cx + side * hw * t
        return x, lift * (t ** 1.7)

    for side in (-1, 1):
        top, bot = [], []
        for i in range(13):
            t = i / 12
            x, dy = curve(t, side)
            top.append((x, cy - hh * 0.78 - dy))
            bot.append((x, cy + hh * 0.86 - dy * 0.55))
        poly = top + bot[::-1]
        d.polygon(poly, fill=PAPER)
        d.line(bot, fill=EDGE, width=max(2, int(S * 0.008)))

    lw = max(2, int(S * 0.017))
    for side in (-1, 1):
        for i in range(4):
            y = cy - hh * 0.40 + i * hh * 0.40
            for t0, t1 in [(0.20, 0.90)]:
                x0, d0 = curve(t0, side)
                x1, d1 = curve(t1 - (0.10 if i == 3 else 0), side)
                d.line([(x0, y - d0), (x1, y - d1)], fill=EDGE, width=lw)

    d.line([(cx, cy - hh * 0.80), (cx, cy + hh * 0.86)],
           fill=EDGE, width=max(2, int(S * 0.010)))

    # ---- cross, drawn last so it sits over the book ----
    bw = inner * 0.115                      # bar thickness
    top_y = S / 2 - inner * 0.50
    foot_y = cy + hh * 0.30
    arm_y = top_y + inner * 0.235
    arm_hw = inner * 0.245
    r = bw * 0.16
    d.rounded_rectangle([cx - bw / 2, top_y, cx + bw / 2, foot_y], radius=r, fill=CROSS)
    d.rounded_rectangle([cx - arm_hw, arm_y, cx + arm_hw, arm_y + bw], radius=r, fill=CROSS)
    return img


standard = draw_mark(bg=True, pad=0.15)
maskable = draw_mark(bg=True, pad=0.25)          # safe zone for Android masking

jobs = [
    ('icon-192.png', standard, 192), ('icon-256.png', standard, 256),
    ('icon-384.png', standard, 384), ('icon-512.png', standard, 512),
    ('maskable-192.png', maskable, 192), ('maskable-512.png', maskable, 512),
    ('apple-touch-icon.png', standard, 180),     # iOS home screen
    ('apple-touch-icon-152.png', standard, 152), # older iPad
    ('apple-touch-icon-167.png', standard, 167), # iPad Pro
    ('favicon-32.png', standard, 32), ('favicon-16.png', standard, 16),
]
for name, src, size in jobs:
    im = src.resize((size, size), Image.LANCZOS)
    if name.startswith('apple') or name.startswith('favicon'):
        flat = Image.new('RGB', (size, size), BLUE)   # iOS ignores alpha
        flat.paste(im, (0, 0), im)
        im = flat
    im.save(f'{OUT}/{name}')
    print(name, size)

ico = standard.resize((64, 64), Image.LANCZOS)
ico.save('site/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
print('favicon.ico')
