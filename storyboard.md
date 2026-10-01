# Storyboard — Snowmoon Chapter 1, four shots

The first cut was one continuous ten-second shot with no camera movement. It is
preserved in `render_v1.py.bak` and still online, but a single static shot cannot
show storytelling, atmosphere or technical execution, and the bounty judges all
three. So the film is now 47 seconds in four shots.

## Source

Chapter 1, *Snowmoon* (GPL v3, Vitalik Buterin), four passages:

1. The opening: Gladias on a foot path, tall trees, stone-brick houses, "without
   any of the junk, dust on the ground, or other imperfections."
2. Later: "another man nearby, also wearing a privacy robe, broke and ran toward
   the fire exit on the right."
3. The Order's guessing game: "anyone can connect to the decentralised
   cryptographic network that manages the Order's operations, and send in a guess
   about what a particular Order member's assigned task is, along with a small
   deposit... if their guess is correct, the Order member's salary is docked, and
   the discoverer gets half as a reward."
4. The privacy rationale: "a crowd that is indistinguishable, and therefore cannot
   be bought one conversation at a time."

## The four shots

| # | Time | Content | Palette |
|---|---|---|---|
| 1 | 0–10 s | The foot path, the houses, the robed man breaking and running for the exit. Fixed camera, as v1. | Night, slate and ember |
| 2 | 10–24 s | The guessing game. A mesh of 26 peers; a guess travels the ring with a deposit; a salary bar drains on a correct guess. | Deep indigo, one amber |
| 3 | 24–36 s | Three ranks of identical faceless hoods. One leaves formation and runs, trailing motion smear. | Cold violet, near-black |
| 4 | 36–47 s | The same street at dawn, empty, swept. The exit sign unlit. | Warm grey-violet |

Shot 1 is `R.frame()` from `render.py`, unchanged. Shots 2–4 are in `render_full.py`.

## The review loop, and what it caught

Every render was looked at before the next one. Three rounds; seven defects fixed.
The two that mattered most were contradictions between a caption and its own
image:

- Shot 2 originally routed the guess node → hub → node and drew the hub larger
  and brighter than any peer. Under a subtitle saying *decentralised*, that is a
  hub-and-spoke diagram. The route now stays on the ring and misses the centre
  entirely; the relay is small and dim.
- Shot 3's figures were two overlapping torso polygons with legs forking from one
  point, and read as several small people stacked in a column. One continuous
  silhouette with planted legs fixed it.
- The figure who breaks formation was invisible on first review. Reviewers could
  not pick him out of the crowd, which is the one thing that shot must not fail at.

Rounds 1–2 also fixed: houses missing entirely (one continuous wall), the runner
unreadable at 12 px, doors indistinguishable from windows, and colour fringing on
every high-contrast edge from compositing a downscaled layer.

## Palette and why

- Sky: indigo 14,20,46 → slate 104,116,140 at the horizon. Cool throughout.
- Stone: desaturated, `(58..84, 56..80, 60..82)` with depth.
- Windows: `(255, 196, 118)` — the only warm colour in the frame.
- Exit: `(24, 190, 108)` with a 26 px Gaussian bloom. **The only saturated green
  in the film.**

The exit is not styled to match the world. That is the interpretation: the fire
exit is the one element of this medieval street that belongs to neither the stone
nor the sky, and the man runs toward it anyway.

## Cleanliness as a choice

The book goes out of its way to say the structures are medieval *without* the junk
and dust a real thousand-year-old building would have. So: swept paving, precise
stone courses, no litter anywhere, no wear on the walls. It is drawn clean on
purpose, and the only thing in ten seconds that disturbs it is a man running.

## Colour grade

```
contrast  (a - 0.5) * 1.10 + 0.5
lift      a * 0.94 + 0.055          # shadows stay readable
highlights a[...,0] += lum^2 * 0.10 # warm the lit windows
shadows   a[...,2] += (1 - lum) * 0.05
vignette  strength 0.34 -> 0.50 as he leaves
```

The shadow lift matters: the first pass crushed the trees and the near houses
into unreadable black, and the review called it out. Without the lift the film
loses the architecture the caption is describing.

## What the review changed

Three rounds, seven defects. They are listed rather than deleted because the loop
is the actual method: render, look, fix, look again. `render_v1.py.bak` is kept so
the first two rounds can be inspected.

```
round 1  houses missing (one continuous wall)         → house() written
         runner unreadable at 12 px                   → 2.05× foreground scale
         doors indistinguishable from windows          → frame, lit edge, handle
         red/cyan fringing on every edge              → draw at final size
round 2  hub-and-spoke under "decentralised"          → ring route, small relay
         figures read as stacked people              → one continuous silhouette
         the breakaway figure invisible               → own treatment + smear
```

## Cost

```
v1   240 frames, 86 s single-core          → 1.9 MB
v2  1128 frames, ~5 min single-core, no GPU → 6.8 MB
```