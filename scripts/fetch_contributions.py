# -*- coding: utf-8 -*-
"""
Baixa o calendario de contribuicoes publico do GitHub (sem token, sem API key)
e salva data/contributions.json com os dias crus + estatisticas derivadas.

   python scripts/fetch_contributions.py [usuario]

Usa so a biblioteca padrao -> roda em qualquer lugar, inclusive no Action.
"""
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import GITHUB_USER

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
URL = "https://github.com/users/{}/contributions"

TD_RE = re.compile(r"<td\b[^>]*ContributionCalendar-day[^>]*>", re.I)
ATTR_RE = re.compile(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"')
TIP_RE = re.compile(r"<tool-tip\b[^>]*\bfor=\"([^\"]+)\"[^>]*>(.*?)</tool-tip>", re.I | re.S)
NUM_RE = re.compile(r"^\s*(No|[\d.,]+)\b", re.I)


def fetch_html(user: str) -> str:
    req = urllib.request.Request(
        URL.format(user),
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; profile-readme-art/1.0)",
            "Accept": "text/html, application/xhtml+xml",
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def parse_days(html: str):
    """-> lista de {'date','count','level'} ordenada por data."""
    tips = {}
    for cid, text in TIP_RE.findall(html):
        plain = re.sub(r"<[^>]+>", "", text).strip()
        m = NUM_RE.match(plain)
        if not m:
            continue
        raw = m.group(1)
        tips[cid] = 0 if raw.lower() == "no" else int(re.sub(r"[.,]", "", raw))

    days = {}
    for tag in TD_RE.findall(html):
        a = dict(ATTR_RE.findall(tag))
        date = a.get("data-date")
        if not date:
            continue
        if "data-count" in a:                      # markup antigo
            count = int(a["data-count"] or 0)
        else:                                      # markup atual: vem do tool-tip
            count = tips.get(a.get("id", ""), 0)
        days[date] = {
            "date": date,
            "count": count,
            "level": int(a.get("data-level") or 0),
        }
    return [days[k] for k in sorted(days)]


def streaks(days):
    """Streak atual (hoje valendo 0 nao quebra) e maior streak."""
    cur = longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    i = len(days) - 1
    if i >= 0 and days[i]["count"] == 0:           # dia ainda nao acabou
        i -= 1
    while i >= 0 and days[i]["count"] > 0:
        cur += 1
        i -= 1
    return cur, longest


def build(user: str) -> dict:
    days = parse_days(fetch_html(user))
    if not days:
        raise SystemExit("Nao achei nenhum dia no HTML. O usuario existe e o perfil e publico?")

    total = sum(d["count"] for d in days)
    active = [d for d in days if d["count"] > 0]
    best = max(days, key=lambda d: d["count"])
    cur, longest = streaks(days)

    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]

    return {
        "user": user,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "range": {"from": days[0]["date"], "to": days[-1]["date"]},
        "days": days,
        "stats": {
            "total": total,
            "active_days": len(active),
            "max_level": max(d["level"] for d in days),
            "best_day": {"date": best["date"], "count": best["count"]},
            "current_streak": cur,
            "longest_streak": longest,
            "avg_per_active_day": round(total / len(active), 1) if active else 0.0,
        },
        "months": months,
    }


def main():
    user = sys.argv[1] if len(sys.argv) > 1 else GITHUB_USER
    try:
        payload = build(user)
    except urllib.error.HTTPError as e:
        raise SystemExit("GitHub respondeu HTTP %s para o usuario %r" % (e.code, user))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    s = payload["stats"]
    print("ok  %s" % OUT.relative_to(ROOT))
    print("    %d dias | %d contribuicoes | streak %d (recorde %d) | melhor dia %s = %d"
          % (len(payload["days"]), s["total"], s["current_streak"],
             s["longest_streak"], s["best_day"]["date"], s["best_day"]["count"]))


if __name__ == "__main__":
    main()
