#!/usr/bin/env python3
"""Draw the serial boot log of the profile README, in a dark and a light version.

    python3 scripts/make-boot-log.py assets

The script writes boot-log-dark.svg and boot-log-light.svg into the directory it is given. The count
on the rx line comes from views.txt in the root of the repository, which the workflow
.github/workflows/views.yml rewrites each day. The cursor on the last line blinks.
"""
import sys
from pathlib import Path

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
WIDTH = 960
FONT_SIZE = 13
LINE = 24

THEMES = {
    "dark": dict(bg="#0d1117", edge="#30363d", text="#e6edf3", muted="#7d8590", accent="#78a9ff",
                 green="#3fb950", amber="#d29922"),
    "light": dict(bg="#ffffff", edge="#d0d7de", text="#1f2328", muted="#59636e", accent="#0969da",
                  green="#1a7f37", amber="#9a6700"),
}

READY = "ask me about edge AI, robotics, electronics and 3D modelling"


def lines(views):
    """The log as a list of (tag, message), in the order of the boot."""
    return [
        ("boot", "CIP-1999 rev C, Ciprian-Florin Ifrim, marking Cip, London"),
        ("fndr0", "Future Machines, bespoke liquid-cooled computers and servers"),
        ("fndr1", "Brainquiver, AURI language models on MCUs, n chips, 0 cloud calls"),
        ("fndr2", "Britready, Life in the UK webapp with analytics and AI assistance"),
        ("edu", "3 MSc and 1 BEng, robotics to AI"),
        ("lang", "English, Italian, Romanian, French"),
        ("vdd", "passion, stable"),
        ("idle", "robots, space, tango, piloting"),
        ("rx", f"{views} profile views"),
    ]


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def log(theme, views):
    c = THEMES[theme]
    entries = lines(views)
    top = 44
    height = top + (len(entries) + 1) * LINE + 20
    char = FONT_SIZE * 0.6
    tag_x = 24 + 7 * char + 10
    msg_x = tag_x + 6 * char + 10
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" '
           f'height="{height}" font-family="{FONT}" font-size="{FONT_SIZE}">',
           f'<rect width="{WIDTH}" height="{height}" rx="10" fill="{c["bg"]}" stroke="{c["edge"]}"/>',
           f'<text x="24" y="26" fill="{c["muted"]}">serial  /dev/tty.cip  115200 baud</text>',
           f'<line x1="0" y1="38" x2="{WIDTH}" y2="38" stroke="{c["edge"]}"/>']
    y = top + 14
    for step, (tag, message) in enumerate(entries):
        out.append(f'<text x="24" y="{y}" fill="{c["green"]}">[0.{step * 2:03d}]</text>'
                   f'<text x="{tag_x:.1f}" y="{y}" fill="{c["accent"]}">{tag}</text>'
                   f'<text x="{msg_x:.1f}" y="{y}" fill="{c["text"]}">{esc(message)}</text>')
        y += LINE
    out.append(f'<text x="24" y="{y}" fill="{c["green"]}">[0.{len(entries) * 2:03d}]</text>'
               f'<text x="{tag_x:.1f}" y="{y}" fill="{c["amber"]}">ready&gt;</text>'
               f'<text x="{msg_x:.1f}" y="{y}" fill="{c["text"]}">{esc(READY)}</text>')
    cursor_x = msg_x + len(READY) * char + 6
    out.append(f'<rect x="{cursor_x:.0f}" y="{y - 12}" width="8" height="15" fill="{c["text"]}">'
               '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.2s" '
               'repeatCount="indefinite"/></rect>')
    out.append("</svg>")
    return "".join(out)


def main():
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "assets")
    views = (Path(__file__).resolve().parent.parent / "views.txt").read_text(encoding="utf-8").strip()
    target.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (target / f"boot-log-{theme}.svg").write_text(log(theme, views) + "\n", encoding="utf-8")
    print("wrote the boot log in dark and light to " + str(target))


if __name__ == "__main__":
    main()
