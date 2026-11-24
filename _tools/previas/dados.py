"""Gera a prévia de link de cada gráfico do site e das votações recentes.

Para cada card cria d/<id>/index.html (Open Graph, redireciona para /#d/<id>) e d/<id>/card.png (1200x630).
Votações recentes: d/vt-<doc>-<data>/ (redireciona para /#vt/<doc>-<data>).
Também grava d/destaques.json, usado pela newsletter.

Uso, na raiz do repositório: python3 _tools/previas/dados.py
"""
import json, html, pathlib, shutil
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SITE = 'https://gravataiemdados.com.br'
E = html.escape

CSS = '''body{margin:0}
.c{width:1200px;height:630px;box-sizing:border-box;background:#f8f8f6;color:#41443a;font-family:Poppins,sans-serif;padding:48px 64px;display:flex;flex-direction:column;justify-content:space-between}
.t{display:flex;justify-content:space-between;align-items:center;gap:20px}
.br{font:800 22px Poppins;letter-spacing:.14em;text-transform:uppercase;white-space:nowrap}.br span{font-weight:500;letter-spacing:.22em;font-size:14px;color:#2f78c4}
.tag{font:600 15px Poppins;letter-spacing:.1em;text-transform:uppercase;color:#77796f;text-align:right}
.f{font:500 16px Poppins;color:#77796f}
.g2{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:56px;align-items:center}
.big{font:800 128px/.86 Poppins;letter-spacing:-.06em;white-space:nowrap}
.big.m{font-size:96px}.big.s{font-size:76px}
.tx{font:500 29px/1.28 Poppins;margin-top:16px}.tx i{font-weight:700}
.bx{background:#fff;border:1px solid #dcdcd5;border-radius:18px;padding:24px 26px;display:flex;flex-direction:column;gap:13px}
.bt{font:600 15px Poppins;color:#77796f}
.row .l{display:flex;justify-content:space-between;gap:12px;font:600 17px Poppins}.row .l span:first-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tr{height:12px;background:#eeeee8;border-radius:4px;margin-top:4px}.tr i{display:block;height:12px;border-radius:4px;background:#2f78c4}
.row.h1 .l{color:#b5562f;font-weight:700}.row.h1 i{background:#b5562f}.row.h2 i{background:#41443a}
h1{margin:0;font:800 64px/.95 Poppins;text-transform:uppercase;letter-spacing:-.05em}
.ld{font:400 24px/1.4 Poppins;color:#4d4f47;margin-top:18px;max-width:30ch}
.kg{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:16px}
.k{background:#fff;border:1px solid #dcdcd5;border-radius:14px;padding:18px 20px}.k b{display:block;font:800 44px/1 Poppins;letter-spacing:-.03em;white-space:nowrap}.k span{display:block;font:500 16px/1.3 Poppins;color:#77796f;margin-top:8px}
.vh{font:700 40px/1.15 Poppins;margin:0;max-width:26ch}
.pl{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}.pl span{font:600 20px Poppins;border-radius:999px;padding:8px 16px;background:#e7f1e4;color:#2e6b2e}.pl .n{background:#f6e3dc;color:#a0441f}.pl .a{background:#eeeee8;color:#55574f}
.vb{display:flex;height:16px;border-radius:5px;overflow:hidden;gap:3px}.vb i{display:block}
'''
HEAD = '<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,500;0,600;0,700;0,800;1,700&display=swap"><style>' + CSS + '</style></head><body><div class="c">'
TOP = lambda tag: f'<div class="t"><div class="br">Gravataí <span>— em dados</span></div><div class="tag">{E(tag)}</div></div>'


def bars(x):
    rs = ''.join(f'<div class="row h{b.get("hl", 0)}"><div class="l"><span>{E(b["l"])}</span><span>{E(b["v"])}</span></div><div class="tr"><i style="width:{max(0, min(1, b["w"])) * 100:.1f}%"></i></div></div>' for b in x.get('bars', []))
    return f'<div class="bx"><div class="bt">{E(x.get("bt", ""))}</div>{rs}</div>'


def card(x):
    if x['t'] == 'dest':
        sz = '' if len(x['big']) <= 6 else (' m' if len(x['big']) <= 9 else ' s')
        tx = ' style="font-size:24px"' if len(x['txt']) > 150 else ''
        mid = (f'<div class="g2"><div><div class="big{sz}">{E(x["big"])}</div><div class="tx"{tx}>{x["txt"]}</div></div>{bars(x)}</div>' if x.get('bars')
               else f'<div><div class="big{sz}">{E(x["big"])}</div><div class="tx"{tx} style="max-width:34ch">{x["txt"]}</div></div>')
        return HEAD + TOP(x['tag']) + mid + f'<div class="f">{E(x["fonte"])} · gravataiemdados.com.br</div></div></body></html>'
    if x['t'] == 'kpi':
        ks = x['kpis'][:4]
        kp = ''.join(f'<div class="k"><b>{E(k["b"])}</b><span>{E(k["l"])}</span></div>' for k in ks)
        return HEAD + TOP(x['crumb']) + f'<h1>{E(x["title"])}</h1><div class="kg" style="--n:{len(ks)}">{kp}</div><div class="f">{E(x["fonte"][:110]) + " · " if x.get("fonte") else ""}gravataiemdados.com.br</div></div></body></html>'
    if x['t'] == 'vot':
        tot = max(1, x['S'] + x['N'] + x['B'] + x['A'])
        vb = f'<i style="flex:{x["S"]};background:#3f8f4f"></i>' + (f'<i style="flex:{x["N"]};background:#c0582f"></i>' if x['N'] else '') + (f'<i style="flex:{x["B"] + x["A"]};background:#bdbfb6"></i>' if x['B'] + x['A'] else '')
        pl = f'<span>{x["S"]} a favor</span><span class="n">{x["N"]} contra</span>' + (f'<span class="a">{x["B"]} abstenç{"ão" if x["B"] == 1 else "ões"}</span>' if x['B'] else '') + (f'<span class="a">{x["A"]} não votou</span>' if x['A'] == 1 else (f'<span class="a">{x["A"]} não votaram</span>' if x['A'] else '')) + f'<span class="a">{E(x["res"])}</span>'
        tl = x['title'] if len(x['title']) <= 120 else x['title'][:117].rsplit(' ', 1)[0] + '…'
        return HEAD + TOP(f'Votação na Câmara · {x["d"]}') + f'<div><div class="big m">{x["S"]} × {x["N"]}</div><p class="vh" style="margin-top:18px">{E(tl)}</p><div class="pl">{pl}</div></div><div><div class="vb">{vb}</div><div class="f" style="margin-top:14px">{E(x["sg"])} · Fonte: votação nominal no site da Câmara · gravataiemdados.com.br</div></div></div></body></html>'
    ld = x.get('lead') or ''
    ld = ld if len(ld) <= 200 else ld[:197].rsplit(' ', 1)[0] + '…'
    return HEAD + TOP(x['crumb']) + f'<div><h1>{E(x["title"])}</h1><div class="ld">{E(ld)}</div></div><div class="f">Dados oficiais e conferíveis · gravataiemdados.com.br</div></div></body></html>'


def pagina(x):
    alvo = f"/#vt/{x['key']}" if x['t'] == 'vot' else f"/#d/{x['id']}"
    t = E((x['title'] if x['t'] != 'dest' else x['title']) + ' · Gravataí em dados')
    d = E((x.get('desc') or x.get('lead') or 'Dados oficiais sobre a Câmara e a Prefeitura de Gravataí.')[:240])
    u = f"{SITE}/d/{x['id']}/"
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>{t}</title>
<meta name="description" content="{d}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Gravataí em dados">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{u}">
<meta property="og:image" content="{u}card.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta http-equiv="refresh" content="0; url={alvo}">
<script>location.replace('{alvo}')</script>
</head><body><p><a href="{alvo}">Abrir no Gravataí em dados</a></p></body></html>'''


def main():
    js = (RAIZ / '_tools/previas/extrair.js').read_text(encoding='utf-8')
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 1280, 'height': 900})
        ctx.add_init_script("try{localStorage.setItem('gv-wl','skip');localStorage.setItem('gv-rv','off')}catch(e){}")
        pg = ctx.new_page()
        pg.goto((RAIZ / 'index.html').as_uri())
        pg.wait_for_timeout(2500)
        itens = pg.evaluate(js)
        dest = RAIZ / 'd'
        if dest.exists():
            shutil.rmtree(dest)
        cp = b.new_page(viewport={'width': 1200, 'height': 630})
        for x in itens:
            o = dest / x['id']
            o.mkdir(parents=True, exist_ok=True)
            cp.set_content(card(x))
            cp.wait_for_timeout(250)
            cp.screenshot(path=str(o / 'card.png'), type='png')
            (o / 'index.html').write_text(pagina(x), encoding='utf-8')
        b.close()
    man = [{k: x.get(k) for k in ('id', 't', 'feat', 'title', 'crumb', 'desc', 'date', 'sg', 'res', 'S', 'N', 'tag', 'big')} for x in itens]
    (dest / 'destaques.json').write_text(json.dumps(man, ensure_ascii=False, indent=0), encoding='utf-8')
    print(len(itens), 'prévias;', sum(1 for x in itens if x['feat']), 'com miniresumo')


if __name__ == '__main__':
    main()
