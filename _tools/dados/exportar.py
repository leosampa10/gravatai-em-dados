"""Gera os CSVs de /dados a partir do DATA do index.html. Uso: python3 _tools/dados/exportar.py (na raiz do repositório)."""
import json,csv,os
s=open('index.html',encoding='utf-8').read();i=s.find('const DATA=');j=s.find('\n',i)
D=json.loads(s[i+11:j].rstrip()[:-1]);os.makedirs('dados',exist_ok=True)
def w(nome,cab,linhas):
    with open('dados/'+nome,'w',newline='',encoding='utf-8-sig') as f:
        c=csv.writer(f,delimiter=';');c.writerow(cab);c.writerows(linhas)
    print(nome,len(linhas))
# vereadores
L=[]
for v in D['ver']:
    p=v.get('prod') or {};g=lambda k,l:(p.get(k) or {}).get(l)
    L.append([v['id'],v['nome'],v.get('p20'),v.get('pat'),v.get('bloco'),'/'.join(v.get('leg',[])),v.get('v20'),v.get('v24'),v.get('s20'),v.get('s24'),g('pl','L1'),g('pl','L2'),g('apr','L1'),g('apr','L2'),g('pi','L1'),g('pi','L2'),g('req','L1'),g('req','L2')])
w('vereadores.csv',['id','nome','partido_2020','partido_atual','bloco','legislaturas','votos_2020','votos_2024','situacao_2020','situacao_2024','projetos_2021_24','projetos_2025_28','viraram_lei_2021_24','viraram_lei_2025_28','pedidos_info_2021_24','pedidos_info_2025_28','requerimentos_2021_24','requerimentos_2025_28'],L)
# votações nominais (um voto por linha)
V=D['vts'];B='0123456789abcdefghijklmn';AB={'f':'sim','c':'não','a':'abstenção','n':'não votou'};nome={v['id']:v['nome'] for v in D['ver']};nome.update(V.get('nn') or {})
import re
L=[]
for it in V['it']:
    dt,sg,em,au,res,ex=it[:6];m={}
    for a,b in re.findall(r'([0-9a-n])([fcanx])',ex or ''): m[V['nm'][B.index(a)]]=b
    for k,vid in enumerate(V['nm']):
        x=m.get(vid)
        if x=='x': continue
        if x is None:
            if k>20: continue
            x='f'
        L.append([dt,sg,em,au,res,nome.get(vid,vid),AB[x]])
w('votacoes_nominais.csv',['data','proposicao','ementa','autor','resultado','vereador','voto'],L)
# indicadores
L=[]
for I in D['ind']:
    for nm,vals in I['s']:
        for y,v in zip(I['years'],vals):
            if v is not None: L.append([I['k'],I['t'],I.get('u',''),nm,y,v,I.get('src','')])
w('indicadores.csv',['codigo','indicador','unidade','local','ano','valor','fonte'],L)
# finanças
w('financas_anuais.csv',['ano','receita_corrente_rs_mi','pessoal_rs_mi','despesa_total_rs_mi','gasto_por_habitante_rs','populacao','investimento_rs_mi','educacao_rs_mi','saude_rs_mi','deflator_para_rs_2025'],[[r['y'],r.get('rec'),r.get('pes'),r.get('tot'),r.get('pc'),r.get('pop'),r.get('cap'),r.get('edu'),r.get('sau'),r.get('defl')] for r in D['fin2']])
# calendário do gasto
C=D['cal'];L=[]
for k in C['K']:
    for y,(d,e,l) in C['v'][k].items():
        for b in range(6):
            if e[b] is not None or l[b] is not None: L.append([k,y,b+1,d,e[b],l[b]])
w('gasto_bimestral_por_area.csv',['area','ano','bimestre','dotacao_atualizada_rs_mi','empenhado_acumulado_rs_mi','liquidado_acumulado_rs_mi'],L)
# pisos
P=D['piso'];w('pisos_educacao_saude.csv',['ano','area','despesa_rs_mi','receita_base_rs_mi','percentual','minimo'],[[y,'educacao',*P['mde'][y],25] for y in sorted(P['mde'])]+[[y,'saude',*P['asps'][y],15] for y in sorted(P['asps'])])
# subsídios
S=D['sal']['s'];w('subsidios.csv',['cargo','ano','valor_rs'],[[c,y,v] for c,d in S.items() for y,v in sorted(d.items())])
# contratos
X=D['ctr'];cols=X['cols'];K=X.get('K',[]);L=[]
for c in X['c']:
    r=dict(zip(cols,c));f=X['forn'][r['f']]
    L.append([r['n'],X['U'][r['u']],f[0],f[1],r['o'],r['ano'],r['v'],r['ad'],r['adp'],r['t'],X['S'][r['s']],r['fim'],K[r['k']] if K else ''])
w('contratos.csv',['contrato','orgao','fornecedor','cnpj','objeto','ano_assinatura','valor_original_rs','aditivos_total_rs','aditivos_de_prorrogacao_rs','numero_de_termos_aditivos','situacao','vencimento','tipo_de_servico'],L)
w('contratos_valor_por_ano.csv',['ano','contrato','valor_movimentado_rs'],[[y,X['c'][i][0],v] for y,i,v in X['m']])
