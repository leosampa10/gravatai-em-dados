"""Monta o e-mail personalizado de cada inscrito da newsletter do Gravataí em dados.

Uso (na raiz do repositório):
  python3 _tools/newsletter/montar.py inscritos.json --desde AAAA-MM-DD [--saida pasta]

inscritos.json: lista de {email, nome, freq ("diario"|"semanal"), temas[], vereadores[], bairro, contas[]}
(montada pela tarefa a partir das respostas do formulário Tally GeR76O; NUNCA salve esse arquivo no repositório).
Gera <saida>/<n>.html e <saida>/envios.json ([{email, assunto, arquivo}]) só para quem tem novidade.
"""
import json, re, sys, os, html, argparse, unicodedata

ap = argparse.ArgumentParser()
ap.add_argument('inscritos'); ap.add_argument('--desde', required=True); ap.add_argument('--saida', default='/tmp/newsletter')
ap.add_argument('--hoje', default=None)
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
corr = [c for c in D.get('corr', []) if '-'.join(reversed(c[0].split('/'))) >= a.desde]
cal = D.get('cal', {})

def bloco(titulo, linhas):
    if not linhas: return ''
    return f'<h2 style="font:700 18px Arial,sans-serif;color:#41443a;margin:24px 0 8px;border-bottom:2px solid #41443a;padding-bottom:4px">{html.escape(titulo)}</h2>' + ''.join(f'<p style="font:15px/1.5 Arial,sans-serif;color:#41443a;margin:0 0 12px">{l}</p>' for l in linhas)

def montar(p):
    temas = p.get('temas') or []; vers = p.get('vereadores') or []; todos = 'Todos os vereadores' in vers
    bairro = (p.get('bairro') or '').strip(); contas = p.get('contas') or []
    partes = []
    # votações
    L = []
    for it in vot_novas:
        dt, sg, em, au, res = it[:5]; vv = votos(it); tt = tema_de(em, temas)
        sel = list(vv) if todos else [n for n in vers if n in vv]
        if not tt and not sel: continue
        fav = sum(1 for x in vv.values() if x == 'a favor'); con = sum(1 for x in vv.values() if x == 'contra')
        txt = f'<b>{html.escape(sg)}</b> ({br(dt)}): {html.escape(em)} <span style="color:#77796f">Autor: {html.escape(au or "não informado")}. Resultado: {html.escape(res.lower())}, {fav} a {con}.</span>'
        if sel and not todos: txt += '<br>' + '; '.join(f'{html.escape(n)}: <b>{vv[n]}</b>' for n in sel)
        elif todos and con:
            txt += '<br>Votaram contra: ' + ', '.join(html.escape(n) for n, x in vv.items() if x == 'contra')
        L.append(txt)
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
    if not any(partes): return None
    partes.append(bloco('Correções no site', [f'{c[0]} · {html.escape(c[1])}: {html.escape(c[2])}' for c in corr]))
    corpo = ''.join(x for x in partes if x)
    if not corpo: return None
    ola = f'Olá, {html.escape(p["nome"].split()[0])}!' if p.get('nome') else 'Olá!'
    per = 'da semana' if p.get('freq') == 'semanal' else 'do dia'
    return f'''<div style="max-width:620px;margin:0 auto;background:#f8f8f6;padding:24px">
<p style="font:800 13px Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#41443a;margin:0">Gravataí em dados</p>
<p style="font:15px Arial,sans-serif;color:#41443a">{ola} Este é o seu resumo {per}, com o que você escolheu acompanhar. Tudo com fonte oficial; sem recomendação de voto.</p>
{corpo}
<p style="font:13px/1.5 Arial,sans-serif;color:#77796f;margin-top:28px;border-top:1px solid #dcdcd5;padding-top:12px">
Mais detalhes em <a href="{SITE}" style="color:#41443a">gravataiemdados.com.br</a>. Para mudar o que você recebe, inscreva-se de novo com o mesmo e-mail.<br>
<a href="{CANCELAR}{html.escape(p["email"])}" style="color:#77796f">Cancelar estes e-mails</a></p></div>'''

os.makedirs(a.saida, exist_ok=True); envios = []
hoje = br(a.hoje) if a.hoje else ''
for n, p in enumerate(json.load(open(a.inscritos, encoding='utf-8'))):
    h = montar(p)
    if not h: continue
    f = f'{a.saida}/{n}.html'; open(f, 'w', encoding='utf-8').write(h)
    envios.append({'email': p['email'], 'assunto': f'Gravataí em dados: seu resumo {"da semana" if p.get("freq")=="semanal" else "do dia"}' + (f' ({hoje})' if hoje else ''), 'arquivo': f})
json.dump(envios, open(f'{a.saida}/envios.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(envios), 'e-mails montados em', a.saida)
