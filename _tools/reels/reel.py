"""Monta um reel no formato Gravataí em dados a partir do vídeo gravado pelo Sergio.

uso: NODE_PATH=$(npm root -g) python3 reel.py spec.json bruto.mp4 saida.mp4

spec.json:
{
 "beats": [                      # a fala, na ordem do roteiro (uma frase ou trecho por item)
   {"t": "Tua conta de água vai subir em janeiro", "hook": true, "key": ["janeiro"]},   # 1º = gancho (caixas grandes)
   {"t": "A Corsan vai reajustar a tarifa em 4,63%", "key": ["reajustar","4,63%"]},
   {"t": "Olha no site: a CPI contou 965 interrupções", "key": ["965"],
    "site": {"goto": "camara:c-fis", "anchor": "#c-a-unica-cpi-do-periodo-investiga", "label": "No site · Câmara › Fiscalização", "steps": []}},
   {"t": "...", "card": {"t": "Só dado <i>oficial</i>", "sub": "Sem nota, sem ranking.", "chips": ["Câmara","TCE-RS","Tesouro"]}}
 ],
 "end": {"cta": "Link no perfil · manda pra quem mora aqui"}
}
- Os silêncios maiores que 0,45 s são cortados (cortes secos, como no formato de referência).
- A legenda sai do texto do roteiro, em blocos de até 3 palavras; as palavras de "key" ganham caixa (ocre e azul, alternando).
- "site": grava o site (tema claro, tela de celular) com o filtro em ação; o vídeo do Sergio vai para o fundo desfocado e para o círculo.
- "card": cartão branco por cima da fala, com os selos aparecendo um a um.
"""
import json, os, re, subprocess, sys, shutil, tempfile, math
HERE = os.path.dirname(os.path.abspath(__file__)); POSTS = os.path.join(HERE, '..', 'posts')
W, H, FPS = 1080, 1920, 30
ENV = dict(os.environ, NODE_PATH=subprocess.check_output(['npm', 'root', '-g'], text=True).strip())
def sh(*a): subprocess.check_call(list(a), env=ENV)
def probe(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).strip())

def speech(f, mind=0.45):
    """Blocos de fala pelo volume (limiar adaptativo ao ruído do ambiente)."""
    import numpy as np
    raw = subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(float)/32768; w=800; n=len(a)//w
    db = 20*np.log10(np.sqrt((a[:n*w].reshape(n,w)**2).mean(1))+1e-9); thr = np.percentile(db,10)+5
    sp = db > thr; T = probe(f); dt = w/16000; segs=[]; i=0
    while i < n:
        if sp[i]:
            j=i
            while j < n and (sp[j] or (j+1 < n and not all(not x for x in sp[j:j+int(mind/dt)]) )): j+=1
            segs.append((max(0,i*dt-0.10), min(T,j*dt+0.14))); i=j
        else: i+=1
    out=[]
    for s_,e_ in segs:
        if out and s_-out[-1][1] < 0.05: out[-1]=(out[-1][0],e_)
        elif e_-s_ > 0.2: out.append((s_,e_))
    return out or [(0,T)]

def remap(t, segs):
    """tempo do bruto -> tempo do vídeo cortado"""
    acc=0
    for a,b in segs:
        if t < a: return acc
        if t <= b: return acc+(t-a)
        acc += b-a
    return acc

def chunks(t):
    ws=t.split(); out=[]; cur=[]
    for w in ws:
        cur.append(w)
        if len(cur)==3 or re.search(r'[.,;:!?]$',w) or (len(cur)==2 and len(' '.join(cur))>16): out.append(cur); cur=[]
    if cur: out.append(cur)
    return out

CSS = '''*{box-sizing:border-box}body{margin:0;background:transparent;font-family:Poppins}#r{position:relative;width:1080px;height:1920px}
.cap{position:absolute;left:40px;right:40px;top:1460px;text-align:center;font:900 76px/1.2 Poppins;color:#fff;text-transform:uppercase;text-shadow:0 3px 12px rgba(0,0,0,.55)}
.cap.lo{top:1440px}
.band{position:absolute;left:0;right:0;top:1250px;bottom:0;background:linear-gradient(rgba(14,14,13,0),rgba(14,14,13,1) 130px,rgba(14,14,13,1))}
.k{padding:2px 16px;border-radius:6px;text-shadow:none}.ky{background:#F2CE6E;color:#1D1E1A}.kb{background:#2F78C4;color:#fff}
.hook{position:absolute;left:60px;right:60px;top:230px;text-align:center}
.hook span{display:inline-block;background:#1D1E1A;color:#fff;font:900 86px/1 Poppins;text-transform:uppercase;padding:12px 22px 6px;margin:6px 0;letter-spacing:-.02em}
.hook span.y{background:#F2CE6E;color:#1D1E1A;font-size:108px}
.hd{position:absolute;right:36px;top:760px;text-align:center;color:#fff;font:600 17px Poppins;letter-spacing:.06em;opacity:.9;text-shadow:0 1px 4px rgba(0,0,0,.5)}
.hd svg{display:block;margin:0 auto 8px}
.pill{position:absolute;left:50%;top:130px;transform:translateX(-50%);background:#2F78C4;color:#fff;font:800 30px Poppins;padding:10px 26px;border-radius:999px;white-space:nowrap}
.phone{position:absolute;left:50%;top:180px;transform:translateX(-50%);width:572px;height:1204px;border-radius:58px;border:14px solid #fff;box-shadow:0 0 0 2px rgba(0,0,0,.08)}
.ring{position:absolute;right:110px;top:1080px;width:266px;height:266px;border-radius:50%;border:8px solid #fff;box-shadow:0 10px 30px rgba(0,0,0,.4)}
.card{position:absolute;left:90px;right:90px;top:200px;background:#fff;border-radius:22px;padding:34px 40px 30px;box-shadow:0 20px 60px rgba(0,0,0,.35)}
.card .rule{height:8px;border-radius:4px;background:linear-gradient(90deg,#2F78C4 0 25%,#c2455a 25% 45%,#b07a12 45% 65%,#7a5ccc 65% 82%,#2e8f6d 82%);margin-bottom:22px}
.card h3{margin:0;font:900 72px/1 Poppins;text-transform:uppercase;letter-spacing:-.04em;color:#1D1E1A}.card h3 i{font-weight:800;text-transform:none}
.card p{margin:10px 0 18px;font:400 30px/1.3 Poppins;color:#41443a}
.chips span{display:inline-block;background:#2F78C4;color:#fff;font:800 30px Poppins;border-radius:999px;padding:8px 22px;margin:0 8px 10px 0}
.end{position:absolute;inset:0;background:#f8f8f6;color:#1D1E1A}
.end .brand{position:absolute;left:0;right:0;top:600px;text-align:center}
.end .url{position:absolute;left:0;right:0;top:860px;text-align:center;font:900 68px Poppins;letter-spacing:-.04em}
.end .sub{position:absolute;left:0;right:0;top:980px;text-align:center;font:400 34px/1.3 Poppins;color:#41443a}
.end .cta{position:absolute;left:50%;top:1090px;transform:translateX(-50%);background:#1D1E1A;color:#fff;font:700 32px Poppins;padding:16px 34px;border-radius:999px;white-space:nowrap}
.end svg.m{position:absolute;left:0;bottom:0;width:1080px;height:330px}'''
IG='<svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="#fff"/></svg>'

def esc(s): return s.replace('&','&amp;').replace('<','&lt;')
def norm(w): return re.sub(r'[^\wÀ-ú%,]','',w.lower()).strip(',')

def cap_html(words, keys, color, lo):
    ks={norm(k) for k in keys}
    out=' '.join(f'<span class="k {color}">{esc(w)}</span>' if norm(w) in ks else esc(w) for w in words)
    return f'<div class="cap{" lo" if lo else ""}">{out}</div>'

def main(specf, raw, out):
    S=json.load(open(specf)); tmp=tempfile.mkdtemp(prefix='reel_'); B=S['beats']
    # 1) cortes secos nos silêncios + enquadramento 1080x1920
    segs=speech(raw)
    vf=f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1'+(''.join(f',delogo=x={m[0]}:y={m[1]}:w={m[2]}:h={m[3]}' for m in S.get('mask',[])))
    lst=open(f'{tmp}/cut.txt','w')
    for k,(a,b) in enumerate(segs):
        # 'voz': trilha só de voz (música separada) no lugar do áudio do bruto; os cortes seguem o bruto
        voz=['-ss',f'{a:.3f}','-i',S['voz'],'-map','0:v','-map','1:a'] if S.get('voz') else []
        sh('ffmpeg','-v','error','-y','-ss',f'{a:.3f}','-i',raw,*voz,'-t',f'{b-a:.3f}','-vf',vf,'-af','aresample=48000','-c:v','libx264','-preset','veryfast','-crf','18','-c:a','aac','-b:a','160k','-ar','48000','-ac','2',f'{tmp}/seg{k:03d}.mp4')
        lst.write(f"file '{tmp}/seg{k:03d}.mp4'\n")
    lst.close(); cut=f'{tmp}/cut.mp4'
    sh('ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{tmp}/cut.txt','-c','copy',cut)
    segs=[(a,a+probe(f'{tmp}/seg{k:03d}.mp4')) for k,(a,b) in enumerate(segs)]
    T=probe(cut)
    # 2) tempo de cada trecho: um trecho por bloco de fala quando bate; senão, proporcional ao tamanho do texto
    lens=[b-a for a,b in segs]
    if all('a' in b for b in B):
        tim=[(remap(b['a'],segs),remap(b['b'],segs)) for b in B]
    elif len(segs)==len(B):
        t0=0;tim=[]
        for L in lens: tim.append((t0,t0+L)); t0+=L
    else:
        cs=[max(len(b['t']),4) for b in B]; tot=sum(cs); t0=0; tim=[]
        for c in cs: d=T*c/tot; tim.append((t0,t0+d)); t0+=d
    # 3) camadas em PNG
    items=[]; ov=[]  # ov: (png, a, b)
    items.append((f'<div class="hd">{IG}@GRAVATAIEMDADOS</div>', f'{tmp}/hd.png'))
    if S.get('band'): items.append(('<div class="band"></div>', f'{tmp}/band.png'))
    sites=[]
    for i,(bt,(a,b)) in enumerate(zip(B,tim)):
        color='ky' if i%2==0 else 'kb'; lo=bool(bt.get('site'))
        if bt.get('hook'):
            ws=bt['t'].split(); ks={norm(k) for k in bt.get('key',[])}; lines=[];cur=[]
            for w in ws:
                if norm(w) in ks:
                    if cur: lines.append(('',cur)); cur=[]
                    lines.append(('y',[w]))
                else:
                    cur.append(w)
                    if len(' '.join(cur))>16: lines.append(('',cur)); cur=[]
            if cur: lines.append(('',cur))
            h='<div class="hook">'+'<br>'.join(f'<span class="{c}">{esc(" ".join(l))}</span>' for c,l in lines)+'</div>'
            p=f'{tmp}/b{i}h.png'; items.append((h,p)); ov.append((p,a,b)); continue
        ch=chunks(re.sub(r'\b(eh|âh|ah|hum)\b,?\s*','',bt['t'],flags=re.I)); cl=[max(len(' '.join(c)),3) for c in ch]; tot=sum(cl); t=a
        for j,c in enumerate(ch):
            d=(b-a)*cl[j]/tot; p=f'{tmp}/b{i}c{j}.png'; items.append((cap_html(c,bt.get('key',[]),color,lo),p)); ov.append((p,t,t+d)); t+=d
        if bt.get('card'):
            C=bt['card']; n=len(C.get('chips',[])); 
            for k in range(n+1):
                chips=''.join(f'<span>✓ {esc(x)}</span>' for x in C.get('chips',[])[:k])
                p=f'{tmp}/b{i}k{k}.png'
                items.append((f'<div class="card"><div class="rule"></div><h3>{C["t"]}</h3><p>{esc(C.get("sub",""))}</p><div class="chips">{chips}</div></div>',p))
                ka=a+(b-a)*k/(n+1) if n else a; ov.append((p,ka,b if k==n else a+(b-a)*(k+1)/(n+1)))
        if bt.get('site'):
            st=bt['site']; p=f'{tmp}/b{i}s.png'
            items.append((f'<div class="pill">{esc(st.get("label","No site"))}</div><div class="phone"></div><div class="ring"></div>',p))
            sites.append((i,a,b,st,p))
    # fechamento
    G=json.load(open(os.path.join(POSTS,'geo.json')))
    cs_=re.findall(r'<circle[^>]*>',G['mark']); mark=''.join(c if c.endswith('/>') else c+'</circle>' for c in cs_)
    d=re.search(r'<path d="(M0 132[^"]*)"',G['ita']).group(1)
    E=S.get('end',{})
    items.append((f'<div class="end"><div class="brand"><svg viewBox="-4 -4 208 114" width="230" height="127" fill="#1D1E1A">{mark}</svg><div style="font:800 40px Poppins;letter-spacing:.14em;margin-top:18px">GRAVATAÍ <span style="color:#2F78C4;font-size:28px;letter-spacing:.1em">— EM DADOS</span></div></div><div class="url">GRAVATAIEMDADOS.COM.BR</div><div class="sub">{E.get("sub","Dado oficial, com fonte, de graça.<br>Câmara, Prefeitura e o teu bairro.")}</div><div class="cta">{esc(E.get("cta","Link no perfil · manda pra quem mora aqui"))}</div><svg class="m" viewBox="0 0 1168 140" preserveAspectRatio="none"><path d="{d} L1168 140 L0 140 Z" fill="#ebe6d6"/><path d="{G["rio"]}" transform="translate(0 112) scale(.974 1.3)" fill="rgba(47,120,196,.5)"/></svg></div>',f'{tmp}/end.png'))
    json.dump({'css':CSS,'items':items},open(f'{tmp}/jobs.json','w'))
    sh('node',os.path.join(HERE,'overlays.js'),f'{tmp}/jobs.json')
    # 4) gravação do site (tema claro, tela inteira de celular)
    for i,a,b,st,_ in sites:
        png=f'{tmp}/s{i}.png'
        hh=int(subprocess.check_output(['node',os.path.join(HERE,'sitecap.js'),json.dumps({k:st[k] for k in st if k!='label'}),png],env=ENV,text=True).strip().split()[-1])
        # tela do celular 544x1176; o print (390 px de largura) vira 544 px e desce devagar
        sc=544/390; ph=int(hh*sc); pan=max(0,ph-1176); dur=max(b-a,0.5)
        sh('ffmpeg','-v','error','-y','-loop','1','-framerate',str(FPS),'-t',f'{dur:.3f}','-i',png,'-vf',f"scale=544:{ph},crop=544:1176:0:'min({pan},{pan}*max(0,t-0.6)/{max(dur-1.2,0.5):.3f})',format=yuv420p",'-c:v','libx264','-preset','veryfast','-crf','18',f'{tmp}/s{i}.mp4')
    # 5) composição
    ins=['-i',cut]; fc=[]; lab='[0:v]'; n=1
    def en(a,b): return f"enable='between(t,{a:.3f},{b:.3f})'"
    if sites:
        fc.append(f'[0:v]split=3[base][bl0][fc0]')
        fc.append(f'[bl0]boxblur=24:2,eq=brightness=-0.18[blur]')
        fc.append(f'[fc0]crop=iw*0.8:iw*0.8:iw*0.1:ih*0.25,scale=250:250,format=yuva420p,geq=lum=\'p(X,Y)\':cb=\'p(X,Y)\':cr=\'p(X,Y)\':a=\'if(lte(hypot(X-125,Y-125),125),255,0)\'[face]')
        fc.append('[face]split='+str(len(sites))+''.join(f'[fa{k}]' for k in range(len(sites))))
        fc.append('[blur]split='+str(len(sites))+''.join(f'[bl{k+1}]' for k in range(len(sites))))
        lab='[base]'
        for k,(i,a,b,st,png) in enumerate(sites):
            ins+=['-i',f'{tmp}/s{i}.mp4']; sv=n; n+=1
            ins+=['-i',png]; pv=n; n+=1
            fc.append(f'{lab}[bl{k+1}]overlay=0:0:{en(a,b)}[x{k}a]')
            fc.append(f'[{sv}:v]setpts=PTS-STARTPTS+{a:.3f}/TB[sv{k}]')
            fc.append(f'[x{k}a][sv{k}]overlay=268:{180+14}:eof_action=pass:{en(a,b)}[x{k}b]')
            fc.append(f'[x{k}b][{pv}:v]overlay=0:0:{en(a,b)}[x{k}c]')
            fc.append(f'[x{k}c][fa{k}]overlay={W-110-8-258}:{1080+8}:{en(a,b)}[x{k}]')
            lab=f'[x{k}]'
    ins+=['-loop','1','-i',f'{tmp}/hd.png']; hv=n; n+=1
    fc.append(f'{lab}[{hv}:v]overlay=0:0:shortest=1[h0]'); lab='[h0]'
    if S.get('band'):
        ins+=['-i',f'{tmp}/band.png']; cond='+'.join(f'between(t,{a:.3f},{b:.3f})' for _,a,b,_,_ in sites) or '0'
        fc.append(f"{lab}[{n}:v]overlay=0:0:enable='not({cond})'[bd]"); lab='[bd]'; n+=1
    for j,(p,a,b) in enumerate(ov):
        ins+=['-i',p]; fc.append(f'{lab}[{n}:v]overlay=0:0:{en(a,b)}[o{j}]'); lab=f'[o{j}]'; n+=1
    fc.append(f"{lab}drawbox=x=0:y=0:w='{W}*t/{T:.3f}':h=10:color=0xF2CE6E:t=fill[vf]")
    body=f'{tmp}/body.mp4'
    sh('ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fc),'-map','[vf]','-map','0:a','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t',f'{T:.3f}',body)
    endv=f'{tmp}/end.mp4'
    sh('ffmpeg','-v','error','-y','-loop','1','-t','2.5','-i',f'{tmp}/end.png','-f','lavfi','-t','2.5','-i','anullsrc=r=48000:cl=stereo','-vf',f'format=yuv420p,fps={FPS}','-c:v','libx264','-preset','veryfast','-c:a','aac','-shortest',endv)
    sh('ffmpeg','-v','error','-y','-i',body,'-i',endv,'-filter_complex','[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]','-map','[v]','-map','[a]','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',out if not S.get('musica') else f'{tmp}/semmus.mp4')
    if S.get('musica'):
        # música de fundo contínua (sem os cortes da fala), com fade no fim
        M=S['musica']; D=probe(f'{tmp}/semmus.mp4'); v=M.get('vol',1.0)
        sh('ffmpeg','-v','error','-y','-i',f'{tmp}/semmus.mp4','-stream_loop','-1','-i',M['src'],'-filter_complex',
           f'[1:a]aresample=48000,atrim=0:{D:.3f},volume={v},afade=t=out:st={D-2:.3f}:d=2[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]',
           '-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',out)
    print('ok',out,f'{T+2.5:.1f}s', 'blocos de fala:',len(segs),'trechos:',len(B))
    shutil.rmtree(tmp,ignore_errors=True)

if __name__=='__main__': main(*sys.argv[1:4])
