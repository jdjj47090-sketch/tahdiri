#!/usr/bin/env python3
"""Render a non-destructive, voice-locked cinematic Tahdiri V2 preview."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
WORK = Path.home() / 'work-tools' / 'tahdiri-ad02-v2'
FRAMES = WORK / 'frames'
W, H, FPS = 540, 960, 30
DURATION = 26.0
BG = (16,23,25); SURF=(24,34,37); SURF2=(32,45,48); LINE=(52,68,72)
INK=(239,247,245); MUTED=(176,192,189); TEAL=(85,212,196); DEEP=(15,95,92); GOLD=(224,165,38); WARN=(244,209,126)
FONT_PATH='/system/fonts/NotoNaskhArabicUI-Regular.ttf'
FONT_BOLD='/system/fonts/NotoNaskhArabicUI-Bold.ttf'
if not Path(FONT_PATH).exists(): FONT_PATH='/system/fonts/NotoNaskhArabic-Regular.ttf'
if not Path(FONT_BOLD).exists(): FONT_BOLD=FONT_PATH
FONT_CACHE={}
SCENES=[(0.00,2.72,'opening'),(2.72,5.92,'page'),(5.92,8.32,'thesis'),(8.32,11.20,'three'),(11.20,13.44,'summary'),(13.44,15.24,'questions'),(15.24,17.84,'review'),(17.84,21.68,'ecosystem'),(21.68,26.0,'brand')]


def font(size,bold=False):
    key=(size,bold)
    if key not in FONT_CACHE: FONT_CACHE[key]=ImageFont.truetype(FONT_BOLD if bold else FONT_PATH,size)
    return FONT_CACHE[key]

def ease(t):
    t=max(0,min(1,t)); return 1-(1-t)**3

def text(draw,xy,s,size,color=INK,bold=False,anchor='mm',stroke=0):
    draw.text(xy,s,font=font(size,bold),fill=color,anchor=anchor,direction='rtl',language='ar',stroke_width=stroke,stroke_fill=(3,12,13,180))

_BASE=None
def base(t, scene_idx):
    global _BASE
    if _BASE is None:
        _BASE=Image.new('RGB',(W,H)); d=ImageDraw.Draw(_BASE)
        for y in range(H):
            f=y/H; k=max(0,1-abs(f-.38)/.78)
            d.line((0,y,W,y),fill=(BG[0]+2,BG[1]+int(13*k),BG[2]+int(12*k)))
        mask=Image.new('L',(W,H),0); md=ImageDraw.Draw(mask)
        md.ellipse((-280,-225,W+280,H+235),fill=0)
        md.ellipse((-180,-140,W+180,H+170),fill=105)
        mask=mask.filter(ImageFilter.GaussianBlur(100))
        _BASE=Image.composite(Image.new('RGB',(W,H),(0,0,0)),_BASE,mask)
    return _BASE.copy()

def glow(im,xy,radius,color,alpha=100):
    lay=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(lay)
    x,y=xy; d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*color,alpha))
    lay=lay.filter(ImageFilter.GaussianBlur(radius*.6)); im.alpha_composite(lay)

def centered_text(im,y,s,size,color=INK,bold=True):
    d=ImageDraw.Draw(im); text(d,(W//2,y),s,size,color,bold)

def lines(draw,box,count,color=(50,69,69),spacing=24,width=180):
    x,y,w,h=box
    for i in range(count):
        yy=y+i*spacing
        if yy<y+h: draw.rounded_rectangle((x,yy,x+width-(i%3)*23,yy+2),radius=1,fill=color)

def screen_surface(im,t,mode):
    """A hand-built representation of actual app components, not a screenshot."""
    p=Image.new('RGBA',(370,560),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle((8,8,362,552),radius=19,fill=(*SURF,255),outline=(*LINE,255),width=2)
    # App navigation/title treatment based on the real dark theme.
    d.rounded_rectangle((25,27,345,82),radius=10,fill=(*SURF2,255))
    text(d,(185,54),'تحضيري',28,INK,True)
    if mode=='summary':
        text(d,(185,119),'مكتبة المواد',21,TEAL,True)
        text(d,(185,160),'الرياضيات',20,INK,False)
        text(d,(185,184),'للصف الثالث المتوسط',18,INK,False)
        d.line((35,207,335,207),fill=(*LINE,255),width=2)
        text(d,(185,237),'ملخص الصفحة',21,TEAL,True)
        for i,label in enumerate(['الفكرة الأساسية','التعاريف','القوانين والرموز والوحدات','نقاط للحفظ']):
            yy=278+i*55
            text(d,(316,yy),label,20,INK,False,anchor='rm')
            d.line((38,yy+20,330,yy+20),fill=(*LINE,255),width=1)
        text(d,(185,518),'لم تتم مراجعته بعد',17,WARN,False)
    elif mode=='questions':
        text(d,(185,125),'مكتبة الوزاريات',22,TEAL,True)
        d.line((35,158,335,158),fill=(*LINE,255),width=2)
        text(d,(185,207),'منسوب للوزاري',22,INK,True)
        text(d,(185,245),'غير متحقق',22,WARN,True)
        text(d,(185,303),'لا يدخل الاختبارات',20,MUTED,False)
        text(d,(185,365),'يُعرض بعد التحقق من',20,MUTED,False)
        text(d,(185,398),'المصدر والسنة والدور',20,MUTED,False)
        d.line((60,440,310,440),fill=(*LINE,255),width=1)
    elif mode=='review':
        text(d,(185,124),'المراجعة',24,TEAL,True)
        d.line((35,158,335,158),fill=(*LINE,255),width=2)
        text(d,(185,214),'مراجعة الصفحة',23,INK,True)
        text(d,(185,268),'اختبار قصير',21,MUTED,False)
        d.line((50,298,320,298),fill=(*LINE,255),width=1)
        text(d,(185,343),'تقدّمي',23,TEAL,True)
        text(d,(185,394),'مهام منجزة',20,INK,False)
        text(d,(185,430),'صفحات مدروسة',20,INK,False)
        text(d,(185,466),'اختبارات',16,INK,False)
        text(d,(185,508),'بيانات تقدّمك على جهازك',16,MUTED,False)
    else:
        text(d,(185,125),'مكتبة المواد',23,TEAL,True)
        text(d,(185,174),'ملخص الصفحة',18,INK,False)
        d.line((40,196,330,196),fill=(*LINE,255),width=1)
        text(d,(185,240),'مكتبة الوزاريات',20,INK,True)
        text(d,(185,274),'منسوب للوزاري',17,INK,False)
        text(d,(185,298),'غير متحقق',17,WARN,False)
        d.line((40,308,330,308),fill=(*LINE,255),width=1)
        text(d,(185,359),'اختبارات',19,INK,True)
        text(d,(185,405),'المراجعة',19,INK,False)
        d.line((40,433,330,433),fill=(*LINE,255),width=1)
        text(d,(185,476),'تقدّمي',19,TEAL,True)
    # The UI floats as one thin, tilted plane in a dark photographed-feeling space.
    scale=0.96+0.02*math.sin(t*.7)
    p=p.resize((int(370*scale),int(560*scale)),Image.Resampling.LANCZOS)
    angle=2.4*math.sin(t*.48)
    p=p.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    x=(W-p.width)//2+int(12*math.sin(t*.5)); y=228+int(8*math.sin(t*.63))
    shadow=Image.new('RGBA',(W,H)); sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x+13,y+18,x+p.width+16,y+p.height+18),radius=24,fill=(0,0,0,140))
    shadow=shadow.filter(ImageFilter.GaussianBlur(22)); im.alpha_composite(shadow)
    im.alpha_composite(p,(x,y))

def draw_book(im,t):
    d=ImageDraw.Draw(im,'RGBA'); drift=math.sin(t*.48)*7
    # Architecture and pools of practical desk light establish a space rather than a UI wallpaper.
    d.polygon([(0,0),(210,0),(165,390),(0,465)],fill=(26,39,39,255))
    d.polygon([(540,0),(540,425),(377,380),(342,0)],fill=(18,30,31,255))
    d.polygon([(0,500),(540,470),(540,960),(0,960)],fill=(17,26,27,255))
    # A quiet over-shoulder student silhouette anchors the opening in a real study moment.
    lean=int(4*math.sin(t*.55))
    d.ellipse((218+lean,270,322+lean,386),fill=(27,39,39,255))
    d.polygon([(177+lean,383),(218+lean,355),(267+lean,370),(321+lean,356),(370+lean,393),(404,525),(137,535)],fill=(23,35,36,255))
    d.arc((208+lean,267,324+lean,389),198,292,fill=(104,133,122,155),width=2)
    # Open textbook, perspective spread, paper edges and central gutter.
    left=[(42,482+drift),(258,430+drift),(263,796),(36,839)]
    right=[(262,430+drift),(502,484+drift),(506,835),(261,796)]
    d.polygon(left,fill=(195,184,153,255)); d.polygon(right,fill=(188,177,148,255))
    d.polygon([(47,481+drift),(258,441+drift),(259,779),(43,819)],fill=(239,232,209,255))
    d.polygon([(266,441+drift),(496,485+drift),(500,816),(265,779)],fill=(232,225,202,255))
    d.line((261,441+drift,262,793),fill=(90,80,63,135),width=4)
    # Subtle authentic-looking print lines are texture only, no fake lesson copy.
    for i in range(8):
        yy=510+i*30+int(drift*.3); x2=223-(i%3)*18
        d.line((72,yy,x2,yy-10),fill=(132,130,113,115),width=2)
        d.line((298,yy-10,470-(i%2)*21,yy+8),fill=(132,130,113,105),width=2)
    # The narrow edge of the desk light stays on the page, leaving the study space quiet.
    d.line((254,453,284,779),fill=(196,157,88,100),width=2)

def draw_page(im,t,u):
    d=ImageDraw.Draw(im,'RGBA'); p=ease(u)
    # Page rises from the spread, then narrows into a single illuminated digital plane.
    xshift=int(145*p)
    pts=[(78+xshift,480-int(50*p)),(260+xshift,440-int(55*p)),(268+xshift,783-int(225*p)),(73+xshift,824-int(205*p))]
    d.polygon(pts,fill=(244,237,215,250-int(95*p)),outline=(255,247,226,200))
    if p<.9:
        for i in range(7):
            yy=520+i*33-int(48*p); d.line((112+xshift,yy,222+xshift-(i%2)*20,yy-18),fill=(92,115,108,130),width=2)
    # Digital edge light follows the page's direction, a purposeful match transition.
    x=206+int(112*p)
    d.line((x,235,x,815),fill=(*TEAL,80+int(110*p)),width=2)
    d.line((x+7,290,x+7,750),fill=(*TEAL,35+int(90*p)),width=1)

def scene_frame(t,idx,start,end,kind):
    u=(t-start)/(end-start); im=base(t,idx).convert('RGBA')
    if kind=='opening':
        draw_book(im,t)
        glow(im,(270,493),245,(197,157,89),47)
        centered_text(im,174,'كل رحلة عظيمة',42,INK,True)
        centered_text(im,226,'تبدأ بخطوة',47,TEAL,True)
        # Slow, nearly imperceptible camera push is expressed through book movement.
    elif kind=='page':
        draw_book(im,t); draw_page(im,t,u)
        centered_text(im,157,'وكل مستقبل تحلم به',36,INK,True)
        centered_text(im,207,'يبدأ من صفحة',46,TEAL,True)
    elif kind=='thesis':
        centered_text(im,145,'لكن التفوق',47,INK,True)
        centered_text(im,193,'ليس مجرد دراسة',44,TEAL,True)
        # The paper plane resolves into the app's actual surface at the line break.
        screen_surface(im,t,'summary')
    elif kind=='three':
        # Three ideas reveal in sync, one at a time; typography is the image.
        labels=['فهم','مراجعة','استعداد']
        active=min(2,int(u*3.25))
        for i,label in enumerate(labels):
            yy=280+i*138; x=270-int(22*ease(max(0,min(1,(u*3.25-i)*1.2))))
            col=TEAL if i==active else (147,166,163)
            d=ImageDraw.Draw(im); text(d,(x,yy),label,49,col,True)
            if i<2 and u>(i+.4)/3.25: d.line((270,yy+38,270,yy+99),fill=(*TEAL,75),width=2)
        glow(im,(270,540),180,(29,120,108),30)
    elif kind in ('summary','questions','review','ecosystem'):
        mode={'summary':'summary','questions':'questions','review':'review','ecosystem':'ecosystem'}[kind]
        title={'summary':'ملخصات المواد','questions':'أسئلتك الوزارية أمامك','review':'ومراجعتك أصبحت أكثر تنظيماً','ecosystem':'كل ما تحتاجه للرحلة الدراسية'}[kind]
        centered_text(im,142,title,32 if kind!='ecosystem' else 29,INK,True)
        if kind=='ecosystem': centered_text(im,188,'في مكان واحد',36,TEAL,True)
        screen_surface(im,t,mode)
        # A very restrained rim light gives the reconstructed interface physical depth.
        glow(im,(270,545),280,(35,115,106),28)
    else:
        logo=Image.open(REPO/'icons/icon-512.png').convert('RGBA').resize((166,166),Image.Resampling.LANCZOS)
        p=.64+.36*ease(min(1,u*5)); logo=logo.resize((int(166*p),int(166*p)),Image.Resampling.LANCZOS)
        im.alpha_composite(logo,((W-logo.width)//2,218+(166-logo.height)//2))
        centered_text(im,435,'تحضيري',58,INK,True)
        d=ImageDraw.Draw(im); d.line((110,482,430,482),fill=(*TEAL,190),width=2)
        if u>0.17: centered_text(im,555,'ادرس بذكاء،',38,INK,True)
        if u>0.34: centered_text(im,615,'وتقدّم بثقة.',42,TEAL,True)
    # Fine restrained grain makes the gradients feel less synthetic while preserving text contrast.
    if idx in (0,1,8):
        overlay=Image.new('RGBA',(W,H)); od=ImageDraw.Draw(overlay)
        # Sparse, dim practical dust only in book light; not on product surfaces.
        if idx in (0,1):
            for k in range(11):
                x=int((k*71+int(t*7))%W); y=int((k*113+int(t*11))%H)
                od.ellipse((x,y,x+1,y+1),fill=(255,231,186,32))
        im.alpha_composite(overlay)
    return im.convert('RGB')

def main():
    if FONT_PATH is None or not Path(FONT_PATH).exists(): raise SystemExit('Arabic font unavailable; refusing unshaped fallback.')
    if not (REPO/'icons/icon-512.png').exists(): raise SystemExit('Actual logo asset missing.')
    if FRAMES.exists() and any(FRAMES.iterdir()): raise SystemExit(f'Refusing to overwrite existing frame directory: {FRAMES}')
    FRAMES.mkdir(parents=True,exist_ok=True)
    total=round(DURATION*FPS)
    for n in range(total):
        t=n/FPS
        idx=next((i for i,(a,b,_) in enumerate(SCENES) if a<=t<b),len(SCENES)-1)
        a,b,kind=SCENES[idx]
        scene_frame(t,idx,a,b,kind).save(FRAMES/f'frame_{n:04d}.png',compress_level=1)
        if n%60==0: print(f'frames {n}/{total}',flush=True)
    print(f'Frames ready: {total} in {FRAMES}')
if __name__=='__main__': main()
