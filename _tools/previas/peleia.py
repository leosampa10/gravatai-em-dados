"""Gera as prévias de link da Peleia: pl/<a>-<b>/index.html + card.jpg (1200x630).

Uma página por par (vereadores do mandato atual e gestões da Prefeitura), em ordem alfabética
(ou numérica, nas gestões). O botão "Copiar link desta Peleia" aponta para essas páginas; se a
ordem escolhida no site for a inversa, o link leva ?i=1 e a página redireciona invertendo os lados.
A imagem é desenhada pelo próprio site (window.gvPeleiaImg), então fica igual à do story.

Uso, na raiz do repositório: python3 _tools/previas/peleia.py
"""
import base64, html, itertools, pathlib, shutil
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SITE = 'https://gravataiemdados.com.br'
E = html.escape


def pagina(k, a, b, meta):
    t = E(meta['t'] + ' · Gravataí em dados')
    d = E(meta['d'])
    alvo = f"/?peleia={k}"
    inv = f"/?peleia={b}-{a}" if not k.startswith('g') else f"/?peleia=g{b}-{a}"
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>{t}</title>
<meta name="description" content="{d}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Gravataí em dados">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{SITE}/pl/{k}/">
<meta property="og:image" content="{SITE}/pl/{k}/card.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE}{alvo}">
<script>location.replace(/[?&]i=1/.test(location.search)?'{inv}':'{alvo}')</script>
<noscript><meta http-equiv="refresh" content="0; url={alvo}"></noscript>
</head><body><p><a href="{alvo}">Abrir a Peleia: {E(meta['A'])} × {E(meta['B'])}</a></p></body></html>'''


def main():
    dest = RAIZ / 'pl'
    if dest.exists():
        shutil.rmtree(dest)
    n = 0
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={'width': 1280, 'height': 900})
        pg.add_init_script("try{localStorage.setItem('gv-wl','skip');localStorage.setItem('gv-rv','off')}catch(e){}")
        pg.goto((RAIZ / 'index.html').as_uri())
        pg.wait_for_timeout(2500)
        pares = pg.evaluate('gvPeleiaPairs()')
        jobs = [('v', a, b, f'{a}-{b}') for a, b in itertools.combinations(sorted(pares['v']), 2)]
        jobs += [('g', a, b, f'g{a}-{b}') for a, b in itertools.combinations(range(pares['g']), 2)]
        for m, a, b, k in jobs:
            r = pg.evaluate('async([m,a,b])=>({img:await gvPeleiaImg(m,a,b,"og",.8),meta:gvPeleiaMeta(m,a,b)})', [m, a, b])
            o = dest / k
            o.mkdir(parents=True, exist_ok=True)
            (o / 'card.jpg').write_bytes(base64.b64decode(r['img'].split(',', 1)[1]))
            (o / 'index.html').write_text(pagina(k, a, b, r['meta']), encoding='utf-8')
            n += 1
        br.close()
    print(n, 'prévias da Peleia')


if __name__ == '__main__':
    main()
