#!/usr/bin/env python3
"""Fetch the IBM Plex Mono woff2 subsets that the site self-hosts.

The fonts are committed to the repository, so this script is only needed
when the family or the weights change. It asks Google Fonts for the
current woff2 URLs, keeps only the subsets the site uses, and writes
them into fonts/.

It also rewrites the @font-face block in scripts/build-markup.py is NOT
touched -- the generator reads the font names, weights and unicode
ranges from its own constants, so the files and the CSS cannot drift
apart by accident.

Run:  python3 scripts/fetch-fonts.py
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "fonts"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def fetch(url, dest=None):
    cmd = ["curl", "-s", "--max-time", "40", "-A", UA]
    if dest:
        cmd += ["-o", str(dest)]
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True, check=True).stdout


def main():
    # Keep in step with PLEX_WEIGHTS / PLEX_SUBSETS in build-markup.py.
    weights = [400, 500]
    subsets = ["latin", "latin-ext"]

    family = "+".join(
        f"IBM+Plex+Mono:wght@{w}" for w in weights
    )
    url = f"https://fonts.googleapis.com/css2?family={family}&display=swap"

    css = fetch(url).decode("utf-8")
    OUT.mkdir(parents=True, exist_ok=True)

    blocks = re.findall(r"@font-face\s*\{(.*?)\}", css, re.S)
    found = 0
    for b in blocks:
        wt = re.search(r"font-weight:\s*(\d+)", b)
        src = re.search(r"url\((https://[^)]+\.woff2)\)", b)
        ur = re.search(r"unicode-range:\s*([^;]+);", b)
        if not (wt and src and ur):
            continue
        urange = ur.group(1).strip()
        if urange.startswith("U+0000-00FF"):
            label = "latin"
        elif urange.startswith("U+0100-02BA"):
            label = "latin-ext"
        else:
            continue
        if int(wt.group(1)) not in weights or label not in subsets:
            continue
        name = f"IBMPlexMono-{wt.group(1)}-{label}.woff2"
        dest = OUT / name
        fetch(src.group(1), dest)
        print(f"{name}  {dest.stat().st_size} bytes")
        found += 1

    if found != len(weights) * len(subsets):
        print(f"expected {len(weights) * len(subsets)} files, wrote {found}",
              file=sys.stderr)
        return 1
    print(f"\n{found} font files in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
