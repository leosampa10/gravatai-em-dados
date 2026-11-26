"""Capa nova dos carrosséis (estilo cartaz): fundo de cor chapada, pergunta grande, card do site
em tema claro levemente inclinado, o Rio Gravataí cruzando atrás, o Morro Itacolomi (com a Pedra
dos Cachorrinhos) no pé e a etiqueta grifada embaixo. Usado por make.build quando o spec tem cap.capa.

spec.cap.capa = {"cor": "azul|verde|terra|ocre|creme|noite", "t": "PERGUNTA EM CAIXA ALTA <i>com ênfase</i>",
                 "tag": "ETIQUETA CURTA", "src": "Fonte: ..."}
"""
import json, os, pathlib
GEO = json.load(open(pathlib.Path(__file__).with_name('geo.json')))
PAL = {  # fundo, texto, morro (tom do fundo), rio, etiqueta (fundo, texto)
 'azul':  ('#2F78C4', '#F8F8F6', '#2A6BB0', 'rgba(248,248,246,.45)', '#F2CE6E', '#1D1E1A'),
 'verde': ('#5F7A43', '#F8F8F6', '#556E3C', 'rgba(248,248,246,.45)', '#F2CE6E', '#1D1E1A'),
 'terra': ('#B5562F', '#F8F8F6', '#A24C29', 'rgba(248,248,246,.45)', '#1D1E1A', '#F8F8F6'),
 'ocre':  ('#D9A441', '#1D1E1A', '#C99536', 'rgba(29,30,26,.25)',    '#1D1E1A', '#F8F8F6'),
 'creme': ('#EBE6D6', '#2F78C4', '#DED7C2', 'rgba(47,120,196,.45)',  '#2F78C4', '#F8F8F6'),
 'noite': ('#1D1E1A', '#ECEBE4', '#2B2C27', 'rgba(111,168,230,.5)', '#F2CE6E', '#1D1E1A'),
}
ORDEM = ['azul','ocre','verde','creme','terra']  # rodízio (o escuro 'noite' só se pedir)
FONT = '<link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,600;0,700;0,800;0,900;1,700;1,800&display=swap" rel="stylesheet">'

def marca(cor):
    import re
    m = GEO['mark']
    cs = re.findall(r'<circle[^>]*>', m)
    return f'<svg viewBox="-4 -4 208 114" width="92" height="51" fill="{cor}">{"".join(c if c.endswith("/>") else c+"</circle>" for c in cs)}</svg>'

def html(cap, img, n_total=6, off=0):
    c = cap['capa']; bg, ink, mor, rio, tb, tt = PAL.get(c.get('cor', 'azul'), PAL['azul'])
    ita = GEO['ita']
    # só o contorno do morro e o cachorrinho, preenchidos
    import re
    d = re.search(r'<path d="(M0 132[^"]*)"', ita).group(1)
    dog = re.search(r'(<g class="dog".*?</g>)', ita, re.S).group(1)
    morro = (f'<svg viewBox="0 0 1168 140" preserveAspectRatio="none" style="position:absolute;left:-20px;bottom:0;width:1120px;height:300px">'
             f'<path d="{d} L1168 140 L0 140 Z" fill="{mor}"/>{dog.replace("currentColor", mor)}</svg>')
    rio_svg = (f'<svg viewBox="0 0 1200 16" preserveAspectRatio="none" style="position:absolute;left:0;bottom:92px;width:1080px;height:40px">'
               f'<path d="{GEO["rio"]}" fill="{rio}"/></svg>')
    return f'''<!doctype html><html><head><meta charset="utf-8">{FONT}<style>
body{{margin:0}}*{{box-sizing:border-box}}
.c{{width:1080px;height:1350px;background:{bg};color:{ink};position:relative;overflow:hidden;font-family:Poppins,sans-serif}}
.top{{position:absolute;left:72px;right:72px;top:60px;display:flex;justify-content:space-between;align-items:center}}
.at{{font:700 22px Poppins;letter-spacing:.12em;text-transform:uppercase;opacity:.85}}
h1{{position:absolute;left:72px;right:72px;top:150px;margin:0;font-weight:900;text-transform:uppercase;font-size:{c.get('fs',104)}px;line-height:.9;letter-spacing:-.05em}}
h1 i{{font-weight:800;text-transform:none;letter-spacing:-.04em}}
.card{{position:absolute;left:50%;top:{c.get('y',440)}px;width:{c.get('w',820)}px;max-height:{c.get('h',580)}px;overflow:hidden;transform:translateX(-50%) rotate({c.get('rot',-2.5)}deg);background:#fff;border-radius:26px;padding:14px;box-shadow:0 30px 60px rgba(0,0,0,.28),0 4px 10px rgba(0,0,0,.12)}}
.card img{{display:block;width:100%;border-radius:16px}}
.card:after{{content:'';position:absolute;left:0;right:0;bottom:0;height:70px;background:linear-gradient(transparent,#fff);border-radius:0 0 26px 26px}}
.tag{{position:absolute;left:72px;top:{c.get('y',440)+c.get('h',580)-30}px;z-index:3;max-width:936px;background:{tb};color:{tt};font:900 34px/1.08 Poppins;text-transform:uppercase;letter-spacing:-.02em;padding:12px 20px 10px;transform:rotate(-1deg);box-shadow:6px 6px 0 rgba(0,0,0,.12)}}
.ft{{position:absolute;left:72px;right:72px;bottom:40px;z-index:2;display:flex;justify-content:space-between;gap:30px;font:400 19px/1.3 Poppins;color:{ink};opacity:.85}}
.ft b{{font-weight:700;white-space:nowrap}}
</style></head><body><div class="c">
{morro}{rio_svg}
<div class="top"><span class="at">@gravataiemdados</span>{marca(ink)}</div>
<h1>{c['t']}</h1>
<div class="card"><img id="sh" src="file://{os.path.abspath(img)}"></div>
<div class="tag">{c['tag']}</div>
<div class="ft"><span>{c.get('src') or cap.get('src','')}</span><b>gravataiemdados.com.br</b></div>
</div>
<script>/* card logo abaixo do título; corta o print a partir de "off" (px do site) */
(function(){{const h=document.querySelector('h1'),c=document.querySelector('.card'),t=document.querySelector('.tag'),im=document.getElementById('sh');
function lay(){{const top=Math.max({c.get('y',0)},h.offsetTop+h.offsetHeight+46);c.style.top=top+'px';const mh=Math.min({c.get('h',640)},1090-top);c.style.maxHeight=mh+'px';
 if({off}&&im.naturalWidth)im.style.marginTop=(-{off}*3*im.width/im.naturalWidth+10)+'px';t.style.top=(top+Math.min(mh,c.offsetHeight)-30)+'px';}}
if(im.complete)lay();else im.onload=lay;document.fonts&&document.fonts.ready.then(lay);}})();</script>
</body></html>'''
