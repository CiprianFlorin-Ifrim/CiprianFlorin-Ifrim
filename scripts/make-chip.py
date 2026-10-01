#!/usr/bin/env python3
"""Draw the chip of the profile README as a schematic symbol in the style of KiCad.

    python3 scripts/make-chip.py assets

The script writes chip-dark.svg and chip-light.svg into the directory it is given. Pins 1 to 11 run
down the left side and pins 12 to 22 run up the right side, the way a datasheet numbers a package. A
pin with a text carries a net label on a wire. A pin with None carries the blue cross of a pin that
is not connected, and a pin with a tuple ends in a power symbol, drawn as KiCad draws it.
"""
import sys
from pathlib import Path

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
WIDTH = 960
SCALE = 0.95

PINS = [
    (1, "ROLE", "Lead AI Architect, IBM"),
    (2, "FNDR1", "Brainquiver"),
    (3, "GH1", "github.com/brainquiver"),
    (4, "FNDR2", "Britready"),
    (5, "GH2", None),
    (6, "MSC1", "Advanced Computing, KCL"),
    (7, "MSC2", "Software Engineering, QSBT"),
    (8, "MSC3", "AI and Data Science, NEU"),
    (9, "BENG", "Robotics, MDX"),
    (10, "EN", ("power", "+3.3V")),
    (11, "GND", "London, UK"),
    (12, "NC", None),
    (13, "PROG", "Python, C, C++, Rust, R, JS"),
    (14, "ACCL", "SG2002 TPU, STM32N6 NPU"),
    (15, "MCU", "STM32, ESP32, nRF52, RP2"),
    (16, "CAD", "SolidWorks, Onshape, NX"),
    (17, "FIX", "@ciprian_ifrim"),
    (18, "3D", "@CiprianIfrim_1527438"),
    (19, "YT", "@ciprian-florinifrim1928"),
    (20, "HF", "hf.co/CiprianFlorinIfrim"),
    (21, "LNKD", "in/ciprian-ifrim"),
    (22, "VDD", "passion +3.3V"),
]

# The colours of the KiCad default theme, in its dark and its light version.
THEMES = {
    "dark": dict(sheet="#001023", grid="#132c47", body="#1d2e3f", outline="#c2c2c2", pin="#d24b4b",
                 pname="#53c6c6", pnum="#c8a0a0", wire="#00c000", label="#e8e8e8", faint="#6f8aa6",
                 nc="#4d7fc4"),
    "light": dict(sheet="#f5f4ef", grid="#d6d4cc", body="#ffffc2", outline="#840000", pin="#840000",
                  pname="#006464", pnum="#a90000", wire="#009600", label="#000000", faint="#8a8678",
                  nc="#0000c8"),
}


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def row(num, count):
    """The row of a pin, counted from the top of its side."""
    return num - 1 if num <= count // 2 else count - num


def power_symbol(c, text, x0, y, left):
    """A KiCad power symbol turned to lie along the wire.

    The library is in millimetres and the sheet grid of 12.7 pixels is 1.27 mm, so 10 pixels are
    1 mm. The +3.3V symbol is a stem of 2.54 mm that ends in an open arrow. It is drawn at 70 percent,
    so its arrow is about as wide as the no connect cross.
    """
    sg = -1 if left else 1
    sx = x0 + sg * 10
    k = 0.7
    tip = sx + sg * 25.4 * k
    head = sx + sg * 12.7 * k
    out = [f'<line x1="{x0}" y1="{y}" x2="{sx}" y2="{y}" stroke="{c["wire"]}" stroke-width="1.5"/>']
    out.append(f'<circle cx="{x0}" cy="{y}" r="1.8" fill="{c["pin"]}"/>')
    out.append(f'<path d="M{sx} {y} H{tip:.1f} M{head:.1f} {y - 7.62 * k:.1f} L{tip:.1f} {y} '
               f'L{head:.1f} {y + 7.62 * k:.1f}" fill="none" stroke="{c["outline"]}" stroke-width="1.5" '
               'stroke-linejoin="round"/>')
    anchor = "end" if left else "start"
    out.append(f'<text x="{tip + sg * 8:.1f}" y="{y + 0.5}" dominant-baseline="central" '
               f'text-anchor="{anchor}" fill="{c["pname"]}">{esc(text)}</text>')
    return out


def net_label(c, value, wx, y, left):
    """A net label on a half pixel grid, so each edge of its box lands on one pixel row."""
    half = 12
    width = round(max(len(value), 4) * 7.2 + 24)
    ym = y + 0.5
    if left:
        tip = wx - 0.5
        box = f"M{tip} {ym} l-{half} -{half} h-{width - half} v{2 * half} h{width - half} z"
        text = (f'<text x="{wx - half - 6}" y="{ym}" dominant-baseline="central" text-anchor="end" '
                f'fill="{c["label"]}">{esc(value)}</text>')
    else:
        tip = wx + 0.5
        box = f"M{tip} {ym} l{half} -{half} h{width - half} v{2 * half} h-{width - half} z"
        text = (f'<text x="{wx + half + 6}" y="{ym}" dominant-baseline="central" '
                f'fill="{c["label"]}">{esc(value)}</text>')
    return [f'<path d="{box}" fill="none" stroke="{c["label"]}" stroke-width="1"/>', text]


def title_block(c, height):
    """The title block in the corner of the sheet, with lines on half pixels."""
    tw, th = 232, 46
    x0, y0 = WIDTH - tw - 16, height - th - 14
    mid = y0 + 23
    stroke = f'stroke="{c["outline"]}" stroke-width="1"'
    out = [f'<rect x="{x0 + 0.5}" y="{y0 + 0.5}" width="{tw}" height="{th}" fill="none" {stroke}/>',
           f'<line x1="{x0}" y1="{mid + 0.5}" x2="{x0 + tw}" y2="{mid + 0.5}" {stroke}/>',
           f'<line x1="{x0 + 116.5}" y1="{mid}" x2="{x0 + 116.5}" y2="{y0 + th}" {stroke}/>']
    fields = [(x0 + 8, y0 + 12, "Title: ", "Ciprian-Florin Ifrim"), (x0 + 8, mid + 12, "Rev: ", "C"),
              (x0 + 124, mid + 12, "Sheet: ", "1/1")]
    for x, y, name, value in fields:
        out.append(f'<text x="{x}" y="{y}" dominant-baseline="central" font-size="10.5" '
                   f'fill="{c["label"]}"><tspan fill="{c["faint"]}">{name}</tspan>{value}</text>')
    return out


def chip(theme):
    c = THEMES[theme]
    count = len(PINS)
    pitch, bx, bw, by = 36, 360, 240, 44
    bh = count // 2 * pitch + 18
    height = by + bh + 44 + 42
    centre_y = by + bh / 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" '
           f'height="{height}" font-family="{MONO}" font-size="12">',
           '<defs><pattern id="g" width="12.7" height="12.7" patternUnits="userSpaceOnUse">'
           f'<circle cx="1" cy="1" r="0.9" fill="{c["grid"]}"/></pattern></defs>',
           f'<rect width="{WIDTH}" height="{height}" rx="6" fill="{c["sheet"]}"/>',
           f'<rect width="{WIDTH}" height="{height}" rx="6" fill="url(#g)"/>',
           f'<g transform="translate({WIDTH / 2} {centre_y}) scale({SCALE}) '
           f'translate({-WIDTH / 2} {-centre_y})">',
           f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{c["body"]}" '
           f'stroke="{c["outline"]}" stroke-width="2"/>']
    for num, name, value in PINS:
        y = by + 27 + row(num, count) * pitch
        left = num <= count // 2
        x0, x1 = (bx - 36, bx) if left else (bx + bw, bx + bw + 36)
        end = x0 if left else x1
        out.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{c["pin"]}" stroke-width="1.5"/>')
        out.append(f'<text x="{(bx - 18) if left else (bx + bw + 18)}" y="{y - 5}" text-anchor="middle" '
                   f'font-size="10" fill="{c["pnum"]}">{num}</text>')
        tx, anchor = (bx + 8, "start") if left else (bx + bw - 8, "end")
        out.append(f'<text x="{tx}" y="{y + 4}" text-anchor="{anchor}" fill="{c["pname"]}">{name}</text>')
        if value is None:
            out.append(f'<path d="M{end - 5} {y - 5} l10 10 M{end - 5} {y + 5} l10 -10" '
                       f'stroke="{c["nc"]}" stroke-width="1.5"/>')
        elif isinstance(value, tuple):
            out += power_symbol(c, value[1], end, y, left)
        else:
            wx = (x0 - 30) if left else (x1 + 30)
            out.append(f'<line x1="{x0}" y1="{y}" x2="{wx}" y2="{y}" '
                       f'stroke="{c["wire"]}" stroke-width="1.5"/>')
            out.append(f'<circle cx="{end}" cy="{y}" r="1.8" fill="{c["pin"]}"/>')
            out += net_label(c, value, wx, y, left)
    out.append(f'<text x="{bx}" y="{by - 12}" fill="{c["pname"]}">U1</text>')
    out.append(f'<text x="{bx + bw}" y="{by + bh + 20}" text-anchor="end" '
               f'fill="{c["pname"]}">CIP-1999</text>')
    out.append("</g>")
    out.append(f'<g transform="translate({WIDTH} {height}) scale({SCALE}) translate({-WIDTH} {-height})">')
    out += title_block(c, height)
    out.append("</g>")
    out.append("</svg>")
    return "".join(out)


def main():
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "assets")
    target.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (target / f"chip-{theme}.svg").write_text(chip(theme) + "\n", encoding="utf-8")
    print("wrote the chip in dark and light to " + str(target))


if __name__ == "__main__":
    main()
