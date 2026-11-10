#!/usr/bin/env python3
"""Auto-generate animated cyberpunk project cards for every public repo.

Usage:
  python scripts/generate_featured.py [repos.json]

Fetches public non-fork, non-archived repos via GitHub API (or reads repos.json),
generates animated cyberpunk SVG cards in assets/cards/, and updates README.md
between <!-- FEATURED:AUTO:START --> and <!-- FEATURED:AUTO:END -->.
"""

import json
import os
import sys
import urllib.request
from string import Template
from xml.sax.saxutils import escape as xesc

OWNER = "akashmark8-cloud"
PROFILE_REPO = "akashmark8-cloud"
MAX_CARDS = 24
CARD_DIR = os.path.join("assets", "cards")
README = "README.md"
START_MARK = "<!-- FEATURED:AUTO:START -->"
END_MARK = "<!-- FEATURED:AUTO:END -->"

LANG_COLORS = {
    "Python": "#38bdf8",
    "C#": "#39ff88",
    "C++": "#ff2ec4",
    "C": "#94a3b8",
    "TypeScript": "#00fff7",
    "JavaScript": "#facc15",
    "PowerShell": "#60a5fa",
    "HTML": "#fb7185",
    "CSS": "#c084fc",
    "Go": "#22d3ee",
    "Rust": "#fb923c",
    "Shell": "#4ade80",
    "Java": "#f59e0b",
    "Kotlin": "#a78bfa",
}

FALLBACK_DESCRIPTIONS = {
    "skiplink": "One-click bypass for ad-driven URL shorteners — lands on the real link with zero ads.",
}

CARD_TEMPLATE = Template("""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="270" viewBox="0 0 420 270" font-family="'Segoe UI', system-ui, -apple-system, sans-serif">
  <style>
    @keyframes neonhue {
      0%   { stop-color: #00fff7; }
      33%  { stop-color: #ff2ec4; }
      66%  { stop-color: #7b2eff; }
      100% { stop-color: #00fff7; }
    }
    .neonborder stop { animation: neonhue 6.5s linear infinite $DELAY1; }
    .neonborder stop:nth-of-type(2) { animation-delay: $DELAY2; }

    @keyframes scanmove {
      0%   { transform: translateY(-30px); }
      100% { transform: translateY(300px); }
    }
    .scanline { animation: scanmove 4.2s linear infinite $DELAY1; }

    @keyframes flicker {
      0%, 91%, 94%, 98%, 100% { opacity: 1; }
      92% { opacity: 0.48; }
      96% { opacity: 0.72; }
    }
    .neontext { animation: flicker 4.2s linear infinite $DELAY1; }

    @keyframes glitchA {
      0%, 84%, 100% { transform: translate(0, 0); opacity: 0; }
      85% { transform: translate(-2.5px, 1px); opacity: 0.95; }
      87% { transform: translate(2px, -1px); opacity: 0.9; }
      89% { transform: translate(-1px, -1px); opacity: 0.95; }
      91% { transform: translate(0, 0); opacity: 0; }
    }
    @keyframes glitchB {
      0%, 80%, 100% { transform: translate(0, 0); opacity: 0; }
      81% { transform: translate(2.5px, -1px); opacity: 0.95; }
      83% { transform: translate(-2px, 1px); opacity: 0.9; }
      85% { transform: translate(1px, 1px); opacity: 0.95; }
      87% { transform: translate(0, 0); opacity: 0; }
    }
    .gcyan    { animation: glitchA 4.6s steps(1) infinite $DELAY1; }
    .gmagenta { animation: glitchB 4.6s steps(1) infinite $DELAY2; }

    @keyframes livedot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50%      { opacity: 0.3; transform: scale(0.8); }
    }
    .live { transform-origin: 344px 33px; animation: livedot 1.7s ease-in-out infinite; }

    @keyframes gridroll {
      0%   { stroke-dashoffset: 0; }
      100% { stroke-dashoffset: -28; }
    }
    .gridline { stroke-dasharray: 14 14; animation: gridroll 3s linear infinite; }

    @keyframes edgePulse {
      0%   { transform: translateX(-90px); opacity: 0; }
      20%  { opacity: 0.95; }
      80%  { opacity: 0.95; }
      100% { transform: translateX(430px); opacity: 0; }
    }
    .edge-pk { animation: edgePulse 3.8s linear infinite $DELAY1; }
  </style>

  <defs>
    <linearGradient id="cbg" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0" stop-color="#050610"/>
      <stop offset="1" stop-color="#110926"/>
    </linearGradient>
    <linearGradient class="neonborder" id="nstroke" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#00fff7"/>
      <stop offset="0.5" stop-color="#ff2ec4"/>
      <stop offset="1" stop-color="#7b2eff"/>
    </linearGradient>
    <linearGradient id="scanfade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#00fff7" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#00fff7" stop-opacity="0.11"/>
      <stop offset="1" stop-color="#00fff7" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="pkgrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#00fff7" stop-opacity="0"/>
      <stop offset="50%" stop-color="#00fff7" stop-opacity="1"/>
      <stop offset="100" stop-color="#ff2ec4" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="cardclip"><rect x="1.5" y="1.5" width="417" height="267" rx="14"/></clipPath>
  </defs>

  <rect x="1.5" y="1.5" width="417" height="267" rx="14" fill="url(#cbg)" stroke="url(#nstroke)" stroke-width="2"/>

  <!-- HUD Corner Brackets -->
  <g stroke="#00fff7" stroke-width="2.2" fill="none" opacity="0.9">
    <path d="M14 30 V14 H30"/>
    <path d="M390 14 H406 V30"/>
    <path d="M406 240 V256 H390" stroke="#ff2ec4"/>
    <path d="M30 256 H14 V240" stroke="#ff2ec4"/>
  </g>

  <g clip-path="url(#cardclip)">
    <g stroke="#1b1442" stroke-width="1">
      <line class="gridline" x1="0" y1="226" x2="420" y2="226"/>
      <line class="gridline" x1="0" y1="242" x2="420" y2="242" opacity="0.7"/>
      <line class="gridline" x1="0" y1="258" x2="420" y2="258" opacity="0.45"/>
    </g>
    <rect class="scanline" x="0" y="0" width="420" height="18" fill="url(#scanfade)"/>
    <rect class="edge-pk" x="0" y="1" width="80" height="3" fill="url(#pkgrad)"/>
    <g fill="#ffffff" opacity="0.025">
      $SCANLINES
    </g>
  </g>

  <!-- Header Row -->
  <circle cx="32" cy="34" r="5.5" fill="$LANGCOLOR"/>
  <text x="45" y="38" font-size="11.5" font-weight="700" fill="#cbd5e1" font-family="Consolas, monospace">$LANGNAME</text>

  <rect x="332" y="22" width="66" height="21" rx="10.5" fill="#061e17" stroke="#39ff88" stroke-opacity="0.55"/>
  <circle class="live" cx="344" cy="33" r="3.5" fill="#39ff88"/>
  <text x="353" y="36.5" font-size="9.5" font-weight="700" fill="#39ff88" font-family="Consolas, monospace">PUBLIC</text>

  <!-- Glitching Title -->
  <g font-size="$TITLE_SIZE" font-weight="800" letter-spacing="0.4">
    <text class="gcyan"    x="208" y="88" text-anchor="middle" fill="#00fff7" opacity="0">$NAME</text>
    <text class="gmagenta" x="212" y="90" text-anchor="middle" fill="#ff2ec4" opacity="0">$NAME</text>
    <text class="neontext" x="210" y="89" text-anchor="middle" fill="#f8fafc">$NAME</text>
  </g>

  <!-- Description -->
  <text x="210" y="122" text-anchor="middle" font-size="12.5" fill="#b8c7d9">$DESC1</text>
  <text x="210" y="142" text-anchor="middle" font-size="12.5" fill="#b8c7d9">$DESC2</text>

  <!-- Centered Stat Chips with Vector Icons -->
  <g font-family="Consolas, monospace" font-size="11" font-weight="700">
    <!-- Stars Chip -->
    <rect x="$STAR_X" y="166" width="$STAR_W" height="24" rx="12" fill="#0b1228" stroke="#00fff7" stroke-opacity="0.6"/>
    <path d="M$STAR_IX 173 L$STAR_IX2 176.2 L$STAR_IX3 176.5 L$STAR_IX4 178.7 L$STAR_IX5 182 L$STAR_IX 180.2 L$STAR_IX6 182 L$STAR_IX7 178.7 L$STAR_IX8 176.5 L$STAR_IX9 176.2 Z" fill="#00fff7"/>
    <text x="$STAR_TX" y="182" fill="#00fff7">$STARS</text>

    <!-- Forks Chip -->
    <rect x="$FORK_X" y="166" width="$FORK_W" height="24" rx="12" fill="#170b26" stroke="#ff2ec4" stroke-opacity="0.6"/>
    <circle cx="$FORK_C1X" cy="174" r="1.6" fill="#ff2ec4"/>
    <circle cx="$FORK_C2X" cy="174" r="1.6" fill="#ff2ec4"/>
    <circle cx="$FORK_C3X" cy="182" r="1.6" fill="#ff2ec4"/>
    <path d="M$FORK_C1X 175.5 V178 H$FORK_C2X V175.5 M$FORK_C3X 178 V180.5" stroke="#ff2ec4" stroke-width="1.3" fill="none"/>
    <text x="$FORK_TX" y="182" fill="#ff2ec4">$FORKS</text>

    <!-- Language / Activity Chip -->
    <rect x="$LANG_X" y="166" width="$LANG_W" height="24" rx="12" fill="#0b1228" stroke="$LANGCOLOR" stroke-opacity="0.75"/>
    <text x="$LANG_TX" y="182" text-anchor="middle" fill="$LANGCOLOR">$LANGSHORT</text>
  </g>

  <!-- Footer HUD -->
  <text x="210" y="220" text-anchor="middle" font-size="10.5" fill="#7c8ea8" font-family="Consolas, monospace">&gt; github.com/$REPOPATH</text>
  <text x="210" y="242" text-anchor="middle" font-size="9.5" fill="#4f5f7a" font-family="Consolas, monospace" letter-spacing="1.6">// UPDATED $UPDATED //</text>
</svg>
""")


def lang_color(lang):
    return LANG_COLORS.get(lang or "", "#a78bfa")


def wrap_desc(text):
    """Split into max two ~48-char lines without awkward mid-word cuts."""
    if not text:
        return "Open-source project by @akashmark8-cloud", ""
    text = " ".join(str(text).replace("\r", " ").replace("\n", " ").split())
    limit = 48
    if len(text) <= limit:
        return text, ""
    words = text.split(" ")
    line1 = ""
    idx = 0
    for i, w in enumerate(words):
        cand = (line1 + " " + w).strip()
        if len(cand) <= limit:
            line1 = cand
            idx = i + 1
        else:
            break
    if not line1:
        line1 = words[0][:limit]
        idx = 1

    rest_words = words[idx:]
    line2 = ""
    for i, w in enumerate(rest_words):
        cand = (line2 + " " + w).strip()
        if len(cand) <= limit - 3:
            line2 = cand
        else:
            line2 = (line2 or w[:limit - 3]).rstrip(".") + "..."
            break
    return line1, line2


def scanline_rows():
    return "\n      ".join('<rect x="0" y="%d" width="420" height="1"/>' % y for y in range(6, 270, 6))


def fit_title(name):
    n = len(name)
    if n <= 14:
        return name, "24"
    if n <= 20:
        return name, "20"
    if n <= 27:
        return name, "16.5"
    return name[:26] + "...", "15.5"


def make_card(repo, card_index):
    raw_name = repo["name"]
    disp_name, title_size = fit_title(raw_name)
    lang = repo.get("language") or ""
    color = lang_color(lang)
    desc_raw = (repo.get("description") or "").strip() or FALLBACK_DESCRIPTIONS.get(raw_name.lower(), "")
    desc1, desc2 = wrap_desc(desc_raw)

    stars = str(repo.get("stargazers_count", 0))
    forks = str(repo.get("forks_count", 0))
    short = (lang[:10] or "CODE").upper()

    star_w = max(58, 30 + 7 * len(stars))
    fork_w = max(56, 30 + 7 * len(forks))
    lang_w = max(62, 24 + 8 * len(short))
    gap = 10
    total_w = star_w + gap + fork_w + gap + lang_w
    start_x = (420 - total_w) // 2

    star_x = start_x
    fork_x = star_x + star_w + gap
    lang_x = fork_x + fork_w + gap

    # Star icon centered at star_x + 16
    sx = star_x + 16
    fcx = fork_x + 15

    pushed = (repo.get("pushed_at") or repo.get("updated_at") or "")[:7] or "LIVE"

    delay1 = "%.1fs" % ((card_index * 0.7) % 3.5)
    delay2 = "%.1fs" % (((card_index * 0.7) + 1.4) % 4.0)

    return CARD_TEMPLATE.substitute(
        DELAY1=delay1,
        DELAY2=delay2,
        SCANLINES=scanline_rows(),
        LANGCOLOR=color,
        LANGNAME=xesc(lang or "Multi-Lang"),
        NAME=xesc(disp_name),
        TITLE_SIZE=title_size,
        DESC1=xesc(desc1),
        DESC2=xesc(desc2),
        STAR_X=str(star_x),
        STAR_W=str(star_w),
        STAR_TX=str(star_x + 26),
        STAR_IX=str(sx),
        STAR_IX2=str(sx + 1.4),
        STAR_IX3=str(sx + 4.8),
        STAR_IX4=str(sx + 2.2),
        STAR_IX5=str(sx + 3.0),
        STAR_IX6=str(sx - 3.0),
        STAR_IX7=str(sx - 2.2),
        STAR_IX8=str(sx - 4.8),
        STAR_IX9=str(sx - 1.4),
        STARS=stars,
        FORK_X=str(fork_x),
        FORK_W=str(fork_w),
        FORK_C1X=str(fcx - 3),
        FORK_C2X=str(fcx + 3),
        FORK_C3X=str(fcx),
        FORK_TX=str(fork_x + 26),
        FORKS=forks,
        LANG_X=str(lang_x),
        LANG_W=str(lang_w),
        LANG_TX=str(lang_x + lang_w // 2),
        LANGSHORT=xesc(short),
        REPOPATH=xesc("%s/%s" % (OWNER, raw_name)),
        UPDATED=xesc(pushed),
    )


def load_repos():
    if len(sys.argv) > 1:
        raw = open(sys.argv[1], "rb").read()
        for enc in ("utf-8-sig", "utf-16", "utf-8"):
            try:
                return json.loads(raw.decode(enc))
            except UnicodeDecodeError:
                continue
        raise ValueError("Unable to decode " + sys.argv[1])
    url = "https://api.github.com/users/%s/repos?type=public&per_page=100&sort=pushed" % OWNER
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "featured-cards-generator")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main():
    repos = load_repos()
    featured = [
        r for r in repos
        if r["name"] != PROFILE_REPO
        and not r.get("fork")
        and not r.get("private")
        and not r.get("archived")
    ]
    featured.sort(key=lambda r: r.get("pushed_at") or r.get("updated_at") or "", reverse=True)
    featured = featured[:MAX_CARDS]
    print("featuring %d repo(s): %s" % (len(featured), ", ".join(r["name"] for r in featured)))

    os.makedirs(CARD_DIR, exist_ok=True)
    keep = set()
    tags = []
    for idx, repo in enumerate(featured):
        name = repo["name"]
        path = os.path.join(CARD_DIR, "%s.svg" % name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(make_card(repo, idx))
        keep.add(os.path.normpath(path))
        tags.append(
            '<a href="https://github.com/%s/%s"><img src="assets/cards/%s.svg" width="405" alt="%s"></a>'
            % (OWNER, xesc(name), xesc(name), xesc(name))
        )

    for existing in os.listdir(CARD_DIR):
        p = os.path.normpath(os.path.join(CARD_DIR, existing))
        if p not in keep:
            os.remove(p)
            print("removed stale card:", existing)

    rows = []
    for i in range(0, len(tags), 2):
        rows.append("  " + " ".join(tags[i:i + 2]))

    block = (
        START_MARK
        + '\n<p align="center">\n'
        + "\n  <br/>\n".join(rows)
        + "\n</p>\n"
        + END_MARK
    )

    with open(README, encoding="utf-8") as fh:
        readme = fh.read()

    start = readme.find(START_MARK)
    end = readme.find(END_MARK)
    if start == -1 or end == -1:
        raise SystemExit("README is missing the FEATURED:AUTO markers")
    after = readme[end + len(END_MARK):].lstrip("\r\n")
    readme = readme[:start] + block + "\n\n" + after

    with open(README, "w", encoding="utf-8") as fh:
        fh.write(readme)
    print("README updated.")


if __name__ == "__main__":
    main()
