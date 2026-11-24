"""Gera as prévias de link de cada vereador do mandato atual.

Para cada vereador (legislatura L2) cria:
  v/<id>/index.html  -> página com as tags Open Graph, que redireciona para /#v/<id>
  v/<id>/card.png    -> imagem 1200x630 usada na prévia (WhatsApp, Instagram, X...)

Uso: python3 _tools/previas/gerar.py   (na raiz do repositório)
"""
import json, html, os, pathlib
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SITE = 'https://gravataiemdados.com.br'

s = (RAIZ / 'index.html').read_text(encoding='utf-8')
i = s.find('const DATA=')
D = json.loads(s[i + 11:s.find('\n', i)].rstrip()[:-1])
FOT = D.get('fotos', {})
import re
_m = re.search(r'SAIU=\{([^}]*)\}', s)
SAIU = set(re.findall(r'(\w+):1', _m.group(1))) if _m else set()


def nf(n):
    return f'{int(n):,}'.replace(',', '.')


def dados(v):
    prod = v.get('prod') or {}
    g = lambda k: (prod.get(k) or {}).get('L2', 0) or 0
    pres = v.get('presL2') or [0, 0]
    bloco = 'Oposição' if 'Oposi' in (v.get('bloco') or '') else 'Base do governo'
    if v['id'] in SAIU:
        bloco = 'Anunciou saída da base'
    votos = v.get('v24')
    sub = f"{v['pat']} · {bloco}" + (f" · {nf(votos)} votos em 2024" if votos and str(votos).isdigit() else '')
    q = lambda n, a, b: a if n == 1 else b
    k = [(g('pl'), q(g('pl'), 'projeto de lei', 'projetos de lei')), (g('apr'), q(g('apr'), 'virou lei', 'viraram lei')),
         (g('pi'), q(g('pi'), 'pedido de informação', 'pedidos de informação')),
         (pres[1], q(pres[1], 'falta', 'faltas') + (f' em {pres[0]} votações' if pres[0] else ''))]
    return sub, k


def card(v):
    sub, k = dados(v)
    partes = v['nome'].split(' ', 1)
    nome = html.escape(partes[0]) + ('<br><i>' + html.escape(partes[1]) + '</i>' if len(partes) > 1 else '')
    foto = FOT.get(v['id'], '')
    img = f'<img src="{foto}" alt="">' if foto else ''
    kp = ''.join(f'<div class="k"><b>{a}</b><span>{html.escape(t)}</span></div>' for a, t in k)
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,500;0,600;0,800;1,700&display=swap">
<style>
body{{margin:0}}
.c{{width:1200px;height:630px;box-sizing:border-box;background:#f8f8f6;color:#41443a;font-family:Poppins,sans-serif;padding:52px 64px;display:flex;flex-direction:column;justify-content:space-between}}
.t{{display:flex;justify-content:space-between;align-items:center}}
.br{{font:800 22px Poppins;letter-spacing:.14em;text-transform:uppercase}}.br span{{font-weight:500;letter-spacing:.22em;font-size:14px;color:#2f78c4}}
.f{{font:600 15px Poppins;letter-spacing:.1em;text-transform:uppercase;color:#77796f}}
.m{{display:flex;align-items:center;gap:40px}}
img{{width:190px;height:190px;border-radius:999px;object-fit:cover;border:6px solid #fff;box-shadow:0 0 0 1px #dcdcd5}}
h1{{margin:0;font:800 74px/.92 Poppins;text-transform:uppercase;letter-spacing:-.05em}}h1 i{{font-weight:700;text-transform:none;letter-spacing:-.03em}}
.s{{font:500 22px Poppins;color:#77796f;margin-top:10px}}
.g{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}
.k{{background:#fff;border:1px solid #dcdcd5;border-radius:14px;padding:18px 20px}}.k b{{display:block;font:800 46px/1 Poppins;letter-spacing:-.03em}}.k span{{display:block;font:500 16px/1.3 Poppins;color:#77796f;margin-top:6px}}
</style></head><body><div class="c">
<div class="t"><div class="br">Gravataí <span>— em dados</span></div><div class="f">Ficha do vereador · 2025–2028</div></div>
<div class="m">{img}<div><h1>{nome}</h1><div class="s">{html.escape(sub)}</div></div></div>
<div class="g">{kp}</div></div></body></html>'''


def pagina(v):
    sub, k = dados(v)
    t = html.escape(f"{v['nome']} ({v['pat']}) · Gravataí em dados")
    d = html.escape(f"{sub}. {k[0][0]} {k[0][1]}, {k[1][0]} {k[1][1]}, {k[2][0]} {k[2][1]}. Ficha completa do mandato 2025–2028.")
    u = f"{SITE}/v/{v['id']}/"
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>{t}</title>
<meta name="description" content="{d}">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="Gravataí em dados">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{u}">
<meta property="og:image" content="{u}card.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE}/#v/{v['id']}">
<meta http-equiv="refresh" content="0; url=/#v/{v['id']}">
<script>location.replace('/#v/{v['id']}')</script>
</head><body><p><a href="/#v/{v['id']}">Abrir a ficha de {html.escape(v['nome'])}</a></p></body></html>'''


def main():
    vs = [v for v in D['ver'] if 'L2' in (v.get('leg') or [])]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1200, 'height': 630})
        for v in vs:
            out = RAIZ / 'v' / v['id']
            out.mkdir(parents=True, exist_ok=True)
            pg.set_content(card(v))
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(out / 'card.png'), type='png')
            (out / 'index.html').write_text(pagina(v), encoding='utf-8')
        b.close()
    print(len(vs), 'prévias geradas')


if __name__ == '__main__':
    main()
