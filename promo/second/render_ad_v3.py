#!/usr/bin/env python3
"""Voice-locked V3 Tahdiri ad, drawn at 540x960 and encoded via FFmpeg skill."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math, subprocess
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parents[1]
WORK=Path.home()/'work-tools'/'tahdiri-ad02-v3'; FRAMES=WORK/'frames-final2'
W,H,FPS,DURATION=540,960,30,26
FONT='/system/fonts/NotoNaskhArabicUI-Regular.ttf'; BOLD='/system/fonts/NotoNaskhArabicUI-Bold.ttf'
if not Path(FONT).exists(): FONT='/system/fonts/NotoNaskhArabic-Regular.ttf'
if not Path(BOLD).exists(): BOLD=FONT
INK=(239,247,245); MUTED=(176,192,189); TEAL=(85,212,196); GOLD=(224,165,38); CACHE={}
def font(sz,b=False):
 k=(sz,b)
 if k not in CACHE: CACHE[k]=ImageFont.truetype(BOLD if b else FONT,sz)
 return CACHE[k]
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def txt(d,xy,s,sz,c=INK,b=False,anchor='mm'):
 d.text(xy,s,font=font(sz,b),fill=c,anchor=anchor,direction='rtl',language='ar',stroke_width=1,stroke_fill=(5,13,14,175))
def base():
 im=Image.new('RGBA',(W,H)); p=im.load()
 for y in range(H):
  for x in range(W):
   v=max(0,1-math.sqrt(((x-W*.5)/(W*.82))**2+((y-H*.43)/(H*.72))**2)); p[x,y]=(16+int(2*v),23+int(17*v),25+int(15*v),255)
 return im
BG=base()
class Stream:
 def __init__(self,path): self.p=subprocess.Popen(['/data/data/com.termux/files/usr/bin/ffmpeg','-hide_banner','-loglevel','error','-i',str(path),'-f','rawvideo','-pix_fmt','rgb24','-vsync','0','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 def get(self):
  b=self.p.stdout.read(W*H*3)
  if len(b)!=W*H*3:return None
  im=ImageEnhance.Brightness(Image.frombytes('RGB',(W,H),b).convert('RGBA')).enhance(.73)
  return Image.alpha_composite(im,Image.new('RGBA',(W,H),(4,19,22,35)))
 def close(self): self.p.stdout.close(); self.p.wait()
def make_vignette():
 sh=Image.new('RGBA',(W,H)); p=sh.load()
 for y in range(H):
  for x in range(W):
   r=math.sqrt(((x-W/2)/(W*.73))**2+((y-H/2)/(H*.68))**2); p[x,y]=(0,0,0,int(max(0,min(1,(r-.48)*90))))
 return sh
VIGNETTE=make_vignette()
def vignette(im): return Image.alpha_composite(im,VIGNETTE)
def glow(im,xy,r,col,a=80):
 g=Image.new('RGBA',(W,H)); ImageDraw.Draw(g).ellipse((xy[0]-r,xy[1]-r,xy[0]+r,xy[1]+r),fill=(*col,a)); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(r*.62)))
def titles(im,lines,y,p,sizes):
 d=ImageDraw.Draw(im)
 for i,s in enumerate(lines):
  q=ease(max(0,min(1,(p-i*.15)/.4))); txt(d,(W//2,y+i*58+int((1-q)*10)),s,sizes[i],TEAL if i==len(lines)-1 else INK,True)
def app(im,mode,t,p):
 """Product surfaces reconstructed from real app labels, not literal screenshots."""
 a=Image.new('RGBA',(392,610),(0,0,0,0)); d=ImageDraw.Draw(a)
 d.rounded_rectangle((8,8,384,602),radius=28,fill=(18,29,32,246),outline=(85,212,196,130),width=2); d.rounded_rectangle((19,19,373,591),radius=23,outline=(255,255,255,17),width=1)
 txt(d,(196,55),'تحضيري',27,INK,True); d.line((52,83,340,83),fill=(85,212,196,115),width=2)
 if mode=='summary':
  txt(d,(196,130),'ملخصاتي',25,TEAL,True); txt(d,(196,184),'مكتبة المواد',20,INK,True); txt(d,(196,225),'ملخص الدرس',21,INK,True)
  for yy,label in [(285,'التعاريف'),(344,'التعاليل'),(403,'المقارنات'),(462,'القوانين')]: txt(d,(327,yy),label,19,MUTED,False,'rm'); d.line((73,yy+19,335,yy+19),fill=(52,68,72,170),width=1)
  txt(d,(196,540),'من الكتاب الدراسي',17,(244,209,126))
 elif mode=='questions':
  txt(d,(196,132),'مكتبة الوزاريات',23,TEAL,True); txt(d,(196,212),'منسوب للوزاري',22,INK,True); d.rounded_rectangle((89,255,303,302),radius=23,fill=(77,56,22,150),outline=(224,165,38,155),width=1); txt(d,(196,279),'غير متحقق',20,(244,209,126),True); txt(d,(196,355),'بانتظار مراجعة المصدر',17,MUTED); txt(d,(196,389),'والسنة والدور',17,MUTED)
 else:
  if mode=='review':
   txt(d,(196,132),'المراجعة الذكية',23,TEAL,True); txt(d,(196,207),'مراجعة الصفحة',21,INK,True); txt(d,(196,255),'اختبار قصير',19,MUTED); d.line((85,293,307,293),fill=(52,68,72,190),width=1); txt(d,(196,354),'تقدّمي',24,TEAL,True)
   for yy,label in [(418,'مهام منجزة'),(468,'صفحات مدروسة'),(518,'اختبارات')]: txt(d,(196,yy),label,19,INK)
   txt(d,(196,559),'بياناتك على جهازك',15,MUTED)
  else:
   txt(d,(196,133),'رحلتك الدراسية',22,TEAL,True)
   for i,label in enumerate(['ملخصاتي','مكتبة الوزاريات','المراجعة','تقدّمي']):
    yy=214+i*82; txt(d,(196,yy),label,21,TEAL if i==3 else INK,True)
    if i<3:d.line((94,yy+30,298,yy+30),fill=(52,68,72,170),width=1)
 a=a.rotate(1.2*math.sin(t*.72),resample=Image.Resampling.BICUBIC,expand=True); k=.93+.05*ease(p); a=a.resize((int(a.width*k),int(a.height*k)),Image.Resampling.LANCZOS)
 shal=a.getchannel('A').filter(ImageFilter.GaussianBlur(18)); sh=Image.new('RGBA',a.size,(0,0,0,160)); sh.putalpha(shal.point(lambda x:int(x*.65))); x=(W-a.width)//2+int(math.sin(t*.48)*11); y=248+int((1-ease(p))*35); im.alpha_composite(sh,(x+13,y+24)); im.alpha_composite(a,(x,y))
def render(t,photo,logo):
 im=BG.copy()
 if t<2.72:
  im=vignette(photo or BG.copy()); ImageDraw.Draw(im,'RGBA').rectangle((0,0,W,278),fill=(8,15,17,118)); titles(im,['كل رحلة عظيمة','تبدأ بخطوة'],142,ease(t/.55),[40,46]); glow(im,(276,713),208,(224,165,38),25)
  if t>2.35:
   a=int(105*ease((t-2.35)/.37)); im=Image.alpha_composite(im,Image.new('RGBA',(W,H),(5,20,22,a)))
 elif t<5.92:
  im=vignette(photo or BG.copy()); p=(t-2.72)/3.2; titles(im,['وكل مستقبل تحلم به','يبدأ من صفحة'],153,ease(p/.35),[35,46]); glow(im,(406-int(250*ease(p)),583),180,TEAL,int(24+42*math.sin(math.pi*p))); d=ImageDraw.Draw(im,'RGBA'); x=430-int(250*ease(p)); d.line((x,360,x-28,762),fill=(85,212,196,105),width=2)
  if p>.73:
   a=int(165*ease((p-.73)/.27)); im=Image.alpha_composite(im,Image.new('RGBA',(W,H),(12,24,26,a)))
 elif t<8.32:
  p=(t-5.92)/2.4; glow(im,(270,467),262,TEAL,24); titles(im,['لكن التفوق','ليس مجرد دراسة'],398,ease(p/.3),[48,42]); d=ImageDraw.Draw(im,'RGBA'); w=int(178*ease(max(0,(p-.23)/.42))); d.line((270-w,520,270+w,520),fill=(85,212,196,145),width=2)
 elif t<11.2:
  p=(t-8.32)/2.88; d=ImageDraw.Draw(im,'RGBA'); labels=['فهم','مراجعة','استعداد']; begins=[0,.31,.66]
  for i,label in enumerate(labels):
   q=ease((p-begins[i])/.22); y=310+i*120; col=TEAL if q>.45 else (78,112,108)
   txt(d,(270,y+int((1-q)*12)),label,44,col,True)
   if q>.18:
    reach=int(300*ease((q-.18)/.62)); yy=y+55; d.line((115,yy,115+reach,yy),fill=(35,115,108),width=2)
    if reach>280:d.ellipse((421,yy-4,429,yy+4),fill=(85,212,196))
  glow(im,(273,586),155,(15,95,92),27)
 elif t<13.44:
  p=(t-11.2)/2.24; glow(im,(269,576),315,(15,95,92),38); txt(ImageDraw.Draw(im),(270,158),'ملخصاتك أقرب',32,INK,True); app(im,'summary',t,p)
 elif t<15.24:
  p=(t-13.44)/1.8; glow(im,(270,553),288,(15,95,92),35); txt(ImageDraw.Draw(im),(270,158),'أسئلتك الوزارية أمامك',29,INK,True); app(im,'questions',t,p)
 elif t<17.84:
  p=(t-15.24)/2.6; glow(im,(270,551),292,(15,95,92),35); txt(ImageDraw.Draw(im),(270,158),'مراجعتك أكثر تنظيماً',29,INK,True); app(im,'review',t,p)
 elif t<21.68:
  p=(t-17.84)/3.84; glow(im,(270,538),355,(15,95,92),45); app(im,'all',t,p)
 else:
  p=(t-21.68)/4.32; s=.70+.30*ease(min(1,p/.32)); side=int(142*s); em=logo.resize((side,side),Image.Resampling.LANCZOS); glow(im,(270,357),188,TEAL,int(42*(1-min(1,p/.8)))); im.alpha_composite(em,((W-side)//2,263+(142-side)//2)); d=ImageDraw.Draw(im); txt(d,(270,469),'تحضيري',47,INK,True); d.line((156,516,384,516),fill=(85,212,196,180),width=2)
  if p>.13:titles(im,['ادرس بذكاء،','وتقدّم بثقة.'],616,ease((p-.13)/.32),[32,36])
 for edge in [2.72,5.92,8.32,11.2,13.44,15.24,17.84,21.68]:
  if abs(t-edge)<.12:
   a=int(20*(1-abs(t-edge)/.12)); im=Image.alpha_composite(im,Image.new('RGBA',(W,H),(85,212,196,a)))
 return im.convert('RGB')
def main():
 if not Path(FONT).exists() or not (REPO/'icons/icon-512.png').is_file():raise SystemExit('Arabic font/logo missing')
 if FRAMES.exists() and any(FRAMES.iterdir()):raise SystemExit(f'Refusing overwrite: {FRAMES}')
 FRAMES.mkdir(parents=True,exist_ok=True); a=Stream(ROOT/'assets'/'study-library.mp4'); b=Stream(ROOT/'assets'/'page-turn.mp4'); logo=Image.open(REPO/'icons/icon-512.png').convert('RGBA')
 photo=None
 for n in range(DURATION*FPS):
  t=n/FPS
  if t<2.72:photo=a.get() or BG.copy()
  elif t<5.92:photo=b.get() or photo or BG.copy()
  else:photo=None
  render(t,photo,logo).save(FRAMES/f'frame_{n:04d}.png',compress_level=1)
  if n%90==0:print(f'frames {n}/{DURATION*FPS}',flush=True)
 a.close();b.close();print('Frames ready',flush=True)
if __name__=='__main__':main()
