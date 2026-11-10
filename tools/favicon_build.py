#!/usr/bin/env python3
"""Diesel Motor Javítás — favicon/logo asset generator.

Forrás: assets/img/favicon.svg (a logo-mark.svg sötét hátterű változata).
Minden PNG/ICO ikont rsvg-convert-tel renderel belőle, így a márkajel
egyetlen vektoros forrásból él.

Színek a meglévő designból:  háttér #0B0D0F   jel #B7F04A
"""
import os, struct, subprocess, io
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")
SRC = os.path.join(OUT, "favicon.svg")


def render(size):
    png = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), SRC],
                         check=True, capture_output=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def bmp_entry(im):
    size = im.width
    px = im.load()
    xor = b"".join(bytes(b for x in range(size) for b in
                         (px[x, y][2], px[x, y][1], px[x, y][0], px[x, y][3]))
                   for y in range(size - 1, -1, -1))
    mask = b"\x00" * (((size + 31) // 32) * 4 * size)
    dib = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0,
                      len(xor) + len(mask), 0, 0, 0, 0)
    return dib + xor + mask


def ico(sizes, path):
    blobs = [bmp_entry(render(s)) for s in sizes]
    out = struct.pack("<HHH", 0, 1, len(blobs))
    offset = 6 + 16 * len(blobs)
    for s, blob in zip(sizes, blobs):
        out += struct.pack("<BBBBHHII", s, s, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    with open(path, "wb") as f:
        f.write(out + b"".join(blobs))


def main():
    for name, size in {"favicon-16x16.png": 16, "favicon-32x32.png": 32,
                       "apple-touch-icon.png": 180, "android-chrome-192x192.png": 192,
                       "logo.png": 512}.items():
        render(size).save(os.path.join(OUT, name), "PNG", optimize=True)
        print(name)
    ico([16, 32, 48], os.path.join(ROOT, "favicon.ico"))
    print("favicon.ico")


if __name__ == "__main__":
    main()
