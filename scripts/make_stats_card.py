# -*- coding: utf-8 -*-
"""
Gera stats.svg: cartao estilo `neofetch` com a sua identidade (do config.py)
e os numeros reais das contribuicoes (de data/contributions.json).
As linhas entram uma a uma e congelam.

   python scripts/make_stats_card.py        # STATIC=1 desliga a animacao
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import HEADLINE, INFO_ROWS, LABELS, MONO, NAME, SHELL_USER, THEME

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "stats.svg"

W, H = 840, 880
STATIC = os.environ.get("STATIC") == "1"
_n = [0]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def ln():
    """delay da proxima linha a entrar (a classe `ln` vai no elemento)."""
    _n[0] += 1
    if STATIC:
        return ""
    return ' style="animation-delay:%.2fs"' % (0.25 + _n[0] * 0.085)


def render(doc):
    st = doc["stats"]
    gen = dt.datetime.fromisoformat(doc["generated_at"]).strftime("%d/%m/%Y")
    best = dt.date.fromisoformat(st["best_day"]["date"]).strftime("%d/%m")

    o = []
    a = o.append
    a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
      'role="img" aria-label="Cartao de perfil de %s">' % (W, H, W, H, esc(NAME)))

    anim = "" if STATIC else """
    @keyframes rise{from{opacity:0;transform:translateX(-14px)} to{opacity:1;transform:translateX(0)}}
    @keyframes blink{0%,49%{opacity:1} 50%,100%{opacity:0}}
    .ln{opacity:0;animation:rise .5s ease-out forwards}
    .car{animation:blink 1s step-end infinite}
    """
    a('<style>%s .mono{font-family:%s}'
      '.ttl{font-size:24px;fill:%s}'
      '.name{font-size:46px;font-weight:700;fill:%s}'
      '.head{font-size:22px;fill:%s}'
      '.k{font-size:25px;font-weight:700}'
      '.v{font-size:25px;fill:%s}'
      '.num{font-size:44px;font-weight:700;fill:%s}'
      '.cap{font-size:19px;fill:%s}'
      '.foot{font-size:18px;fill:%s}'
      '</style>'
      % (anim, MONO, THEME["dim"], THEME["accent"], THEME["dim"],
         THEME["text"], THEME["text"], THEME["dim"], THEME["dim"]))

    # ---- janela
    a('<rect x="2" y="2" width="%d" height="%d" rx="18" fill="%s" stroke="%s" stroke-width="2"/>'
      % (W - 4, H - 4, THEME["bg"], THEME["border"]))
    a('<path d="M2 20a18 18 0 0 1 18-18h%d a18 18 0 0 1 18 18v36H2z" fill="%s"/>'
      % (W - 40, THEME["panel"]))
    a('<line x1="2" y1="56" x2="%d" y2="56" stroke="%s" stroke-width="2"/>' % (W - 2, THEME["border"]))
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        a('<circle cx="%d" cy="29" r="9" fill="%s"/>' % (34 + i * 32, c))
    a('<text class="mono ttl" x="152" y="38">%s@github: ~ $ neofetch</text>' % esc(SHELL_USER))

    # ---- identidade
    a('<text class="mono name ln" x="44" y="126"%s>%s</text>' % (ln(), esc(NAME)))
    a('<text class="mono head ln" x="44" y="164"%s>%s</text>' % (ln(), esc(HEADLINE)))
    a('<text class="mono head ln" x="44" y="200"%s>%s</text>'
      % (ln(), esc("-" * 46)))

    # ---- linhas chave/valor
    y = 244
    for key, val, color in INFO_ROWS[:8]:
        a('<g class="ln"%s>' % ln())
        a('<text class="mono k" x="44" y="%d" fill="%s">%s</text>'
          % (y, THEME.get(color, THEME["cyan"]), esc(key)))
        a('<text class="mono v" x="190" y="%d">%s</text>' % (y, esc(val)))
        a('</g>')
        y += 42

    # ---- divisor
    a('<line x1="44" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2" class="ln"%s/>'
      % (y + 6, W - 44, y + 6, THEME["border"], ln()))

    # ---- numeros ao vivo
    cards = [
        (str(st["total"]), LABELS["year"], THEME["accent"]),
        (str(st["current_streak"]), LABELS["streak_days"], THEME["cyan"]),
        (str(st["longest_streak"]), LABELS["longest"], THEME["purple"]),
        (str(st["active_days"]), LABELS["commit_days"], THEME["yellow"]),
        (str(st["best_day"]["count"]), "%s (%s)" % (LABELS["best"], best), THEME["red"]),
        (str(st["avg_per_active_day"]), LABELS["avg"], THEME["text"]),
    ]
    gy = y + 46
    for i, (v, cap, color) in enumerate(cards):
        cx = 44 + (i % 2) * 400
        cy = gy + (i // 2) * 86
        a('<g class="ln"%s>' % ln())
        a('<text class="mono num" x="%d" y="%d" fill="%s">%s</text>' % (cx, cy, color, esc(v)))
        a('<text class="mono cap" x="%d" y="%d">%s</text>' % (cx, cy + 26, esc(cap)))
        a('</g>')

    # ---- rodape
    foot = LABELS["updated"] % gen
    a('<text class="mono foot ln" x="44" y="%d"%s>%s</text>' % (H - 24, ln(), esc(foot)))
    if not STATIC:
        a('<rect class="car" x="%d" y="%d" width="11" height="20" fill="%s"/>'
          % (50 + int(len(foot) * 10.8), H - 40, THEME["accent"]))
    a('</svg>')
    return "\n".join(o)


def main():
    if not SRC.exists():
        raise SystemExit("Rode primeiro: python scripts/fetch_contributions.py")
    OUT.write_text(render(json.loads(SRC.read_text(encoding="utf-8"))), encoding="utf-8")
    print("ok  %s  (%.1f KB)" % (OUT.name, OUT.stat().st_size / 1024))


if __name__ == "__main__":
    main()
