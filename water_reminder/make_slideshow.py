"""Builds avatars/slideshow.gif from every picture in the photos folder (crossfading)."""
import glob
import os

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "photos")
OUT = os.path.join(HERE, "avatars", "slideshow.gif")
SIZE = (270, 360)
HOLD, FADE_STEPS, FADE_MS = 2000, 8, 60

paths = sorted(p for p in glob.glob(os.path.join(SRC, "*"))
               if p.lower().endswith((".jpg", ".jpeg", ".jfif", ".png", ".webp")))
# crop to the same portrait shape, keeping faces (top of picture) in view
pics = [ImageOps.fit(Image.open(p).convert("RGB"), SIZE, Image.LANCZOS, centering=(0.5, 0.3))
        for p in paths]

frames, durations = [], []
for i, pic in enumerate(pics):
    frames.append(pic)
    durations.append(HOLD)
    nxt = pics[(i + 1) % len(pics)]
    for k in range(1, FADE_STEPS):
        frames.append(Image.blend(pic, nxt, k / FADE_STEPS))
        durations.append(FADE_MS)

frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
print(f"saved {OUT} from {len(pics)} pictures, {len(frames)} frames")
