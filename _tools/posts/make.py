import json,subprocess,os,sys,shutil
from PIL import Image,ImageDraw
ENV=dict(os.environ,NODE_PATH=subprocess.check_output(['npm','root','-g'],text=True).strip())
FONT='<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">'
def tpl(n,kicker,title,src,body='',slotY=None):
    return f'''<!doctype html><html><head><meta charset="utf-8">{FONT}<style>body{{margin:0}}.g{{background-image:radial-gradient(rgba(236,235,228,0.06) 1.6px,transparent 1.6px);background-size:36px 36px}}</style></head><body>
<div class="g" style="width:1080px;height:1350px;box-sizing:border-box;background-color:#1D1E1A;position:relative;overflow:hidden;font-family:Poppins,sans-serif;color:#ECEBE4;padding:84px 84px 0 84px">
<div style="display:flex;align-items:center;justify-content:space-between"><div style="display:flex;align-items:center;gap:14px"><span style="font-weight:900;font-size:30px;letter-spacing:-0.02em;text-transform:uppercase">Gravataí</span><span style="width:34px;height:5px;border-radius:3px;background:#4F86C6"></span><span style="font-weight:600;font-size:20px;letter-spacing:0.3em;text-transform:uppercase;color:#A3A49B">em dados</span></div><span style="font-weight:600;font-size:24px;color:#A3A49B">{n}/6</span></div>
<div style="margin-top:56px;font-weight:700;font-size:24px;letter-spacing:0.14em;text-transform:uppercase;color:#4F86C6">{kicker}</div>
<div style="margin-top:16px;font-weight:900;font-size:58px;line-height:1.06;letter-spacing:-0.03em">{title}</div>{body}
<div style="position:absolute;left:84px;right:84px;bottom:64px;display:flex;justify-content:space-between;align-items:flex-end;gap:40px;border-top:2px solid #3A3C35;padding-top:22px"><span style="font-size:21px;line-height:1.35;color:#A3A49B;max-width:700px">{src}</span><span style="font-weight:600;font-size:22px;color:#ECEBE4;white-space:nowrap">gravataiemdados.com.br</span></div></div></body></html>'''
def render(pairs):
    args=[]
    for h,png in pairs: open(png+'.html','w').write(h); args+=[os.path.abspath(png+'.html'),os.path.abspath(png)]
    subprocess.check_call(['node','render.js']+args,env=ENV)
SLOT_W=880; SLOT_Y=430; MAXB=1180
def compose(base,fr,touch,scale_w=SLOT_W,y0=SLOT_Y,crop=None,off=0,offH=None):
    im=Image.open(base).convert('RGB'); c=Image.open(fr).convert('RGB')
    if off: c=c.crop((0,max(0,int(off*3)-24),c.width,c.height if not offH else min(c.height,max(0,int(off*3)-24)+int(offH*3)))); crop=None
    if crop: c=c.crop((0,0,c.width,min(c.height,int(crop*3))))
    k=scale_w/c.width; h=int(c.height*k)
    if y0+h>MAXB: k=(MAXB-y0)/c.height; h=MAXB-y0
    w=int(c.width*k); c=c.resize((w,h),Image.LANCZOS)
    x0=(1080-w)//2
    # rounded frame
    mask=Image.new('L',(w,h),0);ImageDraw.Draw(mask).rounded_rectangle([0,0,w-1,h-1],28,fill=255)
    d=ImageDraw.Draw(im); d.rounded_rectangle([x0-4,y0-4,x0+w+3,y0+h+3],32,fill='#3A3C35')
    im.paste(c,(x0,y0),mask)
    if touch:
        tx=x0+touch['x']*3*k; ty=y0+touch['y']*3*k; d=ImageDraw.Draw(im,'RGBA')
        d.ellipse([tx-46,ty-46,tx+46,ty+46],fill=(217,137,90,70),outline=(217,137,90,255),width=6)
        d.ellipse([tx-14,ty-14,tx+14,ty+14],fill=(217,137,90,255))
    return im
def scene(spec,outdir):
    if spec.get('img'):  # imagem pronta (print já recortado), sem captura
        return {'frames':[{'f':os.path.abspath(spec['img']),'touch':None,'hold':1}]}
    os.makedirs(os.path.dirname(outdir),exist_ok=True); json.dump(spec,open(outdir+'.json','w'))
    if os.path.exists(outdir): shutil.rmtree(outdir)
    subprocess.check_call(['node','capture.js',outdir+'.json',outdir],env=ENV)
    return json.load(open(outdir+'/meta.json'))
def video(base,meta,out,fps=30):
    tmp=out+'_f';shutil.rmtree(tmp,ignore_errors=True);os.makedirs(tmp);i=0;last=None
    for fr in meta['frames']:
        im=compose(base,fr['f'],fr['touch'],crop=fr.get('crop'))
        for _ in range(fr['hold']): im.save(f'{tmp}/{i:05d}.jpg',quality=92); i+=1
        last=im
    subprocess.check_call(['ffmpeg','-loglevel','error','-y','-framerate',str(fps),'-i',f'{tmp}/%05d.jpg','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',out])
    last.save(out.replace('.mp4','.jpg'),quality=90); shutil.rmtree(tmp)

def tpl_cob(title,qs,who,src,k='A cobrança · opinião',wl='Quem decide'):
    q=''.join(f'<div style="display:grid;grid-template-columns:76px 1fr;gap:20px;align-items:start"><span style="font-weight:900;font-size:64px;line-height:1;color:#D9895A">{i+1}</span><span style="font-weight:600;font-size:34px;line-height:1.3">{x}</span></div>' for i,x in enumerate(qs))
    body=f'<div style="margin-top:44px;display:grid;gap:24px">{q}</div><div style="margin-top:44px;border-left:8px solid #4F86C6;padding:6px 0 6px 32px"><div style="font-weight:800;font-size:34px;text-transform:uppercase">{wl}</div><div style="font-size:29px;line-height:1.35;color:#A3A49B;margin-top:10px">{who}</div></div>'
    return tpl(5,k,f'<span style="text-transform:uppercase;font-size:76px">{title}</span>',src,body=body)

def build(P):
    D='out/'+P['slug'];shutil.rmtree(D,ignore_errors=True);os.makedirs(D)
    json.dump({"date":P['date'],"title":P['title']},open(D+'/post.json','w'),ensure_ascii=False)
    metas={}
    pairs=[(tpl(1,P['cap']['k'],P['cap']['t'],P['cap']['src']),D+'/b1.png')]
    for n,sl in enumerate(P['slides'],start=2):
        pairs.append((tpl(n,sl['k'],sl['t'],sl['src']),D+f'/b{n}.png'))
    c=P['cob'];pairs.append((tpl_cob(c['title'],c['qs'],c['who'],c['src'],c.get('k','A cobrança · opinião'),c.get('wl','Quem decide')),D+'/5.png'))
    render(pairs)
    subprocess.check_call(['node','render.js',os.path.abspath('siga6.html'),os.path.abspath(D+'/6.png')],env=ENV)
    if P['cap'].get('capa'):  # capa nova (cartaz colorido): card do site em tema claro
        import capa, datetime, glob
        c=P['cap']['capa']
        if not c.get('cor'):  # mescla as cores: muda a cada dia e entre os posts do mesmo dia
            d=datetime.datetime.strptime(P['date'],'%d/%m/%Y').date()
            ja=len([x for x in glob.glob('out/'+P['slug'][:8]+'-*') if not x.endswith(P['slug'])])
            c['cor']=capa.ORDEM[(d.toordinal()*2+ja)%len(capa.ORDEM)]
        sc=dict(P['cap']['scene'],light=True,anim={'type':'none'})
        m=scene(sc,f'fr/{P["slug"]}-1')
        render([(capa.html(P['cap'],m['frames'][-1]['f'],off=m.get('off',0)),D+'/1.png')])
        from PIL import Image as _I;_I.open(D+'/1.png').convert('RGB').save(D+'/1.jpg',quality=92);os.remove(D+'/1.png')
    else:
        m=scene(P['cap']['scene'],f'fr/{P["slug"]}-1')
        f=m['frames'][-1];compose(D+'/b1.png',f['f'],None,y0=P['cap'].get('y0',560),crop=f.get('crop')).save(D+'/1.jpg',quality=92)
    for n,sl in enumerate(P['slides'],start=2):
        m=scene(sl['scene'],f'fr/{P["slug"]}-{n}')
        if len(m['frames'])==1 or (not sl['scene'].get('view') and sl['scene'].get('anim',{}).get('type','none')=='none'):
            f=m['frames'][-1];compose(D+f'/b{n}.png',f['f'],None,crop=f.get('crop'),off=m.get('off',0),offH=m.get('offH')).save(D+f'/{n}.jpg',quality=92)
        else: video(D+f'/b{n}.png',m,D+f'/{n}.mp4')
    print('built',P['slug'])
