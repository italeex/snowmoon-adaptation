"""Snowmoon #34 — motion-graphics adaptation, Chapter 1.

Source text (GPL v3, Vitalik Buterin, Snowmoon, ch.1):
  "Gladias was walking along a foot path, with tall trees towering on both sides.
   A series of houses made out of large stone bricks lay behind the trees on both
   sides, medieval in style but without any of the junk, dust on the ground, or
   other imperfections that a real medieval structure would have had a thousand
   years earlier."
  ... "another man nearby, also wearing a privacy robe, broke and ran toward the
   fire exit on the right."

Pipeline: procedural frames via PIL/numpy, no AI image generation, no GPU.
Rendered at final size (no downscaling) to avoid RGBA resample fringing.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H, FPS = 1920, 1080, 24
OUT = "/mnt/hermes_data/snowmoon/frames"
FDIR = "/usr/share/fonts/truetype/dejavu"

def F(name, size):
    return ImageFont.truetype(f"{FDIR}/{name}", size)

def lerp(a, b, t):
    return a + (b - a) * t

def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def sky(w, h, t):
    top = np.array([14, 20, 46], float)
    mid = np.array([46, 62, 104], float)
    hor = np.array([104, 116, 140], float)
    g = np.clip(np.linspace(0, 1, h) / 0.55, 0, 1)[:, None]
    img = top[None, None, :] * (1 - g[:, :, None]) + mid[None, None, :] * g[:, :, None]
    g2 = np.clip((np.linspace(0, 1, h) - 0.55) / 0.45, 0, 1)[:, None]
    img = img * (1 - g2[:, :, None]) + hor[None, None, :] * g2[:, :, None]
    img = np.repeat(img, w, axis=1)
    rng = np.random.default_rng(7)
    for _ in range(300):
        x, y = rng.integers(0, w), rng.integers(0, int(h * 0.5))
        b = rng.random() * 0.55 + 0.45
        img[y, (x + int(t * 1.2)) % w] += 165 * b
    return img

def house(d, x, base, sw, sh, depth, lit):
    warm = (255, 196, 118)
    stone = (58 + int(depth * 26), 56 + int(depth * 24), 60 + int(depth * 22))
    top = base - sh
    d.rectangle([x, top, x + sw, base], fill=stone, outline=(30, 29, 33))
    ch = max(7, int(sh / 7))
    for r in range(int(top) + ch, int(base), ch):
        d.line([(x, r), (x + sw, r)], fill=(stone[0] - 7, stone[1] - 7, stone[2] - 7))
    d.polygon([(x - sw * 0.10, top), (x + sw / 2, top - sh * 0.34), (x + sw * 1.10, top)],
              fill=(42 - int(depth * 8), 38 - int(depth * 8), 42 - int(depth * 8)))
    dw = max(9, int(sw * 0.20)); dh = max(16, int(sh * 0.34))
    dx = x + sw / 2 - dw / 2
    # door: recessed frame + lit inner edge, so it cannot be mistaken for a window
    d.rectangle([dx - 4, base - dh - 5, dx + dw + 4, base + 3], fill=(24, 22, 26))
    d.rectangle([dx, base - dh, dx + dw, base], fill=(34, 25, 20))
    if lit:
        d.rectangle([dx + 3, base - dh + 4, dx + dw - 3, base - 4], fill=warm)
        d.line([(dx + dw * 0.72, base - dh * 0.55), (dx + dw * 0.72, base - dh * 0.42)],
               fill=(60, 40, 24), width=max(1, int(dw * 0.10)))
    else:
        d.line([(dx, base - dh), (dx, base)], fill=(44, 32, 24), width=max(1, int(dw * 0.14)))
    rows = 2 if sh > 150 else 1
    cols = 2 if sw > 110 else 1
    ww = max(8, int(sw * 0.17)); wh = max(9, int(sh / (rows * 2.6)))
    for r in range(rows):
        for c in range(cols):
            wx = x + sw * (0.18 + c * 0.46)
            wy = top + sh * (0.16 + r * 0.34)
            on = lit and ((r * 3 + c * 5 + int(x)) % 3 != 0)
            d.rectangle([wx, wy, wx + ww, wy + wh],
                        fill=warm if on else (26, 28, 34), outline=(22, 21, 24))
            if on:
                d.rectangle([wx - 5, wy - 5, wx + ww + 5, wy + wh + 5], outline=(120, 92, 48))

def street(w, h, t):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    vx, vy = w * 0.52, h * 0.44
    d.rectangle([0, h * 0.56, w, h], fill=(44, 42, 44, 255))
    for i in range(9):
        near = (i + 1) / 9
        sw = lerp(52, 300, near ** 1.9)
        sh = lerp(70, 430, near ** 2.0)
        base = lerp(vy + 8, h * 0.99, near ** 1.35)
        for side in (-1, 1):
            if side < 0 and i % 2 == 0:
                continue
            if side > 0 and i % 2 == 1:
                continue
            gap = lerp(6, 26, near)
            cx = vx + side * (lerp(34, w * 0.30, near ** 1.5) + sw / 2 + gap)
            house(d, cx - sw / 2, base, sw, sh, 1 - near, lit=(i % 3 != 0))
    for side in (-1, 1):
        for i in range(6):
            near = (i + 1) / 6
            tx = vx + side * lerp(70, w * 0.40, near ** 1.6)
            th = lerp(90, h * 1.05, near ** 1.25)
            tw = lerp(10, 46, near)
            sway = np.sin(t * 0.6 + i * 1.3 + (0 if side < 0 else 1.7)) * 6 * near
            trunk = (16, 22, 20, 255)
            d.polygon([(tx - tw * 0.5 + sway, h), (tx - tw * 0.34 + sway, h - th * 0.62),
                       (tx + tw * 0.34 + sway, h - th * 0.62), (tx + tw * 0.5 + sway, h)],
                      fill=trunk)
            for k in range(6):
                cy = h - th * (0.58 + k * 0.072)
                cr = tw * (2.9 - k * 0.33)
                d.ellipse([tx - cr + sway, cy - cr * 0.46, tx + cr + sway, cy + cr * 0.46],
                          fill=(13, 19, 18, 255))
                d.ellipse([tx - cr * 0.6 + sway - 3, cy - cr * 0.5, tx - cr * 0.1 + sway, cy],
                          fill=(20, 27, 25, 255))
    d.polygon([(w * 0.30, h), (w * 0.74, h), (vx + 20, vy), (vx - 20, vy)],
              fill=(78, 74, 72, 255))
    for i in range(20):
        f = i / 20
        y = lerp(h, vy, f ** 1.75)
        hw = lerp(w * 0.22, 6, f ** 1.75)
        sh2 = int(lerp(96, 26, f))
        d.rectangle([vx - hw, y - 2, vx + hw, y + 2], fill=(sh2, sh2 - 6, sh2 - 12, 150))
    for i in range(46):
        f = (i * 0.137) % 1
        y = lerp(h, vy, f ** 1.75)
        hw = lerp(w * 0.22, 6, f ** 1.75)
        x = lerp(vx - hw, vx + hw, (i * 0.379) % 1)
        r = lerp(9, 1.6, f)
        d.ellipse([x - r, y - r * 0.4, x + r, y + r * 0.4], fill=(66, 63, 62, 210))
    return img

def exit_sign(w, h, t, inten):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    vx, vy = w * 0.52, h * 0.44
    pulse = 0.84 + np.sin(t * 2.6) * 0.16
    for r in range(420, 0, -12):
        k = 1 - r / 420
        dl.ellipse([vx - r, vy - r * 0.66, vx + r, vy + r * 0.66],
                   fill=(24, int(190 * k * inten), 108, int(150 * k * inten * pulse)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(img)
    d.rectangle([vx - 74, vy - 26, vx + 74, vy + 96], fill=(24, 30, 30, 255),
                outline=(70, 76, 74, 255))
    d.rectangle([vx - 58, vy - 8, vx + 58, vy + 96], fill=(12, 26, 20, 255))
    d.rounded_rectangle([vx - 58, vy - 46, vx + 58, vy - 6], radius=5,
                        fill=(16, 44, 28, 255), outline=(40, 120, 70, 255))
    d.text((vx, vy - 26), "EXIT", font=F("DejaVuSans-Bold.ttf", 30),
           fill=(130, 255, 176, int(255 * pulse * inten)), anchor="mm")
    return img

def runner(scale, phase, robe, running, warm):
    S = scale
    Wc, Hc = int(210 * S), int(330 * S)
    img = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lean = 20 * S if running else 0
    cloth = (58, 48, 78, 255) if robe else (36, 44, 62, 255)
    cx = Wc / 2
    stride = np.sin(phase * 8.5) * 40 * S if running else 0
    lw = max(3, int(15 * S))
    d.line([cx, Hc * 0.72, cx - 34 * S - stride, Hc * 0.98], fill=cloth, width=lw)
    d.line([cx, Hc * 0.72, cx + 34 * S - stride, Hc * 0.98], fill=cloth, width=lw)
    d.polygon([(cx - 30 * S + lean, Hc * 0.30), (cx + 30 * S + lean, Hc * 0.30),
               (cx + 46 * S, Hc * 0.74), (cx - 46 * S, Hc * 0.74)], fill=cloth)
    d.line([(cx + 20 * S + lean, Hc * 0.34), (cx + 24 * S, Hc * 0.62)],
           fill=tuple(max(0, c - 14) for c in cloth[:3]) + (255,), width=max(2, int(6 * S)))
    aw = max(2, int(11 * S))
    d.line([cx + 16 * S + lean, Hc * 0.36, cx + 56 * S + stride * 0.45, Hc * 0.52],
           fill=cloth, width=aw)
    d.line([cx - 16 * S + lean, Hc * 0.36, cx - 48 * S - stride * 0.35, Hc * 0.56],
           fill=cloth, width=aw)
    hr = 25 * S
    d.ellipse([cx - hr * 0.92 + lean, Hc * 0.30 - hr * 1.05, cx + hr * 0.92 + lean, Hc * 0.30 + hr * 0.95],
              fill=(214, 180, 152, 255))
    d.pieslice([cx - hr * 1.12 + lean, Hc * 0.30 - hr * 1.30, cx + hr * 1.12 + lean, Hc * 0.30 + hr * 0.62],
               180, 360, fill=cloth)
    if warm:
        d.arc([cx - hr * 0.92 + lean, Hc * 0.30 - hr * 1.05, cx + hr * 0.92 + lean, Hc * 0.30 + hr * 0.95],
              -80, 40, fill=(120, 255, 176, 190), width=max(1, int(3 * S)))
        d.line([(cx + 30 * S + lean, Hc * 0.32), (cx + 46 * S, Hc * 0.73)],
               fill=(96, 220, 150, 130), width=max(1, int(4 * S)))
    return img

def grade(arr, warm=0.0):
    a = arr.astype(float) / 255
    a = np.clip((a - 0.5) * 1.10 + 0.5, 0, 1)
    a = a * 0.94 + 0.055
    lum = a @ np.array([0.2126, 0.7152, 0.0722])
    a[..., 0] += (lum ** 2) * 0.10 + warm * 0.05
    a[..., 1] += (lum ** 2) * 0.055
    a[..., 2] += (1 - lum) * 0.05
    return np.clip(a * 255, 0, 255).astype(np.uint8)

def vignette(arr, s=0.42):
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    m = np.clip(1 - s * np.clip(r - 0.55, 0, None) ** 1.6 * 2.1, 0, 1)
    return (arr * m[:, :, None]).astype(np.uint8)

LINES = [
    (0.2, 3.6, "Gladias was walking along a foot path, with tall trees\ntowering on both sides."),
    (3.4, 7.0, "A series of houses made out of large stone bricks lay\nbehind the trees on both sides, medieval in style"),
    (6.8, 10.0, "but without any of the junk, dust on the ground,\nor other imperfections."),
]

def caption(rgb, t):
    for a, b, txt in LINES:
        al = float(np.clip(min((t - a) / 0.7, (b - t) / 0.9), 0, 1))
        if al <= 0.01:
            continue
        rgba = rgb.convert("RGBA")
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        f = F("DejaVuSerif.ttf", 34)
        for dy in (-2, 2):
            d.text((W / 2, H * 0.855 + dy), txt, font=f, fill=(0, 0, 0, int(190 * al)),
                   anchor="mm", align="center")
        d.text((W / 2, H * 0.855), txt, font=f, fill=(240, 236, 226, int(255 * al)),
               anchor="mm", align="center")
        rgba.alpha_composite(layer)
        rgb = rgba.convert("RGB")
    return rgb

def frame(n):
    t = n / FPS
    base = Image.fromarray(sky(W, H, t).astype(np.uint8)).convert("RGBA")
    base.alpha_composite(street(W, H, t))
    f = ease(np.clip(t / 5.4, 0, 1))
    gi = lerp(0.20, 1.0, ease(np.clip((t - 0.5) / 3.2, 0, 1)))
    base.alpha_composite(exit_sign(W, H, t, gi))
    if t < 2.6:
        a = float(np.clip(1 - (t - 1.5) / 1.1, 0, 1))
        g = runner(1.15, t * 0.3, robe=True, running=False, warm=False)
        g.putalpha(g.getchannel("A").point(lambda v: int(v * a)))
        base.alpha_composite(g, (int(W * 0.10), int(H * 0.90 - g.height)))
    # He must stay the largest human form on screen early on, or he reads
    # as background clutter (v1 review: "marginal pass").
    fx = lerp(W * 0.34, W * 0.455, f)
    fy = lerp(H * 1.02, H * 0.50, f ** 1.25)
    sc = lerp(2.05, 0.34, ease(np.clip(t / 5.4, 0, 1)) ** 0.95)
    fig = runner(sc, t, robe=False, running=True, warm=t > 0.9)
    base.alpha_composite(fig, (int(fx - fig.width / 2), int(fy - fig.height * 0.99)))
    out = np.array(base.convert("RGB"))
    out = grade(out, warm=f * 0.6)
    out = vignette(out, 0.34 + 0.16 * (1 - f))
    return Image.fromarray(out)

def main():
    os.makedirs(OUT, exist_ok=True)
    for old in os.listdir(OUT):
        os.remove(os.path.join(OUT, old))
    n_tot = int(10.0 * FPS)
    for n in range(n_tot):
        frame(n).save(f"{OUT}/f{n:05d}.jpg", quality=92)
        if n % 60 == 0:
            print(f"  {n}/{n_tot}", flush=True)
    print("frames:", len(os.listdir(OUT)))

if __name__ == "__main__":
    main()