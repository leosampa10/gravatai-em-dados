
## Formato padrão (desde 27/11/2026, reel da Peleia)
- Começo com o Sergio em tela cheia; a partir do primeiro trecho com `site`, a tela do site fica **no topo** e o rosto vai para o **círculo** até o fim (use `"site":"mesmo"` para seguir na mesma tela).
- **Fundo desfocado** atrás do Sergio (`fundo.py`, MediaPipe Selfie Segmentation). Precisa de um Python com `mediapipe==0.10.14` e `opencv-python-headless`, passado em `REEL_PY`:
  `uv venv -p 3.10 /tmp/sp && uv pip install -p /tmp/sp/bin/python mediapipe==0.10.14 opencv-python-headless`
  `REEL_PY=/tmp/sp/bin/python NODE_PATH=$(npm root -g) python3 reel.py spec.json bruto.mp4 saida.mp4`
- `"cut": [[a,b], ...]` tira trechos do bruto (ex.: "corta essa parte", pausa para o chimarrão).
- O Sergio manda o vídeo limpo + o mesmo com legenda automática; a legenda vira a transcrição (OCR, tesseract por). Se o legendado tiver duração diferente, casar os tempos pelo envelope de áudio.
- Telas especiais em `site`: `tela` (print da tela com botões fixos; `hl` contorna um elemento), `pel` ("v"/"g": janela da Peleia), `q` (ex.: "?peleia=g0-6"), `story` (["v","a","b"]: post de story da Peleia), `img` (imagem pronta), `fixo` (sem rolagem).
- Sem música de fundo na edição (separar voz e música deixou o áudio estranho).
