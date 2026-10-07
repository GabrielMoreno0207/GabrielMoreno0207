# -*- coding: utf-8 -*-
"""Roda a cadeia inteira: dados -> heatmap -> cartao. (O retrato ASCII e separado.)"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for step in ("fetch_contributions", "render_heatmap_svg", "make_stats_card"):
    print("-> %s" % step)
    sys.argv = [step]
    runpy.run_path(str(HERE / (step + ".py")), run_name="__main__")
