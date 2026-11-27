"""Desfoca o fundo do vídeo (mantém a pessoa nítida). Segmentação: MediaPipe Selfie Segmentation.
uso: python fundo.py entrada.mp4 saida.mp4 [blur=45]
precisa de python com mediapipe==0.10.14 e opencv (ver README); o reel.py chama com $REEL_PY."""
import sys, subprocess, numpy as np, cv2, mediapipe as mp
src, out = sys.argv[1], sys.argv[2]; K = int(sys.argv[3]) if len(sys.argv) > 3 else 45
info = subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_entries','stream=width,height,r_frame_rate','-of','csv=p=0',src],text=True).strip().split(',')
W, H = int(info[0]), int(info[1]); fr = info[2]
dec = subprocess.Popen(['ffmpeg','-v','error','-i',src,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',fr,'-i','-','-i',src,'-map','0:v','-map','1:a?',
                        '-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','copy',out],stdin=subprocess.PIPE)
seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0)
prev = None; n = W*H*3
while True:
    buf = dec.stdout.read(n)
    if len(buf) < n: break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    m = seg.process(f).segmentation_mask
    prev = m if prev is None else 0.6*m + 0.4*prev          # suaviza no tempo (menos tremido)
    a = np.clip((prev - 0.35) / 0.3, 0, 1)
    a = cv2.GaussianBlur(a, (0, 0), 3)[..., None]
    small = cv2.resize(f, (W//4, H//4)); bg = cv2.resize(cv2.GaussianBlur(small, (0, 0), K/4), (W, H))
    enc.stdin.write((f*a + bg*(1-a)).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.wait()
