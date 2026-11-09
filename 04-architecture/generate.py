"""Generates the architecture-diagram SVG (light + dark) for README-arch.md."""
import sys
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 880, 840

PAL = {
    "dark": dict(box="#161B22", head="#1C2128", border="#30363D", text="#E6EDF3", muted="#8B949E",
                 accent="#8B6CFF", line="#545D68", bus="#1E1838", ok="#3FB950", boundary="#3D444D"),
    "light": dict(box="#FFFFFF", head="#F6F8FA", border="#D0D7DE", text="#1F2328", muted="#59636E",
                  accent="#512BD4", line="#8C959F", bus="#F1ECFF", ok="#1A7F37", boundary="#B6BEC8"),
}
MONO = "ui-monospace, 'SFMono-Regular', 'Cascadia Mono', Consolas, 'Liberation Mono', Menlo, monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def style(p):
    return f"""
  .mono {{ font-family: {MONO}; }}
  .sans {{ font-family: {SANS}; }}
  .flow {{ stroke-dasharray: 5 5; animation: flow 1.2s linear infinite; }}
  @keyframes flow {{ to {{ stroke-dashoffset: -20; }} }}
  .msg {{ animation: ride 5.5s linear infinite; }}
  .msg.rev {{ animation-name: ride-rev; }}
  @keyframes ride {{ from {{ transform: translateX(0); }} to {{ transform: translateX(800px); }} }}
  @keyframes ride-rev {{ from {{ transform: translateX(800px); }} to {{ transform: translateX(0); }} }}
  .pulse {{ animation: pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 50% {{ opacity: .35; }} }}
  @media (prefers-reduced-motion: reduce) {{ .flow, .msg, .pulse {{ animation: none; }} }}
"""


def t(x, y, s, cls="sans", size=13, fill="#000", anchor="start", weight=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{w} {extra}>{escape(s)}</text>')


def wrap(s, n):
    words, lines, cur = s.split(" "), [], ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > n:
            lines.append(cur)
            cur = w_
        else:
            cur = f"{cur} {w_}".strip()
    return lines + [cur]


def box(p, x, y, w, h, stroke=None, sw=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{p["box"]}" stroke="{stroke or p["border"]}" stroke-width="{sw}"/>'


def service(p, x, y, w, h, name, lines):
    """lines: list of (kind, text) with kind in {'group','item','kv','mono'}."""
    out = [box(p, x, y, w, h)]
    out.append(f'<path d="M{x} {y+10} a10 10 0 0 1 10 -10 h{w-20} a10 10 0 0 1 10 10 v26 h-{w} z" fill="{p["head"]}"/>')
    out.append(f'<line x1="{x}" y1="{y+36}" x2="{x+w}" y2="{y+36}" stroke="{p["border"]}"/>')
    out.append(t(x + 14, y + 23, name, "mono", 13, p["text"], weight="700"))
    out.append(f'<circle class="pulse" cx="{x+w-18}" cy="{y+18}" r="4.5" fill="{p["ok"]}"/>')
    cy = y + 60
    for kind, text in lines:
        if kind == "group":
            cy += 6
            out.append(t(x + 14, cy, text.upper(), "mono", 10, p["accent"], weight="700", extra='letter-spacing="1.4"'))
            cy += 19
        elif kind == "item":
            for ln in wrap(text, 37):
                out.append(t(x + 14, cy, ln, "sans", 12.5, p["text"]))
                cy += 18
        elif kind == "mono":
            out.append(t(x + 14, cy, text, "mono", 11.5, p["text"]))
            cy += 18
    return "".join(out)


def cylinder(p, cx, y, label):
    rx, ry, h = 62, 11, 52
    return (f'<path d="M{cx-rx} {y} v{h} a{rx} {ry} 0 0 0 {2*rx} 0 v-{h}" fill="{p["box"]}" stroke="{p["border"]}"/>'
            f'<ellipse cx="{cx}" cy="{y}" rx="{rx}" ry="{ry}" fill="{p["head"]}" stroke="{p["border"]}"/>'
            + t(cx, y + 38, label, "sans", 13, p["text"], "middle", "600"))


def build(p):
    b = []
    b.append(f'<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             f'<path d="M0 0 L10 5 L0 10 z" fill="{p["line"]}"/></marker></defs>')

    # ── row 1: client → gateway ← identity
    b.append(box(p, 20, 30, 200, 92))
    b.append(t(120, 62, "WEB CLIENT", "mono", 10, p["muted"], "middle", "700", 'letter-spacing="1.4"'))
    b.append(t(120, 88, "React · Blazor", "sans", 14, p["text"], "middle", "600"))
    b.append(t(120, 108, "TypeScript · Bootstrap", "sans", 11.5, p["muted"], "middle"))

    gx, gw = 270, 340
    b.append(box(p, gx, 14, gw, 124, p["accent"], 2))
    b.append(t(gx + gw / 2, 42, "API GATEWAY", "mono", 10, p["accent"], "middle", "700", 'letter-spacing="2"'))
    b.append(t(gx + gw / 2, 76, "Backend Developer", "sans", 26, p["text"], "middle", "700"))
    b.append(t(gx + gw / 2, 102, "Banking & Fintech", "sans", 13, p["muted"], "middle"))
    b.append(t(gx + gw / 2, 124, "ASP.NET Core · C#", "mono", 11.5, p["text"], "middle"))

    b.append(box(p, 660, 30, 200, 92))
    b.append(t(760, 62, "IDENTITY", "mono", 10, p["muted"], "middle", "700", 'letter-spacing="1.4"'))
    b.append(t(760, 88, "Keycloak", "sans", 14, p["text"], "middle", "600"))
    b.append(t(760, 108, "OpenID Connect", "sans", 11.5, p["muted"], "middle"))

    b.append(f'<line class="flow" x1="222" y1="76" x2="266" y2="76" stroke="{p["line"]}" stroke-width="1.5" marker-end="url(#arr)"/>')
    b.append(f'<line class="flow" x1="658" y1="76" x2="614" y2="76" stroke="{p["line"]}" stroke-width="1.5" marker-end="url(#arr)"/>')
    b.append(t(244, 68, "HTTPS", "mono", 9, p["muted"], "middle"))
    b.append(t(636, 68, "OIDC", "mono", 9, p["muted"], "middle"))

    # ── docker boundary
    b.append(f'<rect x="8" y="166" width="{W-16}" height="{H-178}" rx="14" fill="none" stroke="{p["boundary"]}" stroke-dasharray="6 5"/>')
    b.append(t(24, 186, "docker compose", "mono", 11, p["muted"]))

    # ── gateway → services
    sw, sy, sh = 262, 222, 380
    xs = [24, 24 + sw + 17, 24 + 2 * (sw + 17)]
    mid = gx + gw / 2
    b.append(f'<line x1="{mid}" y1="140" x2="{mid}" y2="200" stroke="{p["line"]}" stroke-width="1.5"/>')
    b.append(f'<line x1="{xs[0]+sw/2}" y1="200" x2="{xs[2]+sw/2}" y2="200" stroke="{p["line"]}" stroke-width="1.5"/>')
    for x in xs:
        b.append(f'<line class="flow" x1="{x+sw/2}" y1="200" x2="{x+sw/2}" y2="{sy-3}" stroke="{p["line"]}" stroke-width="1.5" marker-end="url(#arr)"/>')

    b.append(service(p, xs[0], sy, sw, sh, "Projects.Service", [
        ("group", "Banking"), ("item", "Core Banking APIs"), ("item", "Financial Integration Services"),
        ("group", "Work"), ("item", "iScore & Value Integration"), ("item", "Medical Insurance System"),
        ("item", "Numerical Methods App"),
        ("group", "Open source"), ("item", "hilal: notch for Windows (Rust)"),
        ("group", "University"), ("item", "Smart Smile Prediction"), ("item", "Library Management System"),
        ("item", "Student Result System"),
    ]))
    b.append(service(p, xs[1], sy, sw, sh, "Stack.Service", [
        ("group", "Backend"), ("item", "C#, .NET, ASP.NET Core, EF Core, AutoMapper"),
        ("group", "Data"), ("item", "SQL Server, MySQL, Elasticsearch"),
        ("group", "Messaging"), ("item", "RabbitMQ, MassTransit"),
        ("group", "Frontend"), ("item", "React, TypeScript, JavaScript, Blazor, HTML, CSS, Bootstrap"),
        ("group", "Other"), ("item", "Python, Django, Rust, Flutter, Dart"),
        ("group", "Tools"), ("item", "Docker, Git, Postman, Visual Studio, VS Code"),
    ]))
    b.append(service(p, xs[2], sy, sw, sh, "Profile.Service", [
        ("group", "Role"), ("item", "Backend Developer"),
        ("group", "Sector"), ("item", "Banking & Fintech"),
        ("group", "On GitHub since"), ("item", "February 2023"),
        ("group", "Interests"), ("item", "Microservices, Clean Architecture"),
        ("group", "Contact"), ("mono", "in/mohamed-emad-eldin-fathey"),
        ("mono", "ig/mohamedemad6648"), ("mono", "fb/mohamed.emad.972846"),
    ]))

    # ── bus
    by = sy + sh + 40
    for x in xs:
        b.append(f'<line x1="{x+sw/2}" y1="{sy+sh}" x2="{x+sw/2}" y2="{by}" stroke="{p["line"]}" stroke-width="1.5"/>')
        b.append(f'<circle cx="{x+sw/2}" cy="{by}" r="3.5" fill="{p["line"]}"/>')
    b.append(f'<rect x="24" y="{by}" width="{W-48}" height="40" rx="20" fill="{p["bus"]}" stroke="{p["accent"]}" stroke-opacity=".6"/>')
    b.append(t(W / 2, by + 25, "Message bus · RabbitMQ + MassTransit", "mono", 12, p["accent"], "middle", "700"))
    for i, (cls, delay) in enumerate([("msg", 0), ("msg rev", 1.8), ("msg", 3.6)]):
        b.append(f'<circle class="{cls}" style="animation-delay:-{delay}s" cx="40" cy="{by+20}" r="5" fill="{p["accent"]}"/>')

    # ── data stores
    dy = by + 86
    stores = [(W / 2 - 220, "SQL Server"), (W / 2, "MySQL"), (W / 2 + 220, "Elasticsearch")]
    for cx, label in stores:
        b.append(f'<line class="flow" x1="{cx}" y1="{by+42}" x2="{cx}" y2="{dy-14}" stroke="{p["line"]}" stroke-width="1.5" marker-end="url(#arr)"/>')
        b.append(cylinder(p, cx, dy, label))
    return "".join(b)


for mode, p in PAL.items():
    (OUT / f"architecture-{mode}.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
        f'<style>{style(p)}</style>{build(p)}</svg>', encoding="utf-8")
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
