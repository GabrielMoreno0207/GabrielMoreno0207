# -*- coding: utf-8 -*-
"""
Gera contrib-heatmap.svg: o calendario real de contribuicoes, com os quadrados
aparecendo em diagonal e congelando no fim. Zero dependencia externa.

   python scripts/fetch_contributions.py && python scripts/render_heatmap_svg.py

STATIC=1 gera sem animacao (bom pra conferir no navegador).
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import HEAT, LABELS, MONO, SHELL_USER, THEME

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

W = 860
PITCH = 14
CELL = 12
RADIUS = 2.5
TOP = 58            # onde comeca a grade
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
STATIC = os.environ.get("STATIC") == "1"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def sun_index(d):
    """0 = domingo (igual ao GitHub)."""
    return (d.weekday() + 1) % 7


def grid(days):
    """-> (celulas, n_semanas, rotulos_de_mes)"""
    first = dt.date.fromisoformat(days[0]["date"])
    origin = first - dt.timedelta(days=sun_index(first))

    cells, label_at = [], {}
    for day in days:
        d = dt.date.fromisoformat(day["date"])
        col = (d - origin).days // 7
        cells.append((col, sun_index(d), day, d))
        label_at.setdefault((d.year, d.month), col)

    weeks = max(c[0] for c in cells) + 1
    labels = [(col, MONTHS[m - 1]) for (_, m), col in sorted(label_at.items(), key=lambda x: x[1])
              if 0 <= col <= weeks - 3]
    return cells, weeks, labels


def css(title_w):
    if STATIC:
        return ".c{opacity:1}.ln{opacity:1}"
    return """
    @keyframes pop  {from{opacity:0;transform:scale(.25)} 60%%{transform:scale(1.14)} to{opacity:1;transform:scale(1)}}
    @keyframes rise {from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)}}
    @keyframes type {from{width:0} to{width:%(tw)dpx}}
    @keyframes blink{0%%,49%%{opacity:1} 50%%,100%%{opacity:0}}
    .c  {opacity:0;transform-box:fill-box;transform-origin:center;
         animation:pop .5s cubic-bezier(.2,.9,.3,1.3) forwards}
    .ln {opacity:0;animation:rise .6s ease-out forwards}
    .ttl{animation:type 1.1s steps(%(steps)d,end) forwards}
    .car{animation:blink 1s step-end infinite;animation-delay:1.1s}
    """ % {"tw": title_w, "steps": max(len(SHELL_USER) + 22, 8)}


def render(doc):
    days = doc["days"]
    st = doc["stats"]
    cells, weeks, labels = grid(days)

    grid_w = weeks * PITCH
    pad_l = max(44, (W - grid_w) // 2)
    H = TOP + 7 * PITCH + 62

    o = []
    a = o.append
    a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
      'viewBox="0 0 %d %d" role="img" '
      'aria-label="Calendario de contribuicoes de %s no GitHub">'
      % (W, H, W, H, esc(doc["user"])))

    title = "%s@github:~/contributions" % SHELL_USER
    title_w = int(len(title) * 7.3) + 4

    a('<style>' + css(title_w) + '''
    .mono{font-family:%s}
    .t  {font-size:13px;fill:%s}
    .lbl{font-size:9.5px;fill:%s}
    .big{font-size:15px;font-weight:700;fill:%s}
    .sml{font-size:11px;fill:%s}
    </style>''' % (MONO, THEME["text"], THEME["dim"], THEME["text"], THEME["dim"]))

    # ---- moldura de janela de terminal
    a('<rect x="1" y="1" width="%d" height="%d" rx="10" fill="%s" stroke="%s"/>'
      % (W - 2, H - 2, THEME["bg"], THEME["border"]))
    a('<path d="M1 11a10 10 0 0 1 10-10h%d a10 10 0 0 1 10 10v20H1z" fill="%s"/>'
      % (W - 22, THEME["panel"]))
    a('<line x1="1" y1="31" x2="%d" y2="31" stroke="%s"/>' % (W - 1, THEME["border"]))
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        a('<circle cx="%d" cy="16" r="5" fill="%s"/>' % (20 + i * 18, c))

    # ---- titulo "digitando"
    a('<clipPath id="tclip"><rect class="ttl" x="84" y="6" width="%d" height="20"/></clipPath>'
      % (title_w if STATIC else 0,))
    a('<g clip-path="url(#tclip)"><text class="mono t" x="84" y="21">%s</text></g>' % esc(title))
    a('<rect class="car" x="%d" y="9" width="7" height="13" fill="%s"/>'
      % (84 + title_w + 3, THEME["accent"]))

    # ---- rotulos de mes
    for col, name in labels:
        a('<text class="mono lbl" x="%d" y="%d">%s</text>'
          % (pad_l + col * PITCH, TOP - 8, name))

    # ---- rotulos de dia da semana
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        a('<text class="mono lbl" x="%d" y="%d" text-anchor="end">%s</text>'
          % (pad_l - 7, TOP + row * PITCH + 9, name))

    # ---- a grade
    for col, row, day, d in cells:
        delay = "" if STATIC else ' style="animation-delay:%.3fs"' % ((col + row * 1.6) * 0.0115)
        a('<rect class="c" x="%d" y="%d" width="%d" height="%d" rx="%s" fill="%s"%s/>'
          % (pad_l + col * PITCH, TOP + row * PITCH, CELL, CELL, RADIUS,
             HEAT[min(day["level"], len(HEAT) - 1)], delay))

    base = TOP + 7 * PITCH
    def line(idx):
        return "" if STATIC else ' style="animation-delay:%.2fs"' % (0.9 + idx * 0.12)

    # ---- numeros
    nums = [
        ("%d" % st["total"], LABELS["contributions"]),
        ("%d" % st["current_streak"], LABELS["current"]),
        ("%d" % st["longest_streak"], LABELS["longest"]),
        ("%d" % st["active_days"], LABELS["active"]),
    ]
    x = pad_l
    for i, (v, k) in enumerate(nums):
        a('<g class="ln"%s>' % line(i))
        a('<text class="mono big" x="%d" y="%d">%s</text>' % (x, base + 28, esc(v)))
        a('<text class="mono sml" x="%d" y="%d">%s</text>' % (x, base + 44, esc(k)))
        a('</g>')
        x += 142

    # ---- legenda
    lx = W - pad_l - 5 * 14 - 74
    a('<g class="ln"%s>' % line(4))
    a('<text class="mono sml" x="%d" y="%d">%s</text>' % (lx, base + 32, esc(LABELS["less"])))
    for i, c in enumerate(HEAT):
        a('<rect x="%d" y="%d" width="10" height="10" rx="2" fill="%s"/>'
          % (lx + 40 + i * 14, base + 23, c))
    a('<text class="mono sml" x="%d" y="%d">%s</text>' % (lx + 40 + 5 * 14 + 4, base + 32, esc(LABELS["more"])))
    a('</g>')

    a('</svg>')
    return "\n".join(o)


def main():
    if not SRC.exists():
        raise SystemExit("Rode primeiro: python scripts/fetch_contributions.py")
    doc = json.loads(SRC.read_text(encoding="utf-8"))
    OUT.write_text(render(doc), encoding="utf-8")
    print("ok  %s  (%.1f KB)" % (OUT.name, OUT.stat().st_size / 1024))


if __name__ == "__main__":
    main()
