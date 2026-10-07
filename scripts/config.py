# -*- coding: utf-8 -*-
"""
Unico arquivo que voce precisa editar.
Tudo que aparece nos SVGs sai daqui.
"""

# ---------------------------------------------------------------- identidade
GITHUB_USER = "GabrielMoreno0207"
SHELL_USER  = "gabriel"          # o prompt: gabriel@github ~ $
NAME        = "Gabriel Moreno"
HEADLINE    = "Data Communication Analyst & Developer"

# Banner em ASCII do cartao da esquerda ("|" quebra linha)
ASCII_TITLE   = "GABRIEL|MORENO"
ASCII_CAPTION = "ANALISTA E|DESENVOLVEDOR"

# ---------------------------------------------------------- cartao neofetch
# (chave, valor, cor). Cabem 8 linhas.
INFO_ROWS = [
    ("Age",    "25",                                   "accent"),
    ("From",   "Osvaldo Cruz - SP, Brazil",            "cyan"),
    ("Role",   "Data Communication Analyst & Dev",     "cyan"),
    ("Study",  "Postgrad in Data Science & Big Data",  "purple"),
    ("Data",   "Python - R - SQL - Power BI - ML",     "yellow"),
    ("Web",    "React - Tailwind - Node.js",           "yellow"),
    ("Next",   "Data Scientist - Full Stack",          "purple"),
    ("AFK",    "gaming",                               "dim"),
]

# ------------------------------------------------------------------- textos
# troque aqui se quiser os cartoes em portugues
LABELS = {
    "contributions": "contributions",
    "current":       "current streak",
    "longest":       "longest streak",
    "active":        "active days",
    "best":          "best day",
    "avg":           "avg / active day",
    "less":          "less",
    "more":          "more",
    "year":          "contributions (1y)",
    "streak_days":   "current streak (days)",
    "commit_days":   "days with commits",
    "updated":       "updated %s - built by GitHub Actions",
}

# --------------------------------------------------------------- aparencia
# paleta de terminal (funciona no tema claro e no escuro do GitHub)
THEME = {
    "bg":      "#0d1117",
    "panel":   "#010409",
    "border":  "#30363d",
    "text":    "#c9d1d9",
    "dim":     "#8b949e",
    "accent":  "#39d353",
    "cyan":    "#56d4dd",
    "purple":  "#bc8cff",
    "yellow":  "#e3b341",
    "red":     "#ff7b72",
    "ascii":   "#b9c3cf",
}

# verde do heatmap: nada -> muito
HEAT = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace"
