# uso: python3 gallery_section.py out/<slug>  -> imprime o <section> da página "Vídeos dos posts" e grava files_<slug>.json para publish_files
import json,os,sys
from PIL import Image
d=sys.argv[1].rstrip('/')+'/';slug=os.path.basename(d.rstrip('/'));m=json.load(open(d+'post.json'))
items=[]
for i in range(1,7):
    for ext in ['mp4','jpg','png']:
        f=f'{d}{i}.{ext}'
        if os.path.exists(f):
            if ext=='png': Image.open(f).convert('RGB').save(f'{d}{i}.jpg',quality=92);ext='jpg'
            items.append((i,ext));break
H=[f'<section id="{slug}"><div class="d">{m["date"]}</div><h2>{m["title"]}</h2><div class="row">']
files=[]
for i,ext in items:
    src=f'v/{slug}/{i}.{ext}'
    media=f'<video src="{src}" poster="v/{slug}/{i}p.jpg" muted loop playsinline controls preload="metadata"></video>' if ext=='mp4' else f'<img src="{src}" alt="Slide {i}" loading="lazy">'
    H.append(f'<div class="it">{media}<a href="{src}" target="_blank" rel="noopener">Slide {i} · {"vídeo" if ext=="mp4" else "imagem"} ↗</a></div>')
    files.append({"as":src,"path":os.path.abspath(f'{d}{i}.{ext}')})
    if ext=='mp4': files.append({"as":f"v/{slug}/{i}p.jpg","path":os.path.abspath(f'{d}{i}.jpg')})
H.append('</div></section>')
json.dump(files,open(f'files_{slug}.json','w'))
print('\n'.join(H))
