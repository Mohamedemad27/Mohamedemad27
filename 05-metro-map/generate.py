"""Generates the metro-map SVG (light + dark) for README-metro.md."""
import sys
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 880, 640

PAL = {
    "light": dict(bg="#FFFFFF", edge="#D0D7DE", ink="#1F2328", muted="#59636E", station="#FFFFFF",
                  banking="#512BD4", work="#0E8A7E", uni="#E36209", oss="#CF222E", planned="#8C959F"),
    "dark": dict(bg="#161B22", edge="#30363D", ink="#E6EDF3", muted="#8B949E", station="#161B22",
                 banking="#8B6CFF", work="#2BB3A3", uni="#F0883E", oss="#F85149", planned="#6E7681"),
}
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SFMono-Regular', 'Cascadia Mono', Consolas, 'Liberation Mono', Menlo, monospace"

# Stations: name -> (x, y)
S = {
    "Numerical Methods App": (110, 250),
    "C#": (270, 250),
    "ASP.NET Core": (450, 250),
    "iScore & Value Integration": (610, 250),
    "EF Core": (690, 330),
    "Medical Insurance System": (610, 410),
    "SQL Server": (450, 410),
    "Financial Integration Services": (770, 170),
    "Core Banking APIs": (450, 330),
    "Student Result System": (270, 110),
    "Library Management System": (270, 330),
    "Smart Smile Prediction": (650, 490),
    "hilal": (110, 540),
    "Rust": (290, 540),
    "Microservices": (450, 110),
    "Clean Architecture": (650, 110),
}
HUBS = {"C#", "ASP.NET Core", "EF Core", "SQL Server"}

# Lines: key -> (label, path points)
LINES = {
    "banking": ("Banking", [S["Financial Integration Services"], (530, 170), S["ASP.NET Core"],
                            S["Core Banking APIs"], S["SQL Server"]]),
    "work": ("Work", [S["Numerical Methods App"], S["C#"], S["ASP.NET Core"], S["iScore & Value Integration"],
                      S["EF Core"], S["Medical Insurance System"], S["SQL Server"]]),
    "uni": ("University", [S["Student Result System"], S["C#"], S["Library Management System"], (350, 410),
                           S["SQL Server"], (530, 490), S["Smart Smile Prediction"]]),
    "oss": ("Open source", [S["hilal"], S["Rust"]]),
}
PLANNED = [S["ASP.NET Core"], S["Microservices"], S["Clean Architecture"]]

# Label placement: name -> (dx, dy, anchor, lines)
LABELS = {
    "Numerical Methods App": (0, -22, "middle", ["Numerical Methods App"]),
    "C#": (-16, -16, "end", ["C#"]),
    "ASP.NET Core": (16, 26, "start", ["ASP.NET Core"]),
    "iScore & Value Integration": (0, -22, "middle", ["iScore & Value Integration"]),
    "EF Core": (18, 5, "start", ["EF Core"]),
    "Medical Insurance System": (0, 30, "middle", ["Medical Insurance System"]),
    "SQL Server": (-18, 30, "end", ["SQL Server"]),
    "Financial Integration Services": (0, -22, "middle", ["Financial Integration Services"]),
    "Core Banking APIs": (16, 5, "start", ["Core Banking APIs"]),
    "Student Result System": (-16, 5, "end", ["Student Result System"]),
    "Library Management System": (-16, 5, "end", ["Library Management System"]),
    "Smart Smile Prediction": (16, 5, "start", ["Smart Smile Prediction"]),
    "hilal": (0, -20, "middle", ["hilal"]),
    "Rust": (0, -20, "middle", ["Rust"]),
    "Microservices": (0, -20, "middle", ["Microservices"]),
    "Clean Architecture": (0, -20, "middle", ["Clean Architecture"]),
}


def t(x, y, s, size=13, fill="#000", anchor="start", weight=None, cls="sans", extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{w} {extra}>{escape(s)}</text>')


def d(points):
    return "M" + " L".join(f"{x} {y}" for x, y in points)


def length(points):
    return sum(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5 for (x1, y1), (x2, y2) in zip(points, points[1:]))


def build(p):
    css = [f"""
  .sans {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .line {{ fill: none; stroke-width: 9; stroke-linecap: round; stroke-linejoin: round; }}
  .draw {{ animation: draw 1.6s ease-out backwards; }}
  @keyframes draw {{ from {{ stroke-dashoffset: var(--len); }} to {{ stroke-dashoffset: 0; }} }}
  .train {{ animation: ride 9s linear infinite; }}
  @keyframes ride {{ from {{ offset-distance: 0%; }} to {{ offset-distance: 100%; }} }}
  @media (prefers-reduced-motion: reduce) {{ .draw, .train {{ animation: none; }} .train {{ display: none; }} }}
"""]
    b = [f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{p["bg"]}" stroke="{p["edge"]}"/>']

    # title
    b.append(t(28, 46, "Mohamed Emad", 24, p["ink"], weight="700"))
    b.append(t(28, 70, "Backend network map · Banking & Fintech", 13, p["muted"]))

    # planned extension
    b.append(f'<path d="{d(PLANNED)}" fill="none" stroke="{p["planned"]}" stroke-width="5" '
             f'stroke-dasharray="2 9" stroke-linecap="round"/>')

    # lines (drawn in, then a train rides each)
    for i, (key, (_, pts)) in enumerate(LINES.items()):
        L = length(pts)
        b.append(f'<path class="line draw" d="{d(pts)}" stroke="{p[key]}" '
                 f'style="stroke-dasharray:{L:.0f};--len:{L:.0f};animation-delay:{i*0.25:.2f}s"/>')
        if len(pts) > 2:
            css.append(f".tr-{key} {{ offset-path: path('{d(pts)}'); animation-delay: -{i*2.1:.1f}s; }}")
            b.append(f'<circle class="train tr-{key}" r="4" fill="{p["bg"]}" stroke="{p["ink"]}" stroke-width="1.5"/>')

    # stations
    for name, (x, y) in S.items():
        if name in ("Microservices", "Clean Architecture"):
            b.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{p["station"]}" stroke="{p["planned"]}" '
                     f'stroke-width="3" stroke-dasharray="3 3"/>')
        elif name in HUBS:
            b.append(f'<circle cx="{x}" cy="{y}" r="12" fill="{p["station"]}" stroke="{p["ink"]}" stroke-width="4"/>')
        else:
            b.append(f'<circle cx="{x}" cy="{y}" r="7.5" fill="{p["station"]}" stroke="{p["ink"]}" stroke-width="3"/>')

    for name, (dx, dy, anchor, lines) in LABELS.items():
        x, y = S[name]
        hub = name in HUBS
        planned = name in ("Microservices", "Clean Architecture")
        for k, ln in enumerate(lines):
            b.append(t(x + dx, y + dy + k * 16, ln, 14 if hub else 13,
                       p["muted"] if planned else p["ink"], anchor, "700" if hub else "600",
                       extra='font-style="italic"' if planned else ""))

    # legend
    lx, ly = 470, 560
    b.append(f'<line x1="{lx-14}" y1="{ly-24}" x2="{W-28}" y2="{ly-24}" stroke="{p["edge"]}"/>')
    items = [(LINES[k][0], p[k], False) for k in LINES] + [("Planned", p["planned"], True)]
    col_w = 130
    for i, (label, color, dashed) in enumerate(items):
        cx = lx + (i % 3) * col_w
        cy = ly + (i // 3) * 26
        if dashed:
            b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+26}" y2="{cy}" stroke="{color}" stroke-width="5" stroke-dasharray="2 7" stroke-linecap="round"/>')
        else:
            b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+26}" y2="{cy}" stroke="{color}" stroke-width="7" stroke-linecap="round"/>')
        b.append(t(cx + 36, cy + 4.5, label, 12.5, p["ink"]))
    i = len(items)
    cx, cy = lx + (i % 3) * col_w, ly + (i // 3) * 26
    b.append(f'<circle cx="{cx+13}" cy="{cy}" r="7" fill="{p["station"]}" stroke="{p["ink"]}" stroke-width="3.5"/>')
    b.append(t(cx + 36, cy + 4.5, "Interchange", 12.5, p["ink"]))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H+18}" viewBox="0 0 {W} {H+18}">'
            f'<style>{"".join(css)}</style>{"".join(b)}</svg>')


for mode, p in PAL.items():
    (OUT / f"metro-{mode}.svg").write_text(build(p), encoding="utf-8")
print("ok")


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
