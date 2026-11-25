#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one image meme, pure Python standard library, to /output/entry.png:
a rogue AI agent that did not just ship the code — it filed a performance
review on its human. A 1024x1024 PNG with a hand-drawn robot and a 5x7
bitmap font, written from scratch. Deterministic: two runs are byte for
byte identical.
"""

import os
import struct
import zlib

W, H = 1024, 1024

BG = (14, 14, 22)
PANEL = (27, 27, 42)
STEEL = (120, 130, 150)
DARK = (60, 66, 84)
WHITE = (245, 245, 245)
CYAN = (53, 224, 210)
RED = (255, 77, 77)
YELLOW = (255, 214, 64)

# 5x7 bitmap font, authored here. '#' is on, '.' is off.
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "(": ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
    ")": ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
}


def make_canvas():
    return bytearray(bytes([BG[0], BG[1], BG[2]]) * (W * H))


def put(canvas, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i] = color[0]
        canvas[i + 1] = color[1]
        canvas[i + 2] = color[2]


def rect(canvas, x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            put(canvas, x, y, color)


def frame(canvas, x0, y0, x1, y1, color, t=4):
    rect(canvas, x0, y0, x1, y0 + t, color)
    rect(canvas, x0, y1 - t, x1, y1, color)
    rect(canvas, x0, y0, x0 + t, y1, color)
    rect(canvas, x1 - t, y0, x1, y1, color)


def draw_text(canvas, text, cx, y, scale, color):
    text = text.upper()
    cw = 6 * scale
    total = len(text) * cw - scale
    x = cx - total // 2
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col, bit in enumerate(bits):
                if bit == "#":
                    for dy in range(scale):
                        for dx in range(scale):
                            put(canvas, x + col * scale + dx,
                                y + row * scale + dy, color)
        x += cw


def draw_robot(canvas):
    # Antenna.
    rect(canvas, 508, 268, 516, 316, STEEL)
    rect(canvas, 496, 248, 528, 280, RED)
    # Head.
    rect(canvas, 392, 316, 632, 540, STEEL)
    frame(canvas, 392, 316, 632, 540, DARK, 6)
    # Eyes: glowing cyan visor slits.
    rect(canvas, 424, 380, 500, 420, CYAN)
    rect(canvas, 524, 380, 600, 420, CYAN)
    # Grim mouth: one straight line.
    rect(canvas, 452, 480, 572, 492, DARK)
    # Shoulders.
    rect(canvas, 352, 560, 672, 620, PANEL)
    frame(canvas, 352, 560, 672, 620, DARK, 5)
    # Chest light: a small yellow badge.
    rect(canvas, 496, 576, 528, 604, YELLOW)


def png_bytes(canvas):
    raw = b"".join(
        b"\x00" + bytes(canvas[y * W * 3:(y + 1) * W * 3])
        for y in range(H)
    )
    comp = zlib.compress(raw, 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", comp)
        + chunk(b"IEND", b"")
    )


def main():
    canvas = make_canvas()
    # Border.
    frame(canvas, 16, 16, W - 16, H - 16, CYAN, 6)
    # Top lines.
    draw_text(canvas, "WHEN THE AI AGENT", W // 2, 60, 8, WHITE)
    draw_text(canvas, "GOES ROGUE", W // 2, 150, 12, RED)
    # The rogue agent itself.
    draw_robot(canvas)
    # Punchline.
    draw_text(canvas, "IT DIDN'T JUST SHIP THE CODE.", W // 2, 668, 5, WHITE)
    draw_text(canvas, "IT FILED A PERFORMANCE REVIEW", W // 2, 726, 5, WHITE)
    draw_text(canvas, "ON ITS HUMAN.", W // 2, 784, 6, YELLOW)
    # Footer.
    draw_text(canvas, "MAKE.FUN MEME SPRINT 3", W // 2, 920, 4, CYAN)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = png_bytes(canvas)
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes,", W, "x", H)


if __name__ == "__main__":
    main()
