import json,re,unicodedata,collections
d=json.load(open('ctr_min.json'))
if d['cols'][-1]=='k':
    d['cols'].pop();[c.pop() for c in d['c']]
n=lambda t:unicodedata.normalize('NFD',t).encode('ascii','ignore').decode().lower()
K=[('Aluguel de imóveis',r'locacao necessaria|locacao de imovel|locacao do imovel|aluguel|imovel|sala comercial|instalacao (da|do|dos|das) (secretaria|setor|program|centro|caps|unidade)'),
('Saúde: hospitais e serviços médicos',r'hospital|santa casa|medic|saude|clinic|laborat|exame|upa\b|samu|ambulanc|enferm|odonto|farmac|leito|terapeut|psiq|fisioter|hemodial|consulta|cirurg|oxigen|ortes|protes|internac|psicolog|esteriliz|liminar|paciente|vacina|dentar'),
('Limpeza urbana e lixo',r'limpeza urbana|residuo|lixo|coleta|varri|capina|aterro|rocad|rocagem|reciclag|conteiner|cemit|ecoponto|destinacao final'),
('Limpeza, cozinha e apoio terceirizado',r'\basg\b|cozinh|limpeza|servicos gerais|apoio administrativo|recepc|zelad|copeir|mao de obra|terceiriz'),
('Obras, vias e pavimentação',r'pavimenta|asfalt|obra|constru|reforma|drenag|recapea|ponte|calcament|engenharia|ampliac|edificac|terraplen|duplicac|ppci|projeto executivo|sinaliza|malha viaria|\bvias\b|pluvia|recuperacao estrutural|espacos recreativos|emei|revitaliza|praca'),
('Transporte, veículos e frota',r'veicul|motorista|transporte|onibus|frota|combust|caminh|maquina|locacao de (equip|veic)|pneu|retroescav'),
('Educação e merenda',r'escola|educa|ensino|aluno|merenda|aliment escolar|creche|pedagog|livro|didatic|uniforme|senac|senai|aprendizag'),
('Assistência social, cultura e OSCs',r'oficin|\bosc|organizacao da sociedade civil|associacao|assistenc|acolhimento|acolher|abrigo|idoso|crianca|adolesc|vulnerab|fomento|colaborac|cultural|esport|projeto social|residencia inclusiva'),
('Tecnologia, sistemas e telefonia',r'software|sistema|informat|tecnolog|internet|\blink|telefon|telecomunic|impressora|computador|licenca|dados|e-mail|hospedag|relogio'),
('Alimentação e compra de bens',r'aliment|refeic|lanche|genero|material|aquisic|fornecimento de'),
('Iluminação e energia',r'ilumina|energia|eletric|semafor|lampad'),
('Publicidade e comunicação',r'publicidade|propaganda|marketing|divulga|grafica|publicac|jornal|radio'),
('Vigilância e segurança',r'vigilan|seguranca|monitorament|cameras|portaria'),
('Concursos, eventos, seguros e consultorias',r'seguro|consultor|assessor|auditor|capacitac|treinament|concurso|evento|passage|correspond|lavanderia|manutenc')]
cats=[];cnt=collections.Counter();val=collections.Counter()
for c in d['c']:
    k=len(K)
    for t in (n(c[3]),n(d['forn'][c[2]][0])):
        for i,(nm,rx) in enumerate(K):
            if re.search(rx,t): k=i;break
        if k<len(K): break
    cats.append(k);cnt[k]+=1;val[k]+=(c[5] or 0)+c[6]
names=[k[0] for k in K]+['Outros serviços']
for k in sorted(cnt,key=lambda k:-val[k]): print(names[k],cnt[k],round(val[k]/1e6))
d['K']=names;d['cols'].append('k')
for c,k in zip(d['c'],cats): c.append(k)
json.dump(d,open('ctr_min.json','w'),ensure_ascii=False,separators=(',',':'))
# sample outros
import random;random.seed(1)
print([c[3][:60] for c,k in zip(d['c'],cats) if k==len(K)][:25])
