"""Monta o e-mail personalizado de cada inscrito da newsletter do Gravataí em dados.

Uso (na raiz do repositório):
  python3 _tools/newsletter/montar.py inscritos.json --desde AAAA-MM-DD [--saida pasta]

inscritos.json: lista de {email, nome, freq ("diario"|"semanal"), temas[], vereadores[], bairro, contas[], pedido}
(pedido = texto do campo "Quer receber alguma informação específica?"; vira um bloco fixo em todo envio quando há novidade sobre o assunto)
(montada pela tarefa a partir das respostas do formulário Tally GeR76O; NUNCA salve esse arquivo no repositório).
Usa d/destaques.json (gerado por _tools/previas/dados.py) para o bloco "Em destaque" com os cartões de dados e votações.
Gera <saida>/<n>.html e <saida>/envios.json ([{email, assunto, arquivo}]) só para quem tem novidade.
"""
import json, re, sys, os, html, argparse, unicodedata

ap = argparse.ArgumentParser()
ap.add_argument('inscritos'); ap.add_argument('--desde', required=True); ap.add_argument('--saida', default='/tmp/newsletter')
ap.add_argument('--hoje', default=None)
ap.add_argument('--imagens', default='url', choices=['anexo', 'url'], help='anexo: cartões como imagem embutida (cid:attN), para o conector do Gmail; url: link para o site')
a = ap.parse_args()
s = open('index.html', encoding='utf-8').read(); i = s.find('const DATA='); D = json.loads(s[i+11:s.find('\n', i)].rstrip()[:-1])
SITE = 'https://gravataiemdados.com.br'
CANCELAR = 'https://tally.so/r/q5RNa5?email='

def norm(t): return unicodedata.normalize('NFKD', (t or '').lower()).encode('ascii', 'ignore').decode()
TEMAS = {
 'Saúde': r'saude|hospital|ubs|posto|samu|medic|leito|sus\b|vacina|upa\b',
 'Educação e creches': r'educa|escola|creche|ensino|professor|fundeb|aluno|merenda|ideb',
 'Transporte': r'transporte|onibus|tarifa|passagem|mobilidade|transito|linha',
 'Obras, ruas e drenagem': r'obra|pavimenta|asfalto|rua|drenagem|bueiro|ponte|calcada|ilumina',
 'Impostos e taxas (IPTU, iluminação)': r'iptu|imposto|taxa|tribut|iss\b|cosip|contribuicao|planta de valores',
 'Servidores públicos': r'servidor|13o|13º|salario|reajuste|folha|concurso|magisterio|piso',
 'Meio ambiente e enchentes': r'ambient|enchente|chuva|alag|arroio|rio gravatai|defesa civil|saneamento|esgoto|agua|corsan|lixo',
 'Segurança': r'seguranca|guarda|policia|brigada|crime|violencia|homicid',
 'Assistência social e habitação': r'assistencia|social|habita|moradia|cras|creas|vulnerab|idoso|populacao de rua',
}
V = D['vts']; B = '0123456789abcdefghijklmn'; NM = {v['id']: v['nome'] for v in D['ver']}; NM.update(V.get('nn') or {})
AB = {'f': 'a favor', 'c': 'contra', 'a': 'abstenção', 'n': 'não votou'}

def votos(it):
    m = {}
    for x, y in re.findall(r'([0-9a-n])([fcanx])', it[5] or ''): m[V['nm'][B.index(x)]] = y
    out = {}
    for k, vid in enumerate(V['nm']):
        y = m.get(vid)
        if y == 'x': continue
        if y is None:
            if k > 20: continue
            y = 'f'
        out[NM.get(vid, vid)] = AB[y]
    pres = 'clebes' if it[0] < '2026' else 'dila'
    pn = NM.get(pres, pres)
    if out.get(pn) == 'não votou': out[pn] = 'não votou (presidente, só vota em empate)'
    return out

def br(d): return '/'.join(reversed(d.split('-'))) if d else ''
def tema_de(txt, temas): return [t for t in temas if t in TEMAS and re.search(TEMAS[t], norm(txt))]

vot_novas = [it for it in V['it'] if it[0] >= a.desde]
manch = [(f['nm'], x) for f in D['manchetes']['fontes'] for x in f['itens'] if (x.get('d') or '') >= a.desde]
cal = D.get('cal', {})
try: DEST = json.load(open('d/destaques.json', encoding='utf-8'))
except Exception: DEST = []
DID = {x['id']: x for x in DEST}
# cartão de dado ligado a cada tema (os demais giram dia a dia)
TEMA_CARD = {'Educação e creches': 'c-piso', 'Saúde': 'c-piso', 'Assistência social e habitação': 'c-cal', 'Servidores públicos': 's-quanto-ganham',
             'Obras, ruas e drenagem': 'ctr-top', 'Impostos e taxas (IPTU, iluminação)': 'c-cal'}
ROD = [x['id'] for x in DEST if x.get('feat') and x['t'] in ('dest', 'kpi')]
import datetime
DIA = (datetime.date.fromisoformat(a.hoje) if a.hoje else datetime.date.today()).toordinal()

ANEXOS = []
import hashlib
def img(rel, u):
    # rel = caminho local do PNG (d/<id>/card.png); u = página no site
    if a.imagens == 'url' or not os.path.exists(rel): return f'{u}card.png'
    ANEXOS.append({'path': os.path.abspath(rel), 'filename': rel.replace('/', '-'), 'sha256': hashlib.sha256(open(rel, 'rb').read()).hexdigest()})
    return f'cid:att{len(ANEXOS) - 1}'

def cartao(cid):
    x = DID.get(cid)
    if not x: return ''
    u = f'{SITE}/d/{cid}/'
    return (f'<a href="{u}" style="display:block;text-decoration:none;margin:0 0 14px"><img src="{img(f"d/{cid}/card.png", u)}" width="572" alt="{html.escape(x.get("desc") or x["title"])}" style="display:block;width:100%;height:auto;border:1px solid #dcdcd5;border-radius:10px"></a>')

VID = {v['nome']: v['id'] for v in D['ver']}
def cartao_ver(nome):
    vid = VID.get(nome)
    if not vid or not os.path.exists(f'v/{vid}/card.png'): return ''
    u = f'{SITE}/v/{vid}/'
    return (f'<a href="{u}" style="display:block;text-decoration:none;margin:0 0 14px"><img src="{img(f"v/{vid}/card.png", u)}" width="572" alt="Ficha de {html.escape(nome)}" style="display:block;width:100%;height:auto;border:1px solid #dcdcd5;border-radius:10px"></a>')

def vers_de(p):
    vs = [n for n in (p.get('vereadores') or []) if n in VID]
    ped = norm(p.get('pedido') or '')
    for n in VID:
        if n not in vs and ped and (norm(n) in ped or (len(n.split()) > 1 and norm(n.split()[-1]) in ped.split()) or norm(n.split()[0]) in ped.split()):
            vs.append(n)
    return vs[:3]

def destaques(p, vots):
    temas = p.get('temas') or []; contas = p.get('contas') or []
    fichas = ''.join(cartao_ver(n) for n in vers_de(p))
    ids = []
    for it in vots[:2]:
        k = 'vt-' + it[6].split('-')[-1] + '-' + it[0].replace('-', '')
        if k in DID: ids.append(k)
    pref = [TEMA_CARD[t] for t in temas if t in TEMA_CARD]
    if contas: pref.append('c-cal'); pref.append('ctr-top')
    n = 2 if p.get('freq') == 'semanal' else 1
    pool = [c for c in pref if c in DID] or ROD
    for j in range(len(pool)):
        if n <= 0: break
        c = pool[(DIA + j) % len(pool)]
        if c not in ids: ids.append(c); n -= 1
    if not ids and not fichas: return ''
    return '<h2 style="font:700 18px Arial,sans-serif;color:#41443a;margin:24px 0 10px;border-bottom:2px solid #41443a;padding-bottom:4px">Em destaque</h2>' + fichas + ''.join(cartao(c) for c in ids)

def bloco(titulo, linhas):
    if not linhas: return ''
    return f'<h2 style="font:700 18px Arial,sans-serif;color:#41443a;margin:24px 0 8px;border-bottom:2px solid #41443a;padding-bottom:4px">{html.escape(titulo)}</h2>' + ''.join(f'<p style="font:15px/1.5 Arial,sans-serif;color:#41443a;margin:0 0 12px">{l}</p>' for l in linhas)

STOP = set('sobre quero saber receber gostaria informacao informacoes dados quanto como onde quando qual quais para pelo pela mais menos tambem cidade gravatai prefeitura camara vereador vereadores'.split())
def chaves(txt): return [w for w in re.findall(r'[a-z0-9]{4,}', norm(txt)) if w not in STOP]

def pauta_quente(ja):
    # as manchetes mais recentes do período (SobVigia primeiro), mesmo fora dos temas escolhidos
    L = []
    rec = sorted(manch, key=lambda fx: (fx[1].get('d') or ''), reverse=True)
    rec = [fx for fx in rec if fx[0] == 'SobVigia'] + [fx for fx in rec if fx[0] != 'SobVigia']
    for fonte, x in rec:
        if x['u'] in ja: continue
        L.append(f'<a href="{html.escape(x["u"])}" style="color:#41443a;font-weight:700">{html.escape(x["t"])}</a><br><span style="color:#77796f">{html.escape(fonte)} · {br(x.get("d"))}</span>')
        if len(L) == 3: break
    return bloco('A pauta da cidade', L)

def pedido(p):
    ks = chaves(p.get('pedido') or '')
    if not ks: return ''
    hit = lambda t: any(k in norm(t) for k in ks)
    L = []
    for n in vers_de({'pedido': p.get('pedido')}):
        vid = VID[n]; v = next(x for x in D['ver'] if x['id'] == vid)
        L.append(f'<b>{html.escape(n)}</b> ({html.escape(v.get("pat") or "")}, {html.escape(v.get("bloco") or "")}): veja como votou em cada projeto do período logo abaixo, e a ficha completa em <a href="{SITE}/v/{vid}/" style="color:#41443a;font-weight:700">gravataiemdados.com.br/v/{vid}</a>.')
        for it in vot_novas:
            vv = votos(it); x = vv.get(n)
            if x and x != 'a favor': L.append(f'Em {br(it[0])}, no {html.escape(it[1])} ({html.escape(it[2])}), {html.escape(n.split()[0])} <b>{html.escape(x)}</b>.')
    for it in vot_novas:
        if hit(it[1] + ' ' + it[2]):
            L.append(f'<b>{html.escape(it[1])}</b> ({br(it[0])}): {html.escape(it[2])} <span style="color:#77796f">Resultado: {html.escape(it[4].lower())}.</span>')
    for fonte, x in manch:
        if hit(x['t']): L.append(f'<a href="{html.escape(x["u"])}" style="color:#41443a;font-weight:700">{html.escape(x["t"])}</a><br><span style="color:#77796f">{html.escape(fonte)} · {br(x.get("d"))}</span>')
    for x in DEST:
        if x['t'] != 'vot' and hit((x.get('title') or '') + ' ' + (x.get('desc') or '')):
            L.append(f'{html.escape(x.get("desc") or x["title"])} <a href="{SITE}/d/{x["id"]}/" style="color:#41443a;font-weight:700">Ver no site →</a>')
        if len(L) >= 6: break
    return bloco('Sobre o que tu pediu: ' + (p.get('pedido') or '')[:80], L[:6])

def montar(p):
    temas = p.get('temas') or []; vers = p.get('vereadores') or []; todos = 'Todos os vereadores' in vers
    bairro = (p.get('bairro') or '').strip(); contas = p.get('contas') or []
    partes = []
    # votações
    L = []; VS = []
    for it in vot_novas:
        dt, sg, em, au, res = it[:5]; vv = votos(it); tt = tema_de(em, temas)
        sel = list(vv) if todos else [n for n in vers if n in vv]
        if not tt and not sel: continue
        fav = sum(1 for x in vv.values() if x == 'a favor'); con = sum(1 for x in vv.values() if x == 'contra')
        txt = f'<b>{html.escape(sg)}</b> ({br(dt)}): {html.escape(em)} <span style="color:#77796f">Autor: {html.escape(au or "não informado")}. Resultado: {html.escape(res.lower())}, {fav} a {con}.</span>'
        if sel and not todos: txt += '<br>' + '; '.join(f'{html.escape(n)}: <b>{vv[n]}</b>' for n in sel)
        elif todos and con:
            txt += '<br>Votaram contra: ' + ', '.join(html.escape(n) for n, x in vv.items() if x == 'contra')
        L.append(txt); VS.append(it)
    partes.append(bloco('Votações na Câmara', L))
    # notícias
    L = []
    for fonte, x in manch:
        t = x['t']; hit = tema_de(t + ' ' + (x.get('ed') or ''), temas) or (bairro and norm(bairro) in norm(t)) or any(norm(n) in norm(t) for n in vers if n != 'Todos os vereadores')
        if hit: L.append(f'<a href="{html.escape(x["u"])}" style="color:#41443a;font-weight:700">{html.escape(t)}</a><br><span style="color:#77796f">{html.escape(fonte)} · {br(x.get("d"))}</span>')
    partes.append(bloco('Notícias' + (f' (inclui {html.escape(bairro)})' if bairro else ''), L[:12]))
    # contas
    L = []
    if 'Gasto da Prefeitura a cada dois meses' in contas and cal.get('asof') and cal.get('novo'):
        L.append(f'Saiu o relatório do {html.escape(cal["asof"])}. Veja quanto cada área já gastou do previsto no ano: <a href="{SITE}/#prefeitura:p-fin" style="color:#41443a">Prefeitura › Finanças</a>.')
    if 'Contratos novos e aditivos' in contas and D['ctr']['meta'].get('novos'):
        for c in D['ctr']['meta']['novos']: L.append(html.escape(c))
    partes.append(bloco('Prefeitura e contas', L))
    ped = pedido(p)
    if not any(partes) and not ped: return None
    ja = set(re.findall(r'href="([^"]+)"', ''.join(partes)))
    corpo = destaques(p, sorted(VS, key=lambda it: (sum(1 for x in votos(it).values() if x == 'contra'), it[0]), reverse=True)) + ped + pauta_quente(ja) + ''.join(x for x in partes if x)
    if not corpo: return None
    ola = f'Buenas, {html.escape(p["nome"].split()[0])}!' if p.get('nome') else 'Buenas!'
    per = 'da semana' if p.get('freq') == 'semanal' else 'do dia'
    return f'''<div style="max-width:620px;margin:0 auto;background:#f8f8f6;padding:24px">
<a href="{SITE}" style="display:inline-block;text-decoration:none"><img src="{SITE}/img/logo-email.png" width="163" height="36" alt="Gravataí em dados" style="display:block;border:0"></a>
<p style="font:15px Arial,sans-serif;color:#41443a">{ola} Tá aqui o teu resumo {per}, fresquinho, com o que tu escolheu acompanhar. Tudo com fonte oficial; sem recomendação de voto.</p>
{corpo}
<p style="font:13px/1.5 Arial,sans-serif;color:#77796f;margin-top:28px;border-top:1px solid #dcdcd5;padding-top:12px">
Quer mais? Tá tudo em <a href="{SITE}" style="color:#41443a">gravataiemdados.com.br</a>. Pra mudar o que tu recebe, é só se inscrever de novo com o mesmo e-mail. Feito em Gravataí, de chimarrão do lado.<br>
<a href="{CANCELAR}{html.escape(p["email"])}" style="color:#77796f">Cancelar estes e-mails</a></p></div>'''

os.makedirs(a.saida, exist_ok=True); envios = []
hoje = br(a.hoje) if a.hoje else ''
for n, p in enumerate(json.load(open(a.inscritos, encoding='utf-8'))):
    ANEXOS.clear()
    h = montar(p)
    if not h: continue
    f = f'{a.saida}/{n}.html'; open(f, 'w', encoding='utf-8').write(h)
    def _ln(m):
        tx = re.sub('<[^>]+>', '', m.group(2)).strip()
        if not tx:
            al = re.search(r'alt="([^"]*)"', m.group(2)); tx = '• ' + (al.group(1) if al else '')
            return tx + ' ' + m.group(1) + '<br>'
        return tx + ' (' + m.group(1) + ')'
    t = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', _ln, h, flags=re.S)
    t = re.sub(r'<(br|/p|/h2)>', '\n', t); t = re.sub('<[^>]+>', '', t); t = html.unescape(re.sub(r'\n\s*\n+', '\n\n', t)).strip()
    ft = f'{a.saida}/{n}.txt'; open(ft, 'w', encoding='utf-8').write(t)
    envios.append({'email': p['email'], 'assunto': f'Gravataí em dados: seu resumo {"da semana" if p.get("freq")=="semanal" else "do dia"}' + (f' ({hoje})' if hoje else ''), 'arquivo': f, 'texto': ft, 'cancelar': CANCELAR + p['email'], 'anexos': list(ANEXOS)})
json.dump(envios, open(f'{a.saida}/envios.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(envios), 'e-mails montados em', a.saida)
