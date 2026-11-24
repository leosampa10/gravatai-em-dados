"""Monta o e-mail de boas-vindas de cada nova inscrição.

Uso (na raiz do repositório):
  python3 _tools/newsletter/boasvindas.py novos.json [--saida pasta]
novos.json: lista de {email, nome, freq ("diario"|"semanal"), temas[], vereadores[], bairro, contas[], pedido} (só as inscrições novas).
Gera <saida>/bv-<n>.html, bv-<n>.txt e <saida>/boasvindas.json ([{email, assunto, arquivo, texto, cancelar}]).
O cartão (img/boas-vindas.png) e o logo (img/logo-email.png) vêm do site; regenere com _tools/newsletter/imagens.py.
"""
import json, html, os, re, argparse
ap = argparse.ArgumentParser(); ap.add_argument('novos'); ap.add_argument('--saida', default='/tmp/nl')
a = ap.parse_args()
s = open('index.html', encoding='utf-8').read(); i = s.find('const DATA='); D = json.loads(s[i+11:s.find('\n', i)].rstrip()[:-1])
SITE = 'https://gravataiemdados.com.br'; CANCELAR = 'https://tally.so/r/q5RNa5?email='
VID = {v['nome']: v['id'] for v in D['ver']}
E = html.escape
P = 'font:15px/1.55 Arial,sans-serif;color:#41443a;margin:0 0 14px'

def li(x): return f'<li style="margin:0 0 6px">{x}</li>'

def montar(p):
    nome = (p.get('nome') or '').split()
    ola = f'Olá, {E(nome[0])}!' if nome else 'Olá!'
    freq = 'todo dia em que houver novidade' if p.get('freq') == 'diario' else 'uma vez por semana, às segundas-feiras'
    itens = []
    vs = [v for v in (p.get('vereadores') or [])]
    if 'Todos os vereadores' in vs: itens.append('como votou cada vereador nas votações da Câmara')
    else:
        for v in vs:
            vid = VID.get(v)
            itens.append(f'como <b>{E(v)}</b> vota na Câmara' + (f' (<a href="{SITE}/v/{vid}/" style="color:#41443a;font-weight:700">ver a ficha</a>)' if vid else ''))
    if p.get('temas'): itens.append('notícias e votações sobre ' + ', '.join(E(t) for t in p['temas']))
    if p.get('bairro'): itens.append(f'o que sair sobre o bairro <b>{E(p["bairro"])}</b>')
    for c in p.get('contas') or []: itens.append(E(c))
    if (p.get('pedido') or '').strip(): itens.append(f'o que você pediu: <i>"{E(p["pedido"].strip())}"</i>; sempre que houver novidade sobre isso, entra no e-mail')
    itens.append('a pauta da cidade: as votações mais disputadas e as manchetes mais recentes')
    u = SITE
    h = f'''<div style="max-width:620px;margin:0 auto;background:#f8f8f6;padding:24px">
<a href="{SITE}" style="display:inline-block;text-decoration:none;margin:0 0 18px"><img src="{SITE}/img/logo-email.png" width="163" height="36" alt="Gravataí em dados" style="display:block;border:0"></a>
<a href="{u}" style="display:block;text-decoration:none;margin:0 0 20px"><img src="{SITE}/img/boas-vindas.png" width="572" alt="Boas-vindas ao Gravataí em dados: votações da Câmara, a pauta da cidade e dados conferíveis" style="display:block;width:100%;height:auto;border:1px solid #dcdcd5;border-radius:10px"></a>
<p style="{P}">{ola} Sua inscrição está confirmada.</p>
<p style="{P}">Você vai receber um resumo <b>{freq}</b>, com:</p>
<ul style="font:15px/1.55 Arial,sans-serif;color:#41443a;margin:0 0 14px;padding-left:20px">{''.join(li(x) for x in itens)}</ul>
<p style="{P}">Tudo com fonte oficial e sem recomendação de voto. Enquanto o primeiro resumo não chega, o site está em <a href="{SITE}" style="color:#41443a;font-weight:700">gravataiemdados.com.br</a>.</p>
<p style="font:13px/1.5 Arial,sans-serif;color:#77796f;margin-top:24px;border-top:1px solid #dcdcd5;padding-top:12px">Para mudar o que você recebe, inscreva-se de novo com o mesmo e-mail. Dúvidas ou sugestões: é só responder este e-mail.<br><a href="{CANCELAR}{E(p["email"])}" style="color:#77796f">Cancelar estes e-mails</a></p></div>'''
    return h

def texto(h):
    def _ln(m):
        tx = re.sub('<[^>]+>', '', m.group(2)).strip()
        if not tx:
            al = re.search(r'alt="([^"]*)"', m.group(2)); return (al.group(1) if al else '') + ' ' + m.group(1) + '\n'
        return tx + ' (' + m.group(1) + ')'
    t = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', _ln, h, flags=re.S)
    t = re.sub(r'<li[^>]*>', '• ', t); t = re.sub(r'<(br|/p|/li)>', '\n', t); t = re.sub('<[^>]+>', '', t)
    return html.unescape(re.sub(r'\n\s*\n+', '\n\n', t)).strip()

os.makedirs(a.saida, exist_ok=True); out = []
for n, p in enumerate(json.load(open(a.novos, encoding='utf-8'))):
    h = montar(p); f = f'{a.saida}/bv-{n}.html'; ft = f'{a.saida}/bv-{n}.txt'
    open(f, 'w', encoding='utf-8').write(h); open(ft, 'w', encoding='utf-8').write(texto(h))
    out.append({'email': p['email'], 'assunto': 'Inscrição confirmada: Gravataí em dados', 'arquivo': f, 'texto': ft, 'cancelar': CANCELAR + p['email']})
json.dump(out, open(f'{a.saida}/boasvindas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'boas-vindas montados em', a.saida)
