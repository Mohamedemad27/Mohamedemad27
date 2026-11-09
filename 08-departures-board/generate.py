"""Draws the split-flap departures board of my career into ./assets, then builds preview.html.

Each row is one stage, oldest first: when it started, where, the role, the kind of work (gate)
and whether it's done (DEPARTED) or the job I'm in now (IN FLIGHT). Add new jobs to ROWS.
"""
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

MONO = "ui-monospace, 'SFMono-Regular', 'Cascadia Mono', Consolas, 'Liberation Mono', Menlo, monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
YELLOW, WHITE, DIM, GREEN, AMBER = "#FFC72C", "#F4F1E8", "#8A8F98", "#3FD06A", "#FF9F1C"

# (time, destination, role, gate, status) — gates: FT full-time, PT part-time, FL freelance, IN internship
ROWS = [
    ("OCT 22", "FREELANCE", "SOFTWARE ENGINEER", "FL", "DEPARTED"),
    ("AUG 23", "ITI", "SUMMER INTERNSHIP", "IN", "DEPARTED"),
    ("AUG 24", "CIB EGYPT", "INTERNSHIP TRAINEE", "IN", "DEPARTED"),
    ("OCT 24", "ROUTE", "BACK END DEVELOPER", "IN", "DEPARTED"),
    ("JUN 25", "ARAB AFRICAN INTL BANK", "INTERNSHIP TRAINEE", "IN", "DEPARTED"),
    ("JUL 25", "CODEALPHA", "INTERNSHIP TRAINEE", "IN", "DEPARTED"),
    ("JUL 25", "HUDL STATSBOMB", "DATA COLLECTOR", "IN", "DEPARTED"),
    ("AUG 25", "ORANGE EGYPT", "TECHNICAL INTERN", "IN", "DEPARTED"),
    ("SEP 25", "UPWORK", "BACK END DEVELOPER", "FL", "DEPARTED"),
    ("SEP 25", "ITI", "INTERNSHIP TRAINEE", "IN", "DEPARTED"),
    ("JAN 26", "SCALE AI", "SOFTWARE ENGINEER", "PT", "DEPARTED"),
    ("JAN 26", "TRUSTED-IT (TIT)", "BACK END DEVELOPER", "FT", "IN FLIGHT"),
]
CURRENT = "IN FLIGHT"
COLS = [("TIME", 6, YELLOW), ("DESTINATION", 22, WHITE), ("ROLE", 18, YELLOW), ("GATE", 4, YELLOW),
        ("STATUS", 9, YELLOW)]
SKILLS = ["C#", ".NET", "ASP.NET CORE", "EF CORE", "REST APIS", "API TESTING", "TEMENOS T24",
          "AUTOMAPPER", "SQL SERVER", "MYSQL", "ELASTICSEARCH",
          "RABBITMQ", "MASSTRANSIT", "KEYCLOAK", "OPENID CONNECT", "REACT", "TYPESCRIPT", "JAVASCRIPT",
          "BLAZOR", "HTML", "CSS", "BOOTSTRAP", "PYTHON", "DJANGO", "RUST", "FLUTTER", "DART",
          "DOCKER", "GIT", "GITHUB", "POSTMAN", "VISUAL STUDIO", "VS CODE"]

W = 880
PAD = 24
GAP_CELLS = 1                                   # blank cells between columns
N_CELLS = sum(c[1] for c in COLS) + GAP_CELLS * (len(COLS) - 1)
PITCH = (W - 2 * PAD) / N_CELLS
CELL_W, CELL_H, ROW_H = PITCH - 1.6, 24, 32
HEAD_H, COLHEAD_Y = 92, 120
ROW0 = 132
TICK_Y = ROW0 + ROW_H * len(ROWS) + 18
H = TICK_Y + 58

SCRAMBLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
FRAMES, FRAME_T = 6, 0.07
rng = random.Random(27)


def col_starts():
    starts, i = [], 0
    for _, width, _ in COLS:
        starts.append(i)
        i += width + GAP_CELLS
    return starts


STARTS = col_starts()


def cell_x(i):
    return PAD + i * PITCH


def text_run(start, s, y, color, cls="", style=""):
    xs = " ".join(f"{cell_x(start + j) + CELL_W/2:.1f}" for j in range(len(s)))
    # spaces still get a slot so positions stay aligned
    return (f'<text class="{cls}" style="{style}" x="{xs}" y="{y}" font-family="{MONO}" font-size="15" '
            f'font-weight="700" fill="{color}" text-anchor="middle" xml:space="preserve">{escape(s)}</text>')


def build():
    css = f"""
  .scr {{ opacity: 0; }}
  .blink {{ animation: blink 1.1s steps(2, jump-none) infinite; }}
  @keyframes blink {{ 50% {{ opacity: .15; }} }}
  .tick {{ animation: tick 60s linear infinite; }}
  @media (prefers-reduced-motion: reduce) {{ .scr {{ display: none; }} .fin {{ opacity: 1 !important; }} .blink, .tick {{ animation: none; }} }}
"""
    b = []
    b.append(f"""<defs>
  <linearGradient id="bezel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A2D33"/><stop offset="1" stop-color="#15171B"/></linearGradient>
  <linearGradient id="flap" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#26292F"/><stop offset=".49" stop-color="#1D2025"/>
    <stop offset=".51" stop-color="#16181C"/><stop offset="1" stop-color="#1B1D22"/></linearGradient>
  <pattern id="cells" x="{PAD}" y="0" width="{PITCH}" height="{ROW_H}" patternUnits="userSpaceOnUse">
    <rect x="0" y="0" width="{CELL_W}" height="{CELL_H}" rx="2" fill="url(#flap)"/>
  </pattern>
  <pattern id="splits" x="{PAD}" y="0" width="{PITCH}" height="{ROW_H}" patternUnits="userSpaceOnUse">
    <rect x="0" y="{CELL_H/2-0.5}" width="{CELL_W}" height="1" fill="#000" fill-opacity=".85"/>
  </pattern>
  <clipPath id="tickclip"><rect x="{PAD}" y="{TICK_Y}" width="{W-2*PAD}" height="30" rx="4"/></clipPath>
</defs>""")
    b.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="url(#bezel)" stroke="#3A3E45"/>')
    b.append(f'<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="9" fill="#0E0F12"/>')

    # header
    px, py = PAD + 2, 40
    b.append(f'<path transform="translate({px} {py}) scale(1.25)" fill="{YELLOW}" d="M2 14 L10 13 L16 3 L19 3 L16 13 L23 12.5 '
             f'L25.5 9.5 L27.5 9.5 L26.5 14 L27.5 18.5 L25.5 18.5 L23 15.5 L16 15 L19 25 L16 25 L10 15 L2 14 Z"/>')
    b.append(f'<text x="{PAD+46}" y="70" font-family="{SANS}" font-size="30" font-weight="800" fill="{YELLOW}" letter-spacing="3">DEPARTURES</text>')
    b.append(f'<text x="{W-PAD}" y="54" font-family="{SANS}" font-size="18" font-weight="700" fill="{WHITE}" text-anchor="end">MOHAMED EMAD</text>')
    b.append(f'<text x="{W-PAD}" y="74" font-family="{MONO}" font-size="11.5" fill="{DIM}" text-anchor="end" letter-spacing="1">BACKEND DEVELOPER · CAREER SINCE 2022</text>')
    b.append(f'<line x1="{PAD}" y1="{HEAD_H}" x2="{W-PAD}" y2="{HEAD_H}" stroke="#2C3036"/>')

    for (name, width, _), st in zip(COLS, STARTS):
        b.append(f'<text x="{cell_x(st)}" y="{COLHEAD_Y}" font-family="{SANS}" font-size="10.5" font-weight="700" '
                 f'fill="{DIM}" letter-spacing="1.6">{name}</text>')

    # rows
    for r, row in enumerate(ROWS):
        y = ROW0 + r * ROW_H
        for (_, width, _), st in zip(COLS, STARTS):
            b.append(f'<rect x="{cell_x(st)}" y="{y}" width="{width*PITCH - 1.6:.1f}" height="{CELL_H}" fill="url(#cells)"/>')
        ty = y + CELL_H / 2 + 5.5
        t0 = 0.25 + r * 0.13
        for f in range(FRAMES):
            parts = []
            for (_, width, color), st, val in zip(COLS, STARTS, row):
                fake = "".join(rng.choice(SCRAMBLE) if ch != " " else " " for ch in val)
                parts.append(text_run(st, fake, ty, color))
            # SMIL <set>: each scramble frame shows only during its own slot.
            b.append(f'<g class="scr">{"".join(parts)}<set attributeName="opacity" to="1" '
                     f'begin="{t0 + f*FRAME_T:.2f}s" dur="{FRAME_T}s"/></g>')
        final = "".join(text_run(st, val, ty, GREEN if val == CURRENT else color)
                        for (_, width, color), st, val in zip(COLS, STARTS, row))
        # Final text is visible by default; hidden only until its row finishes flipping.
        b.append(f'<g class="fin">{final}<set attributeName="opacity" to="0" begin="0s" '
                 f'dur="{t0 + FRAMES*FRAME_T:.2f}s"/></g>')
        for (_, width, _), st in zip(COLS, STARTS):
            b.append(f'<rect x="{cell_x(st)}" y="{y}" width="{width*PITCH - 1.6:.1f}" height="{CELL_H}" fill="url(#splits)"/>')
        # status light
        status = row[4]
        lx = W - PAD + 2
        color, cls = {CURRENT: (GREEN, "blink"), "SCHEDULED": (AMBER, "")}.get(status, ("#3A3E45", ""))
        b.append(f'<circle class="{cls}" cx="{lx+4}" cy="{y + CELL_H/2}" r="3.5" fill="{color}"/>')

    # ticker
    b.append(f'<rect x="{PAD}" y="{TICK_Y}" width="{W-2*PAD}" height="30" rx="4" fill="#16181C"/>')
    now = next(r for r in ROWS if r[4] == CURRENT)
    msg = "   ◆   ".join([f"NOW: {now[2]} AT {now[1]}"] + SKILLS) + "   ◆   "
    # Two copies laid end to end with a fixed textLength, so the loop distance is exact in every font.
    seg = round(len(msg) * 8.2)
    css += f"  @keyframes tick {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-{seg}px); }} }}\n"
    tick = "".join(
        f'<text x="{k*seg}" y="{TICK_Y+20}" font-family="{MONO}" font-size="13" font-weight="700" fill="{AMBER}" '
        f'textLength="{seg}" lengthAdjust="spacing" xml:space="preserve">{escape(msg)}</text>' for k in range(2))
    b.append(f'<g clip-path="url(#tickclip)"><g transform="translate({PAD+8} 0)"><g class="tick">{tick}</g></g></g>')
    b.append(f'<text x="{W/2}" y="{H-14}" font-family="{MONO}" font-size="10" fill="{DIM}" text-anchor="middle" '
             f'letter-spacing="1.2">GITHUB.COM/MOHAMEDEMAD27</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<style>{css}</style>{"".join(b)}</svg>')


svg = build()
(OUT / "departures.svg").write_text(svg, encoding="utf-8")
print("svg written")


# ─────────────────────────────── preview.html ───────────────────────────────
# Renders README.md the way GitHub does, with a light/dark toggle.
# Open preview.html in a browser. Re-run this script after editing README.md.
import json as _json

_HERE = Path(__file__).resolve().parent
_PREVIEW = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ preview</title>
<link id="css-light" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-light.min.css">
<link id="css-dark" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css" disabled>
<style>
  :root { --bg: #ffffff; --edge: #d0d7de; --muted: #59636e; }
  :root[data-theme="dark"] { --bg: #0d1117; --edge: #30363d; --muted: #8b949e; }
  body { background: var(--bg); margin: 0; font: 14px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }
  .bar { max-width: 1012px; margin: 16px auto 0; padding: 0 16px; display: flex; justify-content: space-between;
         align-items: center; color: var(--muted); }
  .bar button { font: inherit; color: inherit; background: none; border: 1px solid var(--edge); border-radius: 6px;
                padding: 4px 12px; cursor: pointer; }
  .markdown-body { box-sizing: border-box; max-width: 1012px; margin: 12px auto 40px; padding: 32px;
                   border: 1px solid var(--edge); border-radius: 6px; }
  @media (max-width: 767px) { .markdown-body { padding: 16px; margin: 12px 16px 40px; } }
</style>
</head>
<body>
<div class="bar"><span>__TITLE__ / README.md</span><button id="toggle" type="button">Switch theme</button></div>
<article class="markdown-body" id="content"></article>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.0/marked.min.js"></script>
<script>
  const md = __MD__;
  const root = document.getElementById("content");
  root.innerHTML = marked.parse(md, { gfm: true });
  // GitHub picks <picture> sources from the OS theme; the preview picks them from the toggle instead.
  const pics = [...root.querySelectorAll("picture")].map(p => ({
    img: p.querySelector("img"),
    dark: p.querySelector('source[media*="dark"]')?.getAttribute("srcset"),
    light: p.querySelector('source[media*="light"]')?.getAttribute("srcset"),
    sources: [...p.querySelectorAll("source")],
  }));
  pics.forEach(p => p.sources.forEach(s => s.remove()));
  function apply(theme) {
    document.documentElement.dataset.theme = theme;
    document.getElementById("css-dark").disabled = theme !== "dark";
    document.getElementById("css-light").disabled = theme === "dark";
    pics.forEach(p => { const src = theme === "dark" ? p.dark : p.light; if (src) p.img.src = src; });
  }
  let theme = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  apply(theme);
  document.getElementById("toggle").onclick = () => apply(theme = theme === "dark" ? "light" : "dark");
</script>
</body>
</html>
"""
_md = (_HERE / "README.md").read_text(encoding="utf-8")
(_HERE / "preview.html").write_text(
    _PREVIEW.replace("__TITLE__", _HERE.name).replace("__MD__", _json.dumps(_md).replace("</", "<\\/")),
    encoding="utf-8")
print("preview.html written")
