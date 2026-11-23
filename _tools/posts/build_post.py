# uso: python3 build_post.py spec.json  -> gera out/<slug>/ (1.jpg, 2-4 .mp4 ou .jpg, 5.png, 6.png)
import json,sys
from make import build
for f in sys.argv[1:]:
    build(json.load(open(f)))
