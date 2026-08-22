#!/usr/bin/env python3
"""Auto-generate animated cyberpunk project cards for every public repo.

Usage:
  python scripts/generate_featured.py [repos.json]

Without an argument it fetches the repo list from the GitHub API
(authenticated with GITHUB_TOKEN when set). With an argument it reads a
JSON array of repo objects (as produced by `gh api users/<owner>/repos`).

It writes one SVG card per repo into assets/cards/ and rebuilds the README
section between the FEATURED:AUTO markers.
"""

import json
import os
import sys
import urllib.request
from string import Template
from xml.sax.saxutils import escape as xesc

OWNER = "akashmark8-cloud"
PROFILE_REPO = "akashmark8-cloud"  # the profile repo itself is never featured
MAX_CARDS = 6
CARD_DIR = os.path.join("assets", "cards")
README = "README.md"
START_MARK = "<!-- FEATURED:AUTO:START -->"
END_MARK = "<!-- FEATURED:AUTO:END -->"

LANG_COLORS = {
    "Python": "#3572A5",
    "C++": "#f34b7d",
    "C": "#555555",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Shell": "#89e051",
    "Java": "#b07219",
    "Kotlin": "#A97BFF",
    "Jupyter Notebook": "#DA5B0B",
}

CARD_TEMPLATE = Template("""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="280" viewBox="0 0 400 280" font-family="'Segoe UI', Helvetica, Arial, sans-serif">
  <style>
    @keyframes neonhue { 0% { stop-color:#00fff7; } 33% { stop-color:#ff2ec4; } 66% { stop-color:#7b2eff; } 100% { stop-color:#00fff7; } }
    .neonborder stop { animation: neonhue 6s linear infinite; }
    .neonborder stop:nth-of-type(2) { animation-delay: 2s; }
    @keyframes scanmove { 0% { transform: translateY(-30px); } 100% { transform: translateY(320px); } }
    .scanline { animation: scanmove 4s linear infinite; }
    @keyframes flicker { 0%,91%,94%,98%,100% { opacity: 1; } 92% { opacity: 0.45; } 96% { opacity: 0.7; } }
    .neontext { animation: flicker 3.9s linear infinite; }
    @keyframes glitchA {
      0%,84%,100% { transform: translate(0,0); opacity: 0; }
      85% { transform: translate(-2.5px,1px); opacity: 1; }
      87% { transform: translate(2px,-1px); opacity: 1; }
      89% { transform: translate(-1px,-1px); opacity: 1; }
      91% { transform: translate(0,0); opacity: 0; }
    }
    @keyframes glitchB {
      0%,80%,100% { transform: translate(0,0); opacity: 0; }
      81% { transform: translate(2.5px,-1px); opacity: 1; }
      83% { transform: translate(-2px,1px); opacity: 1; }
      85% { transform: translate(1px,1px); opacity: 1; }
      87% { transform: translate(0,0); opacity: 0; }
    }
    .gcyan { animation: glitchA 4.2s steps(1) infinite; }
    .gmagenta { animation: glitchB 4.2s steps(1) infinite 1.1s; }
    @keyframes livedot { 0%,100% { opacity: 1; } 50% { opacity: 0.25; } }
    .live { animation: livedot 1.6s ease-in-out infinite; }
    @keyframes gridroll { 0% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: -28; } }
    .gridline { stroke-dasharray: 14 14; animation: gridroll 3s linear infinite; }
  </style>
  <defs>
    <linearGradient id="cbg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#05060f"/><stop offset="1" stop-color="#120a26"/>
    </linearGradient>
    <linearGradient class="neonborder" id="nstroke" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#00fff7"/><stop offset="0.5" stop-color="#ff2ec4"/><stop offset="1" stop-color="#7b2eff"/>
    </linearGradient>
    <linearGradient id="scanfade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#00fff7" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#00fff7" stop-opacity="0.10"/>
      <stop offset="1" stop-color="#00fff7" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="cardclip"><rect x="1.5" y="1.5" width="397" height="277" rx="14"/></clipPath>
  </defs>

  <rect x="1.5" y="1.5" width="397" height="277" rx="14" fill="url(#cbg)" stroke="url(#nstroke)" stroke-width="2"/>

  <!-- HUD corner brackets -->
  <g stroke="#00fff7" stroke-width="2" fill="none" opacity="0.85">
    <path d="M14 30 V14 H30"/><path d="M370 14 H386 V30"/>
    <path d="M386 250 V266 H370"/><path d="M30 266 H14 V250"/>
  </g>

  <g clip-path="url(#cardclip)">
    <!-- faint perspective grid -->
    <g stroke="#1b1440" stroke-width="1">
      <line class="gridline" x1="0" y1="238" x2="400" y2="238"/>
      <line class="gridline" x1="0" y1="252" x2="400" y2="252" opacity="0.7"/>
      <line class="gridline" x1="0" y1="266" x2="400" y2="266" opacity="0.45"/>
    </g>
    <!-- rolling scanline -->
    <rect class="scanline" x="0" y="0" width="400" height="16" fill="url(#scanfade)"/>
    <!-- scanline texture -->
    <g fill="#ffffff" opacity="0.03">
      $SCANLINES
    </g>
  </g>

  <!-- header row -->
  <circle cx="30" cy="36" r="6" fill="$LANGCOLOR"/>
  <text x="44" y="41" font-size="12" fill="#9fb4c7" font-family="'JetBrains Mono', Consolas, monospace">$LANGNAME</text>
  <circle class="live" cx="352" cy="35" r="4" fill="#39ff88"/>
  <text x="360" y="39" font-size="10" fill="#39ff88" font-family="'JetBrains Mono', Consolas, monospace">LIVE</text>

  <!-- glitching title -->
  <g font-size="24" font-weight="800">
    <text class="gcyan" x="198" y="92" text-anchor="middle" fill="#00fff7" opacity="0">$NAME</text>
    <text class="gmagenta" x="202" y="94" text-anchor="middle" fill="#ff2ec4" opacity="0">$NAME</text>
    <text class="neontext" x="200" y="93" text-anchor="middle" fill="#f4f7ff">$NAME</text>
  </g>

  <!-- description -->
  <text x="200" y="126" text-anchor="middle" font-size="12.5" fill="#b8c7d9">$DESC1</text>
  <text x="200" y="145" text-anchor="middle" font-size="12.5" fill="#b8c7d9">$DESC2</text>

  <!-- stat chips -->
  <g font-family="'JetBrains Mono', Consolas, monospace" font-size="11">
    <rect x="106" y="168" width="72" height="22" rx="11" fill="#0d1226" stroke="#00fff7" stroke-opacity="0.55"/>
    <text x="142" y="183" text-anchor="middle" fill="#00fff7">&#9733; $STARS</text>
    <rect x="186" y="168" width="66" height="22" rx="11" fill="#0d1226" stroke="#ff2ec4" stroke-opacity="0.55"/>
    <text x="219" y="183" text-anchor="middle" fill="#ff2ec4">&#9023; $FORKS</text>
    <rect x="$LANGX" y="168" width="$LANGW" height="22" rx="11" fill="#0d1226" stroke="$LANGCOLOR" stroke-opacity="0.7"/>
    <text x="$LANGTX" y="183" text-anchor="middle" fill="$LANGCOLOR">$LANGSHORT</text>
  </g>

  <!-- footer -->
  <text x="200" y="228" text-anchor="middle" font-size="10" fill="#5b6b85" font-family="'JetBrains Mono', Consolas, monospace">github.com/$REPOPATH</text>
  <text x="200" y="248" text-anchor="middle" font-size="9" fill="#3f4d63" letter-spacing="2">// SYSTEM ONLINE //</text>
</svg>
""")


def lang_color(lang):
    return LANG_COLORS.get(lang or "", "#bd93f9")


def wrap_desc(text):
    """Split into max two ~44-char lines."""
    if not text:
        return "-", ""
    text = str(text).replace("\r", " ").replace("\n", " ")
    words, line1, line2 = text.split(), "", ""
    for w in words:
        if len(line1) + len(w) + (1 if line1 else 0) <= 44 and not line2:
            line1 = (line1 + " " + w).strip()
        else:
            rest = line2 + " " + w
            if len(rest.strip()) <= 44:
                line2 = rest.strip()
            else:
                line2 = (line2 + " " + w).strip()[:41].rsplit(" ", 1)[0] + "..."
                break
    if not line2 and len(line1) > 44:
        cut = line1[:41].rsplit(" ", 1)[0]
        line2 = line1[len(cut):].strip()
        line1 = cut
    return line1 or "-", (line2 + ("..." if line2 and text.endswith(line2) and False else ""))


def scanline_rows():
    rows = []
    for y in range(6, 280, 6):
        rows.append('<rect x="0" y="%d" width="400" height="1"/>' % y)
    return "\n      ".join(rows)


def make_card(repo):
    name = repo["name"]
    lang = (repo.get("language") or "")
    color = lang_color(repo.get("language"))
    desc1, desc2 = wrap_desc(repo.get("description"))
    short = (lang[:9] or "code").upper()
    langw = max(50, 9 * len(short) + 28)
    langx = 260
    svg = CARD_TEMPLATE.substitute(
        SCANLINES=scanline_rows(),
        LANGCOLOR=color,
        LANGNAME=xesc(lang or "unknown"),
        NAME=xesc(name),
        DESC1=xesc(desc1),
        DESC2=xesc(desc2),
        STARS=str(repo.get("stargazers_count", 0)),
        FORKS=str(repo.get("forks_count", 0)),
        LANGSHORT=xesc(short),
        LANGX=str(langx),
        LANGW=str(langw),
        LANGTX=str(langx + langw // 2),
        REPOPATH=xesc("%s/%s" % (OWNER, name)),
    )
    return svg


def load_repos():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as fh:
            return json.load(fh)
    url = "https://api.github.com/users/%s/repos?per_page=100&sort=pushed" % OWNER
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "featured-cards-generator")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main():
    repos = load_repos()
    featured = [
        r for r in repos
        if r["name"] != PROFILE_REPO and not r.get("fork") and not r.get("private")
    ]
    featured.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    featured = featured[:MAX_CARDS]
    print("featuring %d repo(s): %s" % (len(featured), ", ".join(r["name"] for r in featured)))

    os.makedirs(CARD_DIR, exist_ok=True)
    keep = set()
    cells = []
    for repo in featured:
        name = repo["name"]
        path = os.path.join(CARD_DIR, "%s.svg" % name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(make_card(repo))
        keep.add(path)
        cells.append(
            '[![%s](%s/%s.svg)](https://github.com/%s/%s)'
            % (xesc(name), CARD_DIR, xesc(name), OWNER, xesc(name))
        )

    # drop cards for repos that disappeared
    for existing in os.listdir(CARD_DIR):
        p = os.path.join(CARD_DIR, existing)
        if p not in keep:
            os.remove(p)
            print("removed stale card:", existing)

    rows = []
    per_row = 3
    for i in range(0, len(cells), per_row):
        rows.append("\n".join(cells[i:i + per_row]) + "\n")

    block = (
        START_MARK + "\n<div align=\"center\">\n\n"
        + ("\n".join(rows)).strip() + "\n\n</div>\n" + END_MARK
    )

    with open(README, encoding="utf-8") as fh:
        readme = fh.read()

    start = readme.find(START_MARK)
    end = readme.find(END_MARK)
    if start == -1 or end == -1:
        raise SystemExit("README is missing the FEATURED:AUTO markers")
    readme = readme[:start] + block + "\n" + readme[end + len(END_MARK):]

    with open(README, "w", encoding="utf-8") as fh:
        fh.write(readme)
    print("README updated.")


if __name__ == "__main__":
    main()
