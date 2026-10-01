"""Snowmoon #34 — Chapter 1, full short film (47s, four shots).

Supersedes render.py's 10-second single shot: the bounty judges a "finished
audiovisual piece" on storytelling, atmosphere and technical execution, and ten
seconds is too thin to show any of that.

Every pixel is drawn procedurally with PIL/numpy at final 1920x1080. No AI image
generation, no GPU, no downloaded assets. Seeded, so output is reproducible.

Shots
  1  (0-10s)  the foot path, the houses, the run for the exit   [reuses render.py]
  2  (10-24s) the Order's guessing game: a node net, a guess travelling
              with a deposit, a salary bar draining on a correct guess
  3  (24-36s) privacy robes: a crowd of identical masked figures, one breaks
              formation and runs
  4  (36-47s) the same street at dawn, empty, the exit sign dark

Run:  python3 render_full.py
Out:  /mnt/hermes_data/snowmoon/frames_full/f%05d.jpg
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R  # shot 1 and the shared grading/figure helpers

W, H, FPS = R.W, R.H, R.FPS
FULL = "/mnt/hermes_data/snowmoon/frames_full"
SHOTS = [(0, 10), (10, 24), (24, 36), (36, 47)]
DUR = 47.0


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def grade(a, warm=0.0, lift=0.055, contrast=1.10):
    x = a.astype(float) / 255
    x = np.clip((x - 0.5) * contrast + 0.5, 0, 1)
    x = x * (1 - lift) + lift
    lum = x @ np.array([0.2126, 0.7152, 0.0722])
    x[..., 0] += (lum ** 2) * 0.10 + warm * 0.05
    x[..., 1] += (lum ** 2) * 0.055
    x[..., 2] += (1 - lum) * 0.05
    return np.clip(x * 255, 0, 255).astype(np.uint8)


def cap(rgb, t, lines):
    """lines: list of (start, end, text). Fades each in and out."""
    for a, b, txt in lines:
        al = float(np.clip(min((t - a) / 0.7, (b - t) / 0.9), 0, 1))
        if al <= 0.01:
            continue
        rgba = rgb.convert("RGBA")
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        f = R.F("DejaVuSerif.ttf", 34)
        for dy in (-2, 2):
            d.text((W / 2, H * 0.855 + dy), txt, font=f, fill=(0, 0, 0, int(190 * al)),
                   anchor="mm", align="center")
        d.text((W / 2, H * 0.855), txt, font=f, fill=(240, 236, 226, int(255 * al)),
               anchor="mm", align="center")
        rgba.alpha_composite(layer)
        rgb = rgba.convert("RGB")
    return rgb


# ---------------------------------------------------------------- shot 2
def dawn_sky(t, morning=False):
    if morning:
        top = np.array([44, 58, 96], float)
        mid = np.array([116, 122, 152], float)
        hor = np.array([222, 196, 172], float)
    else:
        top = np.array([8, 11, 26], float)
        mid = np.array([30, 40, 74], float)
        hor = np.array([58, 70, 108], float)
    h = H
    g = np.clip(np.linspace(0, 1, h) / 0.55, 0, 1)[:, None]
    img = top[None, None, :] * (1 - g[:, :, None]) + mid[None, None, :] * g[:, :, None]
    g2 = np.clip((np.linspace(0, 1, h) - 0.55) / 0.45, 0, 1)[:, None]
    img = img * (1 - g2[:, :, None]) + hor[None, None, :] * g2[:, :, None]
    return np.repeat(img, W, axis=1)


RING = np.random.default_rng(41)
_NN = 26
_ANG = np.linspace(0, 2 * np.pi, _NN, endpoint=False) + 0.21
_RAD = 600 + RING.normal(0, 26, _NN)
NODES = [(W / 2 + np.cos(a) * r, H * 0.50 + np.sin(a) * r * 0.62) for a, r in zip(_ANG, _RAD)]
CENTRE = (W / 2, H * 0.50)
# The book says "decentralised". A hub-and-spoke diagram contradicts the
# subtitle it is drawn under, so the guess routes node -> node around the ring
# and only a thin, dimmed relay sits at the centre. No authoritative hub.
EDGES = [(i, (i + 1) % _NN) for i in range(_NN)]
EDGES += [(3, 9), (5, 14), (11, 20), (17, 24), (2, 12), (7, 18), (1, 22)]
SPOKES = [(0, "c"), (1, "c"), (2, "c"), (3, "c"), (4, "c"), (5, "c"), (6, "c"), (7, "c"),
          (8, "c"), (9, "c"), (10, "c"), (11, "c"), (12, "c"), (13, "c"), (14, "c"),
          (15, "c"), (16, "c"), (17, "c"), (18, "c"), (19, "c"), (20, "c"), (21, "c"),
          (22, "c"), (23, "c"), (24, "c"), (25, "c")]
EDGES += SPOKES
TARGET = 9
SOURCE = 3

L2 = [
    (0.4, 4.6, "To make sure that Order members take their privacy seriously,\nthey were kept on their toes by a sort of deliberately engineered game."),
    (4.4, 9.2, "Anyone can connect to the decentralised cryptographic network\nthat manages the Order's operations, and send in a guess about"),
    (8.8, 13.6, "what a particular Order member's assigned task is,\nalong with a small deposit."),
    (10.2, 14.0, "If their guess is correct, the Order member's salary is docked,\nand the discoverer gets half as a reward."),
]


def shot2(n):
    t = n / FPS
    img = Image.fromarray(dawn_sky(t).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)

    # ground haze so the net floats rather than sits flat
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(gl)
    for i in range(30):
        f = i / 30
        y = H * (0.62 + 0.012 * f)
        dg.ellipse([-200 + f * 300, y - 10, W + 200 - f * 300, y + 10],
                   fill=(40, 52, 86, int(26 + 30 * (1 - f))))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(18)))

    # edges: ring and chords bright, spokes thin and dimmed — the centre is a
    # relay, not an authority, so it must not read as a hub
    for a, b in EDGES:
        if b == "c":
            p1, p2 = NODES[a], CENTRE
            d.line([p1, p2], fill=(48, 58, 92, 70), width=1)
        else:
            d.line([NODES[a], NODES[b]], fill=(66, 82, 126, 160), width=2)

    # the guess travels node -> node around the ring and never through the centre,
    # so the diagram cannot be misread as centralised
    loop = (t % 6.0) / 6.0
    path = [SOURCE, 8, 10, 12, 14, TARGET]
    seglen = len(path) - 1
    seg = min(int(loop * seglen), seglen - 1)
    p = loop * seglen - seg
    a, b = NODES[path[seg]], NODES[path[seg + 1]]
    px, py = lerp(a[0], b[0], p), lerp(a[1], b[1], p)
    strike = loop > 0.995
    # comet trail: the last three nodes' worth of the path, dimming behind
    for k in range(1, 4):
        pp = (loop * seglen - k * 0.14) % seglen
        sg = min(int(pp), seglen - 1)
        aa, bb = NODES[path[sg]], NODES[path[sg + 1]]
        q = pp - sg
        tx, ty = lerp(aa[0], bb[0], q), lerp(aa[1], bb[1], q)
        d.line([px, py, tx, ty], fill=(255, 196, 118, int(120 / k)), width=int(7 / k))

    # nodes: breathing, target reddens after a correct guess
    for i, (x, y) in enumerate(NODES):
        r = 15 + 3 * np.sin(t * 1.4 + i * 0.7)
        if i == TARGET and loop > 0.5:
            glow = (loop - 0.5) / 0.5
            col = (int(60 + 195 * glow), int(70 - 40 * glow), int(100 - 60 * glow), 255)
        else:
            col = (74, 92, 140, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        d.ellipse([x - r - 7, y - r - 7, x + r + 7, y + r + 7],
                  outline=(col[0], col[1], col[2], 90), width=2)
    # the centre is a relay, drawn small: an authoritative hub would contradict
    # the word "decentralised" in the caption underneath it
    cr = 11 + 1.6 * np.sin(t * 2.1)
    d.ellipse([CENTRE[0] - cr, CENTRE[1] - cr, CENTRE[0] + cr, CENTRE[1] + cr],
              fill=(70, 84, 124, 255))

    # the deposit travelling with the guess
    gl2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg2 = ImageDraw.Draw(gl2)
    for rr in range(74, 0, -6):
        k = 1 - rr / 74
        dg2.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(255, 196, 118, int(46 * k)))
    img.alpha_composite(gl2.filter(ImageFilter.GaussianBlur(14)))
    d.ellipse([px - 13, py - 13, px + 13, py + 13], fill=(255, 208, 140, 255))
    d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=(255, 246, 224, 255))

    # the salary that gets docked, bottom left
    if loop > 0.5:
        f = (loop - 0.5) / 0.5
        bx, by, bw, bh = 150, H - 250, 420, 26
        d.rectangle([bx, by, bx + bw, by + bh], outline=(120, 138, 186, 200), width=2)
        d.rectangle([bx + 2, by + 2, bx + int(bw * (1 - f)) - 2, by + bh - 2],
                    fill=(196, 96, 88, 220))
        d.text((bx, by - 34), "SALARY", font=R.F("DejaVuSans-Bold.ttf", 20),
               fill=(150, 166, 210, 255))

    out = grade(np.array(img.convert("RGB")), warm=0.1)
    return cap(Image.fromarray(out), t, L2)


# ---------------------------------------------------------------- shot 3
L3 = [
    (0.3, 4.4, "The security of the Order, particularly preventing influence and bribery,\nrests on the privacy of its members."),
    (4.2, 8.4, "Order members are strictly forbidden to reveal their assigned task,\nand to reveal who holds it."),
    (8.0, 12.0, "A crowd that is indistinguishable, and therefore cannot be bought\none conversation at a time."),
]


def robed(scale, phase, alpha=255):
    """A hooded member of the Order. Faces are never drawn: the hood front is
    a flat void, because the point of the figure is that it cannot be told apart
    from the others.

    Drawn as ONE continuous silhouette. The first pass segmented the torso and
    the legs, which read as several small people stacked in a column.
    """
    S = scale
    Wc, Hc = int(210 * S), int(330 * S)
    im = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cloth = (58, 52, 84, alpha)
    edge = (78, 70, 108, alpha)
    cx = Wc / 2
    bob = np.sin(phase * 1.6) * 3 * S
    lw = max(4, int(17 * S))

    # legs: one pair, wide and planted, so the figure has ground contact
    d.line([cx - 11 * S, Hc * 0.70, cx - 20 * S, Hc * 0.965], fill=cloth, width=lw)
    d.line([cx + 11 * S, Hc * 0.70, cx + 20 * S, Hc * 0.965], fill=cloth, width=lw)
    d.ellipse([cx - 32 * S, Hc * 0.945, cx - 8 * S, Hc * 0.995], fill=(22, 19, 30, alpha))
    d.ellipse([cx + 8 * S, Hc * 0.945, cx + 32 * S, Hc * 0.995], fill=(22, 19, 30, alpha))

    # torso + robe as one tapering mass, no seam
    d.polygon([(cx - 26 * S, Hc * 0.34 + bob), (cx + 26 * S, Hc * 0.34 + bob),
               (cx + 47 * S, Hc * 0.80), (cx - 47 * S, Hc * 0.80)], fill=cloth)
    d.polygon([(cx - 26 * S, Hc * 0.34 + bob), (cx + 26 * S, Hc * 0.34 + bob),
               (cx + 40 * S, Hc * 0.60), (cx - 40 * S, Hc * 0.60)], fill=edge)

    # arms
    aw = max(3, int(13 * S))
    d.line([cx + 17 * S, Hc * 0.38 + bob, cx + 50 * S, Hc * 0.54], fill=cloth, width=aw)
    d.line([cx - 17 * S, Hc * 0.38 + bob, cx - 50 * S, Hc * 0.58], fill=cloth, width=aw)

    # hood: a peaked cowl, and a flat void where a face would be
    hr = 27 * S
    d.pieslice([cx - hr * 1.16, Hc * 0.33 - hr * 1.28 + bob,
                cx + hr * 1.16, Hc * 0.33 + hr * 0.58 + bob], 180, 360, fill=cloth)
    d.polygon([(cx, Hc * 0.33 - hr * 1.30 + bob), (cx + hr * 1.16, Hc * 0.33 + hr * 0.30 + bob),
               (cx - hr * 1.16, Hc * 0.33 + hr * 0.30 + bob)], fill=cloth)
    d.ellipse([cx - hr * 0.86, Hc * 0.33 - hr * 0.98 + bob,
               cx + hr * 0.86, Hc * 0.33 + hr * 0.66 + bob], fill=(26, 23, 34, alpha))
    return im


def shot3(n):
    t = n / FPS
    img = Image.fromarray(dawn_sky(t).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, H * 0.60, W, H], fill=(38, 36, 40, 255))

    # the crowd, in ranks, all identical — one is about to break.
    # Reviewer could not see the breakaway, so he gets his own silhouette
    # treatment and the others are dimmed by the haze he runs out of.
    brk = ease(np.clip((t - 7.2) / 3.4, 0, 1))
    idx = 0
    for row in range(3):
        for col in range(5):
            sc = 0.30 + row * 0.13
            x = W * (0.14 + col * 0.18) + np.sin(t * 0.5 + idx) * 2
            y = H * (0.66 + row * 0.11)
            if idx == 7:
                x = lerp(x, W * 0.86, brk)
                y = lerp(y, H * 0.30, brk)
                sc = lerp(sc, 0.34, brk)
                if brk > 0.02:
                    fig = R.runner(sc, t * 1.6, robe=True, running=brk > 0.2, warm=False)
                    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    dl = ImageDraw.Draw(lay)
                    # smear trailing behind him: four fading streaks
                    for k in range(1, 5):
                        al = int(70 * (1 - k / 5) * brk)
                        dx = 150 * k * brk
                        dl.ellipse([x - fig.width / 2 - dx, y - fig.height * 0.62,
                                    x - fig.width / 2 - dx + fig.width, y - fig.height * 0.62 + fig.height],
                                   fill=(96, 88, 128, al))
                    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(16)))
                    # rim light on him only
                    img.alpha_composite(fig, (int(x - fig.width / 2), int(y - fig.height)))
                    d3 = ImageDraw.Draw(img)
                    d3.ellipse([x - fig.width / 2 + fig.width * 0.62, y - fig.height * 0.66,
                                x - fig.width / 2 + fig.width * 0.96, y - fig.height * 0.30],
                               outline=(150, 132, 190, int(150 * brk)), width=max(1, int(3 * sc)))
                    idx += 1
                    continue
            fig = robed(sc, t * 0.9 + idx, alpha=int(255 - 70 * brk))
            img.alpha_composite(fig, (int(x - fig.width / 2), int(y - fig.height)))
            idx += 1

    out = grade(np.array(img.convert("RGB")), warm=0.05, lift=0.045)
    return cap(Image.fromarray(out), t, L3)


# ---------------------------------------------------------------- shot 4
L4 = [
    (0.5, 5.2, "The next morning the foot path is swept again."),
    (4.6, 10.6, "The houses stand behind the trees, medieval in style, without any\nof the junk, dust on the ground, or other imperfections."),
]


def shot4(n):
    t = n / FPS
    img = Image.fromarray(dawn_sky(t, morning=True).astype(np.uint8)).convert("RGBA")
    img.alpha_composite(R.street(W, H, t))
    # the exit sign, unlit now
    d = ImageDraw.Draw(img)
    vx, vy = W * 0.52, H * 0.44
    d.rounded_rectangle([vx - 58, vy - 46, vx + 58, vy - 6], radius=5,
                        fill=(22, 34, 30, 255), outline=(58, 82, 66, 255))
    d.text((vx, vy - 26), "EXIT", font=R.F("DejaVuSans-Bold.ttf", 30),
           fill=(64, 92, 76, 255), anchor="mm")
    d.rectangle([vx - 74, vy - 26, vx + 74, vy + 96], fill=(40, 44, 48, 255),
                outline=(78, 84, 88, 255))
    d.rectangle([vx - 58, vy - 8, vx + 58, vy + 96], fill=(22, 24, 28, 255))

    # long low light across the paving
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(gl)
    for i in range(18):
        f = i / 18
        y = H * (0.58 + f * 0.05)
        dg.ellipse([-300 + f * 500, y - 16, W + 300 - f * 500, y + 16],
                   fill=(255, 196, 140, int(30 * (1 - f))))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(30)))

    out = grade(np.array(img.convert("RGB")), warm=0.9, lift=0.075, contrast=1.06)
    return cap(Image.fromarray(out), t, L4)


# ---------------------------------------------------------------- audio
def build_audio(path="/mnt/hermes_data/snowmoon/sound_full.wav", sr=44100, seed=23):
    rng = np.random.default_rng(seed)
    n = int(sr * DUR)
    t = np.arange(n) / sr
    sig = 0.014 * rng.standard_normal(n)
    sig *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t)

    def add(lo, dur, fn):
        i0 = int(lo * sr)
        L = int(dur * sr)
        if i0 + L > n:
            L = n - i0
            if L <= 0:
                return
        f = np.linspace(0, 1, L)
        sig[i0:i0 + L] += fn(f)

    # shot 1: accelerating footsteps
    tt = 0.0
    while tt < 10.0:
        add(tt, 0.10, lambda f: (np.sin(2 * np.pi * (150 - 70 * f) * f * 0.1) * np.exp(-f * 11)) * 0.30
            + rng.standard_normal(len(f)) * np.exp(-f * 26) * 0.30)
        tt += float(np.interp(tt, [0, 5.4], [0.62, 0.235]))
    add(8.6, 0.5, lambda f: np.sin(2 * np.pi * 70 * f * 0.5) * np.exp(-f * 5) * 0.22)

    # shot 2: a low cryptographic hum, two tones that beat against each other
    for i in range(n):
        pass
    m = (t >= 10.0) & (t < 24.0)
    env = np.clip(np.minimum((t - 10) / 1.2, (24 - t) / 1.6), 0, 1)
    sig[m] += env[m] * (np.sin(2 * np.pi * 98 * t[m]) * 0.028
                        + np.sin(2 * np.pi * 99.4 * t[m]) * 0.028
                        + np.sin(2 * np.pi * 196 * t[m]) * 0.012)
    # each loop of the guess, a soft tick
    for k in range(3):
        add(10.0 + k * 6.0 + 0.05, 0.18,
            lambda f: (np.sin(2 * np.pi * 1400 * f * 0.18) * np.exp(-f * 22)) * 0.10)

    # shot 3: many voices, none intelligible
    m3 = (t >= 24.0) & (t < 36.0)
    env3 = np.clip(np.minimum((t - 24) / 1.5, (36 - t) / 2.0), 0, 1)
    murmur = np.zeros(int(m3.sum()))
    for k in range(5):
        f0 = 110 + k * 23
        murmur += np.sin(2 * np.pi * f0 * t[m3] + rng.random() * 6) * (0.012 / (k + 1))
    sig[m3] += env3[m3] * murmur
    add(31.2, 0.6, lambda f: rng.standard_normal(len(f)) * np.exp(-f * 14) * 0.16)

    # shot 4: birdsong over wind
    m4 = t >= 36.0
    env4 = np.clip((t - 36.0) / 2.5, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
    birds = np.zeros(int(m4.sum()))
    for k in range(9):
        s0 = 36.6 + k * 1.1 + rng.random() * 0.5
        i0 = int((s0 - 36.0) * sr)
        L = int(0.09 * sr)
        if i0 + L < len(birds):
            f = np.linspace(0, 1, L)
            trill = np.sin(2 * np.pi * (2100 + 500 * np.sin(2 * np.pi * 26 * f)) * f * 0.09)
            birds[i0:i0 + L] += trill * np.exp(-f * 8) * 0.05
    sig[m4] += env4[m4] * birds
    sig[m4] += env4[m4] * np.sin(2 * np.pi * 0.09 * t[m4]) * 0.02

    sig = np.tanh(sig * 1.6) * 0.60
    st = np.stack([sig, sig], axis=1)
    pcm = (st * 32767).astype("<i2")
    with open(path, "wb") as fh:
        import wave
        w = wave.open(fh, "wb")
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes()); w.close()
    return path


def main():
    os.makedirs(FULL, exist_ok=True)
    for old in os.listdir(FULL):
        os.remove(os.path.join(FULL, old))
    n_tot = int(DUR * FPS)
    for n in range(n_tot):
        t = n / FPS
        if t < 10.0:
            img = R.frame(n)
        elif t < 24.0:
            img = shot2(n - 10 * FPS)
        elif t < 36.0:
            img = shot3(n - 24 * FPS)
        else:
            img = shot4(n - 36 * FPS)
        img.save(f"{FULL}/f{n:05d}.jpg", quality=92)
        if n % 120 == 0:
            print(f"  {n}/{n_tot}", flush=True)
    print("frames:", len(os.listdir(FULL)))
    print("audio:", build_audio())


if __name__ == "__main__":
    main()