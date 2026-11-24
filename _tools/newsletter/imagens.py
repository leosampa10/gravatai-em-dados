"""Gera as imagens fixas da newsletter: img/logo-email.png (logo do site) e img/boas-vindas.png (cartão de boas-vindas).
Uso, na raiz do repositório: python3 _tools/newsletter/imagens.py"""
import pathlib, re, math
from playwright.sync_api import sync_playwright
R = pathlib.Path(__file__).resolve().parents[2]
s = (R / 'index.html').read_text(encoding='utf-8')
i = s.find('<span class="gv-wm">'); SVG = s[s.rfind('<svg', 0, i):i].replace('class="gv-mark"', 'style="width:BWpx;height:BHpx;flex:none;color:#41443a"')
FONT = '<link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,700&display=swap" rel="stylesheet">'

def logo(k=1.0):
    return (f'<div style="display:flex;align-items:center;gap:{10*k:.0f}px">' + SVG.replace('BW', f'{52*k:.0f}').replace('BH', f'{29*k:.0f}') +
            f'<div style="display:flex;flex-direction:column;line-height:1"><b style="font:900 {19*k:.0f}px/1 Poppins;letter-spacing:-.02em;text-transform:uppercase;color:#41443a">Gravataí</b>'
            f'<i style="display:flex;align-items:center;gap:{6*k:.0f}px;margin-top:{3*k:.0f}px;font:600 {9.5*k:.1f}px/1 Poppins;font-style:normal;letter-spacing:.32em;text-transform:uppercase;color:#77796f">'
            f'<s style="display:inline-block;width:{14*k:.0f}px;height:{2*k:.0f}px;border-radius:2px;background:#4f86c6"></s>em dados</i></div></div>')

dots = ''
for r, n in ((48, 7), (76, 10), (104, 13), (132, 16)):
    for j in range(n):
        a = math.pi * j / (n - 1)
        dots += f'<i style="left:{140 + r*math.cos(a):.0f}px;top:{140 - r*math.sin(a):.0f}px"></i>'

BV = f'''<!doctype html><html><head><meta charset="utf-8">{FONT}<style>
body{{margin:0}}.c{{width:1200px;height:600px;box-sizing:border-box;padding:52px 64px 56px;font-family:Poppins;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;background:#f8f8f6;color:#41443a}}
.ed{{font:600 15px Poppins;letter-spacing:.12em;text-transform:uppercase;color:#77796f}}
h1{{margin:0;font:800 84px/.9 Poppins;text-transform:uppercase;letter-spacing:-.055em;position:relative}}h1 i{{font-weight:700;text-transform:none;letter-spacing:-.03em}}
p.s{{margin:18px 0 0;font:400 26px/1.35 Poppins;color:#77796f;max-width:30ch}}
.k{{display:flex;gap:16px;position:relative}}.k div{{flex:1;border-radius:14px;padding:18px 20px;background:#fff;border:1px solid #dcdcd5}}.k b{{display:block;font:700 19px/1.25 Poppins}}.k span{{display:block;font:400 15px/1.35 Poppins;margin-top:6px;color:#77796f}}
.k em{{font-style:normal;display:inline-block;font:800 13px Poppins;letter-spacing:.1em;color:#2f78c4;margin-bottom:8px}}
.dots{{position:absolute;right:56px;top:160px;width:290px;height:150px}}.dots i{{position:absolute;width:12px;height:12px;border-radius:50%;background:#dcdcd5}}.dots i:nth-child(3n){{background:#2f78c4;opacity:.55}}
</style></head><body><div class="c"><div class="dots">{dots}</div>
<div style="display:flex;justify-content:space-between;align-items:center;position:relative">{logo(1.5)}<div class="ed">Inscrição confirmada</div></div>
<div><h1>Boas-vindas ao<br><i>Gravataí em dados</i></h1><p class="s">O que faz quem você elegeu, direto no seu e-mail.</p></div>
<div class="k"><div><em>01</em><b>Votações da Câmara</b><span>o placar e o voto de quem você acompanha</span></div><div><em>02</em><b>A pauta da cidade</b><span>as notícias que importam, com link para a fonte</span></div><div><em>03</em><b>Dados conferíveis</b><span>números oficiais, sem recomendação de voto</span></div></div>
</div></body></html>'''

LG = f'<!doctype html><html><head><meta charset="utf-8">{FONT}<style>body{{margin:0;background:transparent}}#l{{display:inline-block;padding:2px}}</style></head><body><div id="l">{logo(1.0)}</div></body></html>'

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1200, 'height': 600})
    pg.set_content(BV); pg.wait_for_timeout(700); pg.screenshot(path=str(R / 'img/boas-vindas.png'))
    pg2 = b.new_page(viewport={'width': 400, 'height': 100}, device_scale_factor=3)
    pg2.set_content(LG); pg2.wait_for_timeout(700); pg2.locator('#l').screenshot(path=str(R / 'img/logo-email.png'), omit_background=True)
    b.close()
print('ok')
