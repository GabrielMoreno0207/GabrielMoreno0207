# Como publicar e manter

O perfil é composto por **três SVGs animados** gerados por script e commitados no
repositório. Nada de serviço externo, nada de token: o GitHub renderiza animação
CSS dentro de SVG, então a animação viaja junto com o arquivo.

| arquivo | o que é | atualiza |
|---|---|---|
| `contrib-heatmap.svg` | calendário de contribuições, quadrados entrando em diagonal | sozinho, todo dia |
| `stats.svg` | cartão `neofetch` com seus dados + números reais | sozinho, todo dia |
| `ascii-art.svg` | o desenho do coder em ASCII, digitado linha a linha | só quando você rodar |

---

## 1. Publicar

O repositório precisa ter **exatamente o seu nome de usuário** — é isso que faz o
GitHub mostrar o README no seu perfil.

```bash
cd "C:/Users/Gabriel Ti/github-profile"
git init
git add .
git commit -m "feat: perfil animado"
git branch -M main
git remote add origin https://github.com/GabrielMoreno0207/GabrielMoreno0207.git
git push -u origin main
```

Se o repositório `GabrielMoreno0207/GabrielMoreno0207` ainda não existe, crie em
<https://github.com/new> com esse nome, **público**, e sem README inicial.

> Você já tem um perfil publicado nesse repositório. O push acima substitui o
> README atual. Se quiser guardar o antigo, renomeie-o para `README-antigo.md`
> antes de commitar.

## 2. Deixar atualizando sozinho

O workflow `.github/workflows/update-profile-art.yml` roda todo dia às ~03:17 de
Brasília, refaz o heatmap e o cartão de stats e commita de volta. Depois do
primeiro push:

1. Vá em **Actions** no repositório e habilite os workflows (o GitHub pede
   confirmação na primeira vez).
2. Em **Settings → Actions → General → Workflow permissions**, marque
   **Read and write permissions** — sem isso o bot não consegue commitar.
3. Rode uma vez na mão em **Actions → Update profile art → Run workflow** pra
   conferir.

## 3. Mudar o conteúdo

Quase tudo está em **`scripts/config.py`**: nome, idade, cidade, stack, cores do
tema, e os rótulos dos cartões (hoje em inglês, pra bater com o seu perfil atual —
troque o dicionário `LABELS` se quiser em português).

Depois de editar:

```bash
python scripts/build_all.py      # refaz heatmap + cartão de stats
python scripts/make_ascii_svg.py # refaz o banner ASCII
```

### Ver antes de commitar

```bash
python -m http.server 8787
# abre http://127.0.0.1:8787/preview.html
```

> ⚠️ O Chrome dessa máquina está com a animação de imagens desligada, então SVG
> dentro de `<img>` aparece congelado. O `preview.html` contorna isso injetando os
> SVGs direto na página. No GitHub a animação roda normal.

## 4. Trocar o desenho do cartao da esquerda

A arte usada esta em `art/`:

| arquivo | o que e |
|---|---|
| `art/coder-original.avif` | a ilustracao como voce baixou |
| `art/coder.png` | a mesma, limpa: sem fundo, sem o `>_` e sem os `1010 / 1001` |

### Limpar outra ilustracao

`scripts/clean_art.py` separa a imagem em pedacos conectados, mantem o maior e
joga o resto fora. E assim que o `>_` e os binarios sairam: cada um era um pedaco
solto. Buracos internos (lente de oculos, borda do laptop) sao preservados.

```bash
# ver os pedacos antes de decidir
python scripts/clean_art.py art/coder-original.avif --inspect

# limpar e cortar a sobra de fundo
python scripts/clean_art.py caminho/da/arte.avif --bg white --crop --out art/coder.png
```

Opcoes: `--keep 2` mantem os dois maiores pedacos (se o desenho for separado),
`--min-area 500` mantem tambem tudo acima dessa area, `--level` ajusta o que conta
como fundo (padrao 720 de 765, ou seja, quase branco).

### Gerar o ASCII

```bash
python scripts/make_ascii_svg.py --image art/coder.png --black-point 0 --gamma 0.55
```

`--gamma` abaixo de 1 engrossa (0.55 e o que esta valendo), acima de 1 afina.
`--black-point` so e necessario se o fundo nao for branco puro.
O texto embaixo (`ANALISTA E | DESENVOLVEDOR`) vem de `ASCII_CAPTION` no `config.py`.

### Voltar pro banner so de texto

```bash
python scripts/make_ascii_svg.py          # usa ASCII_TITLE + ASCII_CAPTION
```

### Usar uma foto de verdade

```bash
# tira o fundo, enquadra no rosto e joga sobre preto (fica melhor no cartao escuro)
python scripts/prep_photo.py "caminho/da/foto.jpg" --bg black --zoom 0.85

python scripts/make_ascii_svg.py --image source-prepped.png --on-dark        --black-point 0.22 --gamma 0.65
```

## 5. Detalhe que vale conferir

Seu heatmap mostra **196 contribuições**, que é pouco pra quem commita todo dia —
provavelmente porque seus repositórios de trabalho são privados. Em
<https://github.com/settings/profile> marque
**“Include private contributions on my profile”**: o gráfico passa a contar os
commits privados (sem revelar nada dos repositórios) e o cartão fica muito mais cheio.

## Dependências

O fluxo diário (`fetch_contributions`, `render_heatmap_svg`, `make_stats_card`)
usa **só a biblioteca padrão do Python** — por isso o workflow não instala nada.

`make_ascii_svg.py` precisa de `pillow` e `numpy`; `clean_art.py` precisa também de
`opencv-python-headless`; `prep_photo.py` precisa ainda de `rembg` pro recorte de
fundo de foto (todos já instalados nesta máquina). Lista em
`scripts/requirements.txt`.
