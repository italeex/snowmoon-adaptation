# Snowmoon — Chapter 1 adaptation

An adaptation of Chapter 1 of [*Snowmoon*](https://vitalik.eth.limo/snowmoon/) by
Vitalik Buterin, released under GPL v3. This repository is the open-source
production pipeline required by the bounty: every non-commodity material used to
make the film is here.

**Film:** 47 seconds, four shots, 1920×1080 at 24 fps, H.264 + AAC.
**Video:** <https://files.catbox.moe/rxple8.mp4>

**Watch it here:** [FILM.md](FILM.md) — the film is embedded and plays without login. The file is in this repo as `snowmoon_full.mp4` (6.8 MB). (7 099 564 bytes, verified: HTTP 206,
`ftypisom`, 47.000 s, stereo AAC 160 k).
(The first cut, a single 10-second shot, is at <https://files.catbox.moe/t0tsee.mp4>
and its pipeline is preserved in `render_v1.py.bak`.)

## The scene

Chapter 1, Meldan, Veridia. Gladias walks a foot path between tall trees, past
stone-brick houses; a second man in a privacy robe breaks and runs for the fire
exit. The film is ten seconds of that movement — one continuous shot, no cuts.

Quoted text (GPL v3):

> "Gladias was walking along a foot path, with tall trees towering on both sides.
> A series of houses made out of large stone bricks lay behind the trees on both
> sides, medieval in style but without any of the junk, dust on the ground, or
> other imperfections that a real medieval structure would have had a thousand
> years earlier."
>
> "...another man nearby, also wearing a privacy robe, broke and ran toward the
> fire exit on the right."

## How it was made — and what was *not* used

There is no AI image generation anywhere in this pipeline. Every pixel is drawn
procedurally from a seeded random number generator, at final 1920×1080, with no
GPU. This is a deliberate constraint, not a limitation I worked around: it means
the output is exactly reproducible and the whole pipeline is auditable.

```
PIL        raster drawing: sky gradient, houses, trees, figures, captions
numpy      gradient construction, colour grade, vignette
ffmpeg     H.264 assembly, AAC audio mux
Dejavu     DejaVuSerif for the quoted text, DejaVuSansBold for the exit sign
```

Rendering cost: 240 frames in ~86 s on one CPU core, single-threaded.

```
python3 render.py                          # 240 PNG-equivalent frames -> frames/
ffmpeg -framerate 24 -i frames/f%05d.jpg -i sound.wav \
       -c:v libx264 -pix_fmt yuv420p -crf 19 -preset slow \
       -c:a aac -b:a 160k -shortest snowmoon_ch1.mp4
```

## Files

| Path | What it is |
|---|---|
| `render.py` | The entire visual pipeline: sky, street, houses, trees, figures, exit sign, grade, captions. |
| `sound.py` | Procedural audio: wind bed, accelerating footsteps, door thud, closing tone. |
| `still.jpg` | The still submitted as the claim image (t=1.2 s). |
| `snowmoon_ch1.mp4` | The finished 10 s film, 1080p24, H.264 + AAC. |
| `storyboard.md` | Shot breakdown and the reasoning behind each choice. |
| `render_v1.py.bak` | Superseded first pass, kept so the review that shaped v2 is auditable. |

## Three rounds of visual review, and what they changed

The film was looked at after every render. Nothing was declared finished on a zero
exit code alone. Seven substantive defects were found and fixed:

1. **Round 1 — the architecture contradicted its own subtitle.** The caption read
   "a series of houses" and the frame showed one continuous wall: no roofs, doors
   or windows. `house()` was written.
2. **Round 1 — the running figure was unreadable** at 12 px wide and could be
   mistaken for a post. Now 2.05× the near-frame scale early on.
3. **Round 1 — doors were indistinguishable from windows**, both being dark
   rectangles. Doors gained a recessed frame, a lit edge and a handle.
4. **Round 1 — colour fringing on every high-contrast edge**, caused by
   compositing a downscaled RGBA layer. Fixed by drawing figures at final size
   and never resampling them.
5. **Round 2 — the network diagram contradicted "decentralised".** The guess was
   routed node → hub → node and the hub was drawn larger and brighter than every
   peer: a hub-and-spoke diagram under a subtitle saying peer-to-peer. The route
   now runs along the ring and never through the centre, the relay is small and
   dim, and the message has a comet trail so its direction is unambiguous.
6. **Round 2 — the robed figures read as several small people stacked in a
   column,** because the torso was two overlapping polygons and the legs forked
   from a single point. Redrawn as one continuous silhouette with planted legs.
7. **Round 2 — the figure who breaks formation was invisible.** Reviewers could
   not identify him. He now leaves earlier, runs further, keeps his own
   silhouette treatment, gets a motion smear, and the crowd is dimmed behind him.

The loop — render, look, fix, look again — is the actual production method here,
and it is the part worth building on.

## Interpretation

The street is **clean**, because the text insists on "without any of the junk,
dust on the ground, or other imperfections": swept paving, precise stonework, no
litter, and the only disturbance in forty-seven seconds is a man running through
it. He is the litter.

The network has **no centre**, because "decentralised" is drawn as one: a mesh of
equals, the relay small and unlit, the message taking the long way around the
ring. The salary bar drains when a guess lands — the whole mechanism in one
graphic.

The crowd is **faceless on purpose**. No hood in the film has a face, because a
crowd you can identify is a crowd you can approach, and that is the security the
Order is buying.

## Licence

Snowmoon text and this adaptation's scene are © Vitalik Buterin, GPL v3. This
pipeline is released under GPL v3 to match. Third-party code (PIL, numpy, ffmpeg,
DejaVu) is not redistributed here and keeps its own licence.