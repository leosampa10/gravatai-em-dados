# Posts "dados do site" (carrossel com vídeo)

Gera cada carrossel de 6 slides (1080×1350) a partir do PRÓPRIO site (index.html deste repositório), com prints reais e vídeos curtos do filtro em ação.

Fluxo (na pasta _tools/posts, com Playwright e ffmpeg; NODE_PATH=$(npm root -g)):
1. `capture.js` abre ../../index.html em 390×844 (dpr 3, tema escuro) e grava os quadros de uma cena.
2. `make.py` monta os slides na identidade visual (topo "GRAVATAÍ — EM DADOS", n/6, rodapé com fonte e site) e gera MP4 com ffmpeg.
3. `python3 build_post.py spec.json` → out/<slug>/: 1.jpg (capa), 2–4 (.mp4 se animado, .jpg se parado), 5.png (cobrança), 6.png (Siga).
4. `python3 gallery_section.py out/<slug>` → imprime a <section> da página "Vídeos dos posts" e grava files_<slug>.json.

Spec (ver exemplo-spec.json): slug, date, title; cap {k,t,src,scene}; slides [3× {k,t,src,scene}]; cob {title,qs[3],who,src}.
Tipos de cena (scene): {"goto":"grupo:aba","title":"^regex do h2","clipTo":".chart|.rng","maxH":px,"prep":[seletores],"anim":...}
- anim {"type":"slider"} — régua "Desde" do ano mais recente ao mais antigo
- anim {"type":"scrub","from":0..1,"to":0..1,"steps":n} — dedo passando no gráfico (tooltip)
- anim {"type":"toggle","btn":"button[data-m=pc]","after":"^título do card por habitante"} — Total → Por habitante
- anim {"type":"clicks","steps":[{"sel":"...","hold":n}]} — toques em botões do card
- anim {"type":"none"} — print parado
- modo tela inteira: {"goto":..,"view":true,"anchor":"seletor","off":px,"vh":px,"steps":[{"sel":"...","inline":true}]} — grava a tela do celular (ex.: tocar numa votação e o site rolar até ela).
- botões de série (data-k) ligam e desligam linhas em todos os cards; em Gravataí × RS × Brasil a linha de Gravataí (k=0) fica fixa.
