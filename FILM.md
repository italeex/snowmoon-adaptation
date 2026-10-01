---
title: "Snowmoon — Chapter 1, 47 seconds"
---

<div align="center">

# Snowmoon — Chapter 1

**An audiovisual adaptation of Chapter 1 of *Snowmoon* by Vitalik Buterin (GPL v3).**

47 seconds · 1920×1080 · 24 fps · four shots · sound

</div>

<div align="center">

<video controls width="900" poster="https://files.catbox.moe/rxple8.mp4">
  <source src="https://raw.githubusercontent.com/italeex/snowmoon-adaptation/main/snowmoon_full.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

**[Direct download / direct link to the finished film](https://raw.githubusercontent.com/italeex/snowmoon-adaptation/main/snowmoon_full.mp4)**

</div>

---

## What this is

Four scenes from the first chapter of a 32-chapter novel: a clean medieval street
between stone-brick houses, a robed man who breaks formation and runs for the fire
exit, the Order's guessing game rendered as a peer network, a crowd deliberately
made indistinguishable, and the same street at dawn, empty and swept.

## How it was made

No AI image generation anywhere. Every pixel is drawn procedurally from a seeded
generator at final 1920×1080, with no GPU and no downloaded assets, so the output is
exactly reproducible and the whole pipeline is auditable.

```
python3 render_full.py    # 1128 frames, ~5 minutes single-core
ffmpeg -framerate 24 -i frames_full/f%05d.jpg -i sound_full.wav \
       -c:v libx264 -pix_fmt yuv420p -crf 19 -preset slow \
       -c:a aac -b:a 160k -shortest snowmoon_full.mp4
```

## Reviews found real defects, and the fixes are listed rather than hidden

Three rounds; seven substantive defects fixed. The two that mattered most were
contradictions between a caption and its own image — the network diagram was
rebuilt because a hub-and-spoke drawing sat under a subtitle saying *decentralised*,
and the robed figures were redrawn because reviewers read them as several small
people stacked in a column. [Full list in the README](README.md).

## Licence

Snowmoon and the quoted text are © Vitalik Buterin, GPL v3. This pipeline is
released under GPL v3 to match. Third-party code (PIL, numpy, ffmpeg, DejaVu) is
not redistributed here and keeps its own licence.
