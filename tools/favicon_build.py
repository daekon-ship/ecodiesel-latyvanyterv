#!/usr/bin/env python3
"""Diesel Motor Javítás — favicon/logo asset generator.

A márkajel (brand-mark SVG) egyszerűsített, kis méretben is olvasható
verziójából állít elő minden webes ikont.

Színek a meglévő designból:
  background #0B0D0F   mark      #B7F04A
"""
import os, struct
from PIL import Image, ImageDraw

BG = (0x0B, 0x0D, 0x0F)
FG = (0xB7, 0xF0, 0x4A)
UNIT = 32.0                      # a márka SVG viewBox-a

# --- A márka sziluettje 32x32 koordinátában (a brand-mark útvonalakból) -----
CHIMNEY = [(10, 4), (18, 4), (18, 11), (10, 11)]
BODY = [
    (2, 11), (19, 11), (23, 14), (28, 14), (28, 24),
    (23, 24), (21, 26), (7, 26), (5, 24), (2, 24),
]
TAB = [(28, 15), (30, 15), (30, 21), (28, 21)]
BORE = (18.5, 19.5, 3.6)         # henger-lyuk = a márka "pontja", kontrasztos kivágás

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")      # PNG/SVG ikonok
ICO = ROOT                                       # favicon.ico a gyökérben


def master(size=1024):
    """Nagy felbontású, sima élű mesterkép."""
    s = size / UNIT
    img = Image.new("RGBA", (size, size), BG + (255,))
    d = ImageDraw.Draw(img)
    for shape in (CHIMNEY, BODY, TAB):
        d.polygon([(x * s, y * s) for x, y in shape], fill=FG + (255,))
    cx, cy, r = BORE[0] * s, BORE[1] * s, BORE[2] * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BG + (255,))
    return img


def png(img, size, path):
    im = img.resize((size, size), Image.LANCZOS)
    im.save(path, "PNG", optimize=True)
    return os.path.getsize(path)


def bmp_entry(img, size):
    """32 bites DIB (BITMAPINFOHEADER + BGRA, alulról felfelé) az ICO-hoz."""
    im = img.resize((size, size), Image.LANCZOS).convert("RGBA")
    px = im.load()
    rows = []
    for y in range(size - 1, -1, -1):
        row = bytearray()
        for x in range(size):
            r, g, b, a = px[x, y]
            row += bytes((b, g, r, a))
        rows.append(bytes(row))
    xor = b"".join(rows)
    stride = ((size + 31) // 32) * 4          # 1 bites AND-maszk, 32 bitre igazítva
    mask = b"\x00" * (stride * size)
    dib = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0,
                      len(xor) + len(mask), 0, 0, 0, 0)
    return dib + xor + mask


def ico(entries, path):
    blobs = [bmp_entry(im, sz) for sz, im in entries]
    out = struct.pack("<HHH", 0, 1, len(blobs))
    offset = 6 + 16 * len(blobs)
    for (sz, _), blob in zip(entries, blobs):
        out += struct.pack("<BBBBHHII",
                           sz if sz < 256 else 0, sz if sz < 256 else 0,
                           0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    with open(path, "wb") as f:
        f.write(out + b"".join(blobs))
    return os.path.getsize(path)


def svg():
    def poly(pts):
        return " ".join(f"{x},{y}" for x, y in pts)
    cx, cy, r = BORE
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <title>Diesel Motor Javítás</title>
  <rect width="32" height="32" fill="#0B0D0F"/>
  <g fill="#B7F04A">
    <polygon points="{poly(CHIMNEY)}"/>
    <polygon points="{poly(BODY)}"/>
    <polygon points="{poly(TAB)}"/>
  </g>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#0B0D0F"/>
</svg>
"""


def main():
    img = master(1024)
    sizes = {
        "favicon-16x16.png": 16,
        "favicon-32x32.png": 32,
        "apple-touch-icon.png": 180,
        "android-chrome-192x192.png": 192,
        "logo.png": 512,
    }
    for name, size in sizes.items():
        print(f"{name:32s} {png(img, size, os.path.join(OUT, name)):>7d} B")

    ico_path = os.path.join(ICO, "favicon.ico")
    print(f"{'favicon.ico (16+32+48)':32s} "
          f"{ico([(16, img), (32, img), (48, img)], ico_path):>7d} B")

    with open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg())
    print(f"{'favicon.svg':32s} "
          f"{os.path.getsize(os.path.join(OUT, 'favicon.svg')):>7d} B")


if __name__ == "__main__":
    main()
