import pandas as pd,re,json,datetime as dt
fix=lambda s: re.sub('[ﾀ-￿]',lambda m:chr(ord(m.group())-0xFF00),s) if isinstance(s,str) else s
df=pd.read_excel('/mnt/user-data/uploads/ef1b3a94-Relatorio.xlsx',header=None).map(fix)
H=['ug','idano','proc','lano','lnum','status','sit','tipo','tano','tid','tnum','obj','cod','cnpj','nome','ass','ini','fim','venc','valor','vad','contrato','esp','inst','x']
df=df.iloc[1:].copy();df.columns=H[:df.shape[1]]
n0=len(df)
isdate=lambda v: isinstance(v,(dt.datetime,pd.Timestamp))
good=df['status'].isin(['Encerrado','Vigente','Rescindido','Indeterminado'])&pd.to_numeric(df['valor'],errors='coerce').notna()&df['ass'].apply(isdate)
bad=df[~good];df=df[good].copy()
print('linhas',n0,'descartadas',len(bad))
df['valor']=pd.to_numeric(df['valor']);df['vad']=pd.to_numeric(df['vad'],errors='coerce').fillna(0)
def ctr(v):
    if isdate(v): return f'{v.month}/{v.year}'
    return str(v).strip().replace('"','') if pd.notna(v) else ''
df['ctr']=df['contrato'].apply(ctr)
df['orig']=df['tipo'].isna()|(df['tipo']=='Normal')
df['ano']=df['ass'].apply(lambda d:d.year)
df['mov']=df.apply(lambda r:r['valor'] if r['orig'] else r['vad'],axis=1)
UG={'MUNICÍPIO DE GRAVATAI':'Prefeitura','ISSEG - INSTITUTO DE SAUDE DOS SERVIDORES DE GRAVATAÍ':'ISSEG','INSTITUTO DE PREVIDÊNCIA DOS SERVIDORES MUNICIPAIS DE GRAVATAI - IPG':'IPG','CAMARA MUNICIPAL DE VEREADORES DE GRAVATAI':'Câmara','FUNDACAO MUNICIPAL DE MEIO AMBIENTE - FMMA':'FMMA','INSTITUTO DE PREVIDÊNCIA E ASSISTÊNCIA DOS SERVIDORES MUNICIPAIS DE GRAVATAÍ - SAÚDE':'IPG Saúde'}
df['u']=df['ug'].map(UG).fillna('Outro')
print(df['u'].value_counts().to_dict())
df['key']=df['u']+'|'+df['ctr']+'|'+df['cnpj'].astype(str)
F={};forn=[]
def fi(c,n):
    if c not in F: F[c]=len(forn);forn.append([n,c])
    return F[c]
C=[]
for k,g in df.groupby('key',sort=False):
    g=g.sort_values('ass');o=g[g['orig']]
    r0=g.iloc[0];last=g.iloc[-1]
    vo=float(o['valor'].sum()) if len(o) else None
    ad=float(g.loc[~g['orig'],'vad'].sum());adp=float(g.loc[g['tipo'].isin(['Prorrogação']),'vad'].sum())
    a0=(o['ass'].min() if len(o) else pd.to_datetime(g['ini'],errors='coerce').min())
    a0=a0 if (isdate(a0) and pd.notna(a0)) else r0['ass']
    venc=pd.to_datetime(g['venc'],errors='coerce').max()
    C.append({'n':r0['ctr'],'u':r0['u'],'f':fi(r0['cnpj'],r0['nome']),'o':re.sub(r'\s+',' ',str(r0['obj']))[:140],'a':a0.strftime('%Y-%m-%d'),'v':round(vo,2) if vo is not None else None,'ad':round(ad,2),'adp':round(adp,2),'t':int((~g['orig']).sum()),'s':str(last['status']),'e':str(r0['esp']) if pd.notna(r0['esp']) and not isdate(r0['esp']) else '','i':str(r0['inst']).replace('"','') if pd.notna(r0['inst']) else '','fim':venc.strftime('%Y-%m-%d') if pd.notna(venc) else ''})
print('contratos',len(C),'fornecedores',len(forn))
print('com valor original',sum(1 for c in C if c['v'] is not None))
# rows movement per year/forn for mandate tops
mov=df.groupby(['ano','cnpj'])['mov'].sum().reset_index()
M=[[int(r.ano),F[r.cnpj],round(float(r.mov),2)] for r in mov.itertuples() if r.cnpj in F and abs(r.mov)>0]
tot=df.groupby('ano')['mov'].sum()
print((tot/1e6).round(1).to_dict())
json.dump({'forn':forn,'c':C,'m':M,'meta':{'linhas':int(n0),'desc':int(len(bad)),'ger':'23/11/2026','prot':'7978/2026'}},open('ctr.json','w'),ensure_ascii=False,separators=(',',':'))
import os;print(os.path.getsize('ctr.json')//1024,'KB')
bad.to_csv('linhas_descartadas.csv',index=False)
