"""Generates the profile header SVG (light + dark).

Matches 04-architecture (card, mono labels, pulse dot) and 05-metro-map
(line colours, interchanges, the train) so the three read as one set.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 880, 290

PAL = {
    "dark": dict(bg="#161B22", edge="#30363D", ink="#E6EDF3", muted="#8B949E", accent="#8B6CFF",
                 ok="#3FB950", station="#161B22", dot="#30363D",
                 banking="#8B6CFF", work="#2BB3A3", uni="#F0883E", oss="#F85149", planned="#6E7681"),
    "light": dict(bg="#FFFFFF", edge="#D0D7DE", ink="#1F2328", muted="#59636E", accent="#512BD4",
                  ok="#1A7F37", station="#FFFFFF", dot="#D0D7DE",
                  banking="#512BD4", work="#0E8A7E", uni="#E36209", oss="#CF222E", planned="#8C959F"),
}
MONO = "ui-monospace, 'SFMono-Regular', 'Cascadia Mono', Consolas, 'Liberation Mono', Menlo, monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

LINE_Y = 214
# (name, x, kind) where kind is "stop", "hub" or "planned"
STATIONS = [
    ("Rust", 64, "stop"),
    ("C#", 214, "hub"),
    ("ASP.NET Core", 384, "hub"),
    ("EF Core", 554, "hub"),
    ("SQL Server", 704, "hub"),
    ("Microservices", 816, "planned"),
]
# segment colours between consecutive solid stations
SEGMENTS = ["oss", "banking", "work", "uni"]


def t(x, y, s, cls="sans", size=13, fill="#000", anchor="start", weight=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{w} {extra}>{escape(s)}</text>')


def build(p):
    css = f"""
  .mono {{ font-family: {MONO}; }}
  .sans {{ font-family: {SANS}; }}
  .seg {{ fill: none; stroke-width: 9; stroke-linecap: round; }}
  .draw {{ animation: draw .9s ease-out backwards; }}
  @keyframes draw {{ from {{ stroke-dashoffset: var(--len); }} to {{ stroke-dashoffset: 0; }} }}
  .rise {{ animation: rise .7s ease-out backwards; }}
  @keyframes rise {{ from {{ transform: translateY(8px); }} to {{ transform: none; }} }}
  .pulse {{ animation: pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 50% {{ opacity: .35; }} }}
  .train {{ offset-path: path('M{STATIONS[0][1]} {LINE_Y} H{STATIONS[-2][1]}'); animation: ride 7s linear infinite; }}
  @keyframes ride {{ from {{ offset-distance: 0%; }} to {{ offset-distance: 100%; }} }}
  @media (prefers-reduced-motion: reduce) {{ .draw, .rise, .pulse {{ animation: none; }} .train {{ display: none; }} }}
"""
    b = []
    # card
    b.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{p["bg"]}" stroke="{p["edge"]}"/>')

    # dot grid, fading out towards the name
    b.append('<defs>'
             f'<pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse">'
             f'<circle cx="2" cy="2" r="1.3" fill="{p["dot"]}"/></pattern>'
             '<linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">'
             '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>'
             '<mask id="m"><rect x="470" y="1" width="409" height="160" fill="url(#fade)"/></mask>'
             '</defs>')
    b.append(f'<rect x="470" y="1" width="409" height="160" fill="url(#grid)" mask="url(#m)"/>')

    # text block
    b.append('<g class="rise">')
    b.append(t(40, 58, "BACKEND DEVELOPER · BANKING & FINTECH", "mono", 11, p["accent"], weight="700",
               extra='letter-spacing="1.8"'))
    b.append(t(38, 112, "Mohamed Emad", "sans", 50, p["ink"], weight="700", extra='letter-spacing="-0.5"'))
    b.append(t(40, 146, "Core banking APIs, integrations and credit scoring, built with C# and ASP.NET Core.",
               "sans", 16, p["muted"]))
    b.append('</g>')

    # status, top right
    b.append(f'<rect x="{W-154}" y="34" width="114" height="30" rx="15" fill="{p["bg"]}" stroke="{p["edge"]}"/>')
    b.append(f'<circle class="pulse" cx="{W-134}" cy="49" r="4.5" fill="{p["ok"]}"/>')
    b.append(t(W-120, 53.5, "200 OK", "mono", 12, p["ink"], weight="700"))
    b.append(t(W-40, 86, "on GitHub since Feb 2023", "mono", 11, p["muted"], anchor="end"))

    # the line: solid segments, then the planned extension
    solid = [s for s in STATIONS if s[2] != "planned"]
    for i, (key, (_, x1, _k1), (_, x2, _k2)) in enumerate(zip(SEGMENTS, solid, solid[1:])):
        L = x2 - x1
        b.append(f'<path class="seg draw" d="M{x1} {LINE_Y} H{x2}" stroke="{p[key]}" '
                 f'style="stroke-dasharray:{L};--len:{L};animation-delay:{0.3 + i*0.22:.2f}s"/>')
    px1, px2 = solid[-1][1], STATIONS[-1][1]
    b.append(f'<path d="M{px1} {LINE_Y} H{px2}" fill="none" stroke="{p["planned"]}" stroke-width="5" '
             f'stroke-dasharray="2 9" stroke-linecap="round"/>')

    # train
    b.append(f'<circle class="train" r="4" fill="{p["bg"]}" stroke="{p["ink"]}" stroke-width="1.5"/>')

    # stations + labels
    for name, x, kind in STATIONS:
        if kind == "hub":
            b.append(f'<circle cx="{x}" cy="{LINE_Y}" r="12" fill="{p["station"]}" stroke="{p["ink"]}" stroke-width="4"/>')
            b.append(t(x, LINE_Y + 38, name, "sans", 14, p["ink"], "middle", "700"))
        elif kind == "stop":
            b.append(f'<circle cx="{x}" cy="{LINE_Y}" r="7.5" fill="{p["station"]}" stroke="{p["ink"]}" stroke-width="3"/>')
            b.append(t(x, LINE_Y + 38, name, "sans", 13, p["ink"], "middle", "600"))
        else:
            b.append(f'<circle cx="{x}" cy="{LINE_Y}" r="8" fill="{p["station"]}" stroke="{p["planned"]}" '
                     f'stroke-width="3" stroke-dasharray="3 3"/>')
            b.append(t(x, LINE_Y + 38, name, "sans", 13, p["muted"], "middle", "600", 'font-style="italic"'))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<title>Mohamed Emad, Backend Developer, Banking and Fintech</title>'
            f'<style>{css}</style>{"".join(b)}</svg>')


for mode, p in PAL.items():
    (OUT / f"header-{mode}.svg").write_text(build(p), encoding="utf-8")
print("ok")
