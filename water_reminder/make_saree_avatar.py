"""Draws avatars/saree_lady.gif: a cartoon South Indian lady in a sari offering water."""
import os
from PIL import Image, ImageDraw

S = 4  # draw at 4x then shrink for smooth edges
W, H = 240, 260
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatars", "saree_lady.gif")

SKIN, HAIR = "#c68642", "#1b1210"
SAREE, BORDER, BLOUSE = "#d81b60", "#ffc107", "#6a1b9a"


def r(box):
    return [v * S for v in box]


def frame(blink, lift):
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = 105
    # hair back + braid
    d.ellipse(r([cx - 52, 18, cx + 52, 128]), fill=HAIR)
    # body: blouse and saree
    d.rounded_rectangle(r([cx - 55, 150, cx + 55, 260]), 30 * S, fill=BLOUSE)
    d.polygon([v * S for v in (cx - 55, 175, cx + 25, 150, cx + 55, 190, cx - 10, 260, cx - 55, 260)], fill=SAREE)
    d.line([v * S for v in (cx + 25, 150, cx - 30, 260)], fill=BORDER, width=7 * S)
    # neck + face
    d.rectangle(r([cx - 13, 120, cx + 13, 158]), fill=SKIN)
    d.ellipse(r([cx - 40, 40, cx + 40, 135]), fill=SKIN)
    # hair front with middle parting
    d.chord(r([cx - 44, 30, cx + 44, 100]), 180, 360, fill=HAIR)
    d.polygon([v * S for v in (cx - 44, 65, cx - 40, 100, cx - 30, 62)], fill=HAIR)
    d.polygon([v * S for v in (cx + 44, 65, cx + 40, 100, cx + 30, 62)], fill=HAIR)
    # jasmine flowers
    for fx, fy in ((cx + 40, 50), (cx + 47, 62), (cx + 50, 76), (cx + 49, 90)):
        d.ellipse(r([fx - 6, fy - 6, fx + 6, fy + 6]), fill="white", outline="#e0e0e0")
    # bindi, eyes, smile, blush, earrings
    d.ellipse(r([cx - 4, 66, cx + 4, 74]), fill="#c62828")
    for ex in (cx - 17, cx + 17):
        if blink:
            d.arc(r([ex - 9, 82, ex + 9, 94]), 200, 340, fill=HAIR, width=3 * S)
        else:
            d.ellipse(r([ex - 8, 80, ex + 8, 96]), fill="white")
            d.ellipse(r([ex - 5, 82, ex + 5, 95]), fill="#2b1a12")
            d.ellipse(r([ex - 1, 84, ex + 2, 87]), fill="white")
            d.arc(r([ex - 10, 76, ex + 10, 92]), 200, 340, fill=HAIR, width=2 * S)
        d.ellipse(r([ex - 9, 101, ex + 5, 109]), fill="#e57373")
    d.chord(r([cx - 14, 104, cx + 14, 124]), 0, 180, fill="#b71c1c")
    for ex in (cx - 41, cx + 41):
        d.ellipse(r([ex - 5, 108, ex + 5, 120]), fill=BORDER)
    # arm offering a glass of water
    gy = 165 - lift
    d.line([v * S for v in (cx + 45, 175, cx + 85, gy + 25)], fill=SKIN, width=14 * S)
    d.polygon([v * S for v in (cx + 75, gy - 25, cx + 120, gy - 25, cx + 114, gy + 30, cx + 81, gy + 30)],
              fill="#e1f5fe", outline="#0277bd")
    d.polygon([v * S for v in (cx + 78, gy - 5, cx + 117, gy - 5, cx + 114, gy + 30, cx + 81, gy + 30)],
              fill="#4fc3f7")
    d.ellipse(r([cx + 78, gy + 18, cx + 94, gy + 34]), fill=SKIN)  # fingers
    return im.resize((W, H), Image.LANCZOS)


frames = [frame(blink=(i == 9), lift=[0, 2, 4, 6, 8, 6, 4, 2, 0, 0, 0, 0][i]) for i in range(12)]
# GIF transparency: composite on popup background colour
bg = (1, 59, 92, 255)
out = [Image.alpha_composite(Image.new("RGBA", f.size, bg), f).convert("RGB") for f in frames]
out[0].save(OUT, save_all=True, append_images=out[1:], duration=110, loop=0)
out[0].save(OUT.replace(".gif", "_preview.png"))
print("saved", OUT)
