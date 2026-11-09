#!/usr/bin/env python3
"""Render the voice-led 9:16 Tahdiri ad using FFmpeg available in Termux."""
from pathlib import Path
import math, os, struct, subprocess, wave

ROOT = Path(__file__).resolve().parent
VOICE = ROOT / 'voiceover.mp3'
OUT = ROOT / 'tahdiri-ad-02.mp4'
WORK = Path.home() / 'work-tools' / 'tahdiri-ad02'
FONT = Path(os.environ.get('TAHDIRI_FONT', '/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf'))
W,H,FPS = 1080,1920,30
BG='#101719'; SUR='#182225'; SUR2='#202d30'; LINE='#344448'; INK='#eff7f5'; MUT='#b0c0bd'; BRAND='#55d4c4'; DEEP='#0f5f5c'; GOLD='#e0a526'; OK='#8ce0b0'
# Boundaries follow the Arabic voiceover's detected sentence timestamps.
SCENES = [
 (0.00,2.72,'journey'), (2.72,5.92,'page'), (5.92,8.32,'study'),
 (8.32,11.20,'ready'), (11.20,13.44,'summary'), (13.44,15.24,'ministerial'),
 (15.24,17.84,'review'), (17.84,21.68,'all'), (21.68,26.00,'brand')
]

def run(cmd):
    env=os.environ.copy(); env.pop('LD_LIBRARY_PATH',None); env.pop('LD_PRELOAD',None)
    subprocess.run(cmd,check=True,env=env)

def drawbox(x,y,w,h,color,thick='fill'):
    return f"drawbox=x={x}:y={y}:w={w}:h={h}:color={color}:t={thick}"

def textfile(name,text):
    p=WORK/'text'/f'{name}.txt'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8'); return p

def drawtext(name,text,y,size,color=INK,x='(w-text_w)/2',weight=True):
    p=textfile(name,text)
    return f"drawtext=fontfile='{FONT}':textfile='{p}':text_shaping=1:x={x}:y={y}:fontsize={size}:fontcolor={color}:borderw=1:bordercolor=#00000044:shadowcolor=#00000080:shadowx=0:shadowy=5"

def panel(x,y,w,h,color=SUR,border=LINE):
    return [drawbox(x,y,w,h,color),drawbox(x,y,w,3,border)]

def logo(filters,y=280,size=150):
    x=(W-size)//2; unit=size/160
    filters.append(drawbox(int(x),y,size,size,DEEP))
    filters += [drawbox(int(x+39*unit),int(y+47*unit),int(82*unit),int(8*unit),INK),drawbox(int(x+76*unit),int(y+47*unit),int(8*unit),int(68*unit),INK),drawbox(int(x+52*unit),int(y+110*unit),int(57*unit),int(8*unit),INK)]
    filters.append(drawtext('logo_dot','●',int(y+94*unit),int(26*unit),GOLD,x=f'{int(x+100*unit)}'))

def scene_filters(kind):
    f=[drawbox(0,0,W,H,BG)]
    # Dim teal light panels anchor each composition in the product palette.
    f += [drawbox(0,0,W,14,BRAND),drawbox(35,150,5,1490,'#55d4c433')]
    if kind=='journey':
        f += [drawtext('j1','كل رحلة عظيمة',235,72,INK),drawtext('j2','تبدأ بخطوة',345,86,BRAND)]
        f += panel(115,680,850,720,'#e6e2d5','#d6ceb7')
        f += [drawbox(536,680,8,720,'#c4b99c')]
        f += [drawtext('j3','صفحة جديدة',340,34,'#38514b'),drawtext('j4','هدفك يبدأ هنا',490,30,'#52605a')]
        for i in range(8): f.append(drawbox(205,785+i*54,670-(i%3)*95,3,'#87938b'))
        f += [drawtext('j5','خطوة اليوم…',540,30,DEEP),drawtext('j6','تقرّبك من حلمك',590,30,DEEP)]
    elif kind=='page':
        f += [drawtext('p1','وكل مستقبل تحلم به',230,63,INK),drawtext('p2','يبدأ من صفحة',330,78,BRAND)]
        f += panel(140,650,800,760,SUR)
        f += [drawtext('p3','من الكتاب',465,32,MUT),drawtext('p4','إلى خطوتك القادمة',520,36,INK)]
        # A clean path into the digital study screen.
        f += [drawbox(250,710,580,4,BRAND),drawbox(250,710,4,160,BRAND),drawbox(826,710,4,160,BRAND)]
        f += [drawtext('p5','تحضيري',735,40,INK),drawtext('p6','موادك وصفحاتك بمكان واحد',815,28,MUT)]
        f += panel(225,925,630,280,SUR2)
        f += [drawtext('p7','الرياضيات',990,34,INK),drawtext('p8','ملخص  •  سؤال  •  مراجعة',1075,24,BRAND)]
    elif kind=='study':
        f += [drawtext('s1','التفوّق مو مجرد دراسة',260,62,INK),drawtext('s2','هو فهمٌ يثبت',365,40,BRAND)]
        f += panel(125,690,830,680,SUR)
        f += [drawtext('s3','افهم الفكرة',620,39,INK),drawtext('s4','تدرّب عليها',850,39,INK),drawtext('s5','راجعها بثقة',1080,39,INK)]
        for yy in (745,975,1205): f.append(drawbox(260,yy,560,3,LINE))
        f += [drawbox(780,690,7,160,BRAND),drawbox(780,920,7,160,GOLD),drawbox(780,1150,7,160,OK)]
        f += [drawtext('s6','فهم',300,25,BRAND),drawtext('s7','تدريب',530,25,GOLD),drawtext('s8','مراجعة',760,25,OK)]
    elif kind=='ready':
        f += [drawtext('r1','فهم ومراجعة',260,68,INK),drawtext('r2','واستعدادٌ أهدأ',365,44,BRAND)]
        f += panel(130,685,820,660,SUR)
        f += [drawtext('r3','خطتك الدراسية',600,32,BRAND),drawtext('r4','درس اليوم',755,36,INK),drawtext('r5','اختبر فهمك',950,36,INK),drawtext('r6','تابع تقدّمك',1145,36,INK)]
        for yy in (825,1020,1215):f.append(drawbox(220,yy,640,2,LINE))
    elif kind=='summary':
        f += [drawtext('sm1','ملخصات المواد',245,64,INK),drawtext('sm2','المعلومة أوضح',335,34,BRAND)]
        f += panel(105,610,870,820,SUR)
        f += [drawtext('sm3','تحضيري     ‹     الرياضيات',535,24,MUT),drawtext('sm4','ملخص الصفحة ٤٢',650,37,BRAND),drawtext('sm5','القوانين الأساسية',790,35,INK),drawtext('sm6','المعادلات الخطية',960,31,INK),drawtext('sm7','الفكرة الرئيسية',1090,28,MUT)]
        f += [drawbox(185,850,710,3,LINE),drawbox(185,1030,710,3,LINE),drawbox(185,1170,710,3,LINE)]
        f += [drawtext('sm8','رياضيات · الفصل الأول',1270,23,MUT)]
    elif kind=='ministerial':
        f += [drawtext('m1','أسئلتك الوزارية',240,61,INK),drawtext('m2','قدّامك وقت ما تحتاجها',330,30,BRAND)]
        f += panel(100,600,880,830,SUR)
        f += panel(620,650,300,78,'#3a311d','#e0a526')
        f += [drawtext('m3','★  وزاري موثّق',672,23,GOLD,x='640')]
        f += [drawtext('m4','حلّ المعادلة التالية:',820,31,INK,x='185'),drawtext('m5','٢س + ٥ = ١٩',915,39,INK,x='185')]
        for i,lab in enumerate(['س = ٥','س = ٧','س = ١٢']):
            yy=1030+i*104; f += panel(170,yy,740,76,'#202d30',BRAND if i==1 else LINE); f.append(drawtext(f'mopt{i}',lab,yy+20,27,INK,x='220'))
    elif kind=='review':
        f += [drawtext('rv1','راجع، اختبر، وتقدّم',250,58,INK)]
        f += panel(100,600,880,790,SUR)
        f += [drawtext('rv2','مراجعة اليوم',690,37,BRAND),drawtext('rv3','اختبار قصير',850,34,INK),drawtext('rv4','إجابة صحيحة  ✓',965,30,OK)]
        f += [drawbox(190,1030,700,3,LINE),drawtext('rv5','إنجازك هذا الأسبوع',1100,29,INK)]
        bars=[120,190,145,240,185,300,265]
        for i,h in enumerate(bars):
            f += [drawbox(280+i*76,1330-h,42,h,BRAND if i==5 else DEEP),drawtext(f'rvday{i}',['ح','ن','ث','ر','خ','س','ح'][i],1350,19,MUT,x=str(280+i*76))]
    elif kind=='all':
        f += [drawtext('a1','كل ما تحتاجه',220,68,INK),drawtext('a2','للرحلة الدراسية',315,60,BRAND)]
        f += panel(85,560,910,900,SUR)
        f += [drawtext('a3','تحضيري  ·  دراستك بترتيب',500,29,MUT)]
        cards=[(155,650,'ملخصات المواد','≡',BRAND),(555,650,'أسئلة وزارية','★',GOLD),(155,970,'اختبارات ومراجعة','✓',OK),(555,970,'متابعة الإنجاز','↗','#a7d4fa')]
        for i,(xx,yy,title,ic,col) in enumerate(cards):
            f += panel(xx,yy,370,270,SUR2,LINE)
            f += [drawtext(f'aico{i}',ic,yy+55,46,col,x=str(xx+165)),drawtext(f'atitle{i}',title,yy+160,28,INK,x=str(xx+32))]
        f += [drawtext('a4','خطواتك كلها في مكان واحد',1350,27,MUT)]
    elif kind=='brand':
        logo(f,y=280,size=170)
        f += [drawtext('b1','تحضيري',530,85,INK),drawbox(260,680,560,4,BRAND),drawtext('b2','ادرس بذكاء،',850,59,INK),drawtext('b3','وتقدّم بثقة.',950,68,BRAND),drawtext('b4','مستقبلك يبدأ من صفحة',1200,30,MUT)]
    return f

def make_still(kind,index):
    filters=scene_filters(kind)
    vf=','.join(filters)
    dest=WORK/f'scene-{index:02}.png'
    run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','lavfi','-i',f'gradients=s={W}x{H}:c0=#19302e:c1={BG}:x0=0:y0=0:x1={W}:y1={H}:r=1:d=1','-vf',vf,'-frames:v','1',str(dest)])
    return dest

def make_music(path,duration=26.2,sr=48000):
    # Soft, original ambient bed: warm sustained chords and sparse bell accents.
    chords=[(130.81,155.56,196.00),(103.83,130.81,155.56),(155.56,196.00,233.08),(116.54,146.83,174.61)]
    total=int(duration*sr)
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        block=4800
        for start in range(0,total,block):
            out=bytearray()
            for n in range(start,min(start+block,total)):
                t=n/sr; ci=min(3,int(t/6.5)); chord=chords[ci]; phase=t%6.5
                fade=min(1,t/1.8,max(0,(duration-t)/1.5))
                val=0.0
                for k,f in enumerate(chord):
                    val += (math.sin(2*math.pi*f*t)+.20*math.sin(2*math.pi*f*2*t)+.06*math.sin(2*math.pi*f*3*t))*(.012/(k+1))
                # Gentle pulsing low note and a few transition chimes, kept below dialogue.
                val += .009*math.sin(2*math.pi*65.41*t)*(0.45+0.55*math.sin(2*math.pi*.12*t)**2)
                for when,f in [(2.72,523.25),(5.92,659.25),(11.2,587.33),(13.44,698.46),(15.24,587.33),(17.84,783.99),(21.68,659.25)]:
                    q=t-when
                    if 0<=q<.65: val += .010*math.sin(2*math.pi*f*q)*math.exp(-5*q)
                val*=fade
                v=max(-1,min(1,val)); sample=int(v*32767)
                out.extend(struct.pack('<hh',sample,int(sample*(.96+.04*math.sin(2*math.pi*.18*t)))) )
            w.writeframesraw(out)

def main():
    if not VOICE.exists(): raise SystemExit(f'Missing voiceover: {VOICE}')
    WORK.mkdir(parents=True,exist_ok=True)
    scenes=[]
    for i,(_,_,kind) in enumerate(SCENES):
        print(f'Rendering scene {i+1}/{len(SCENES)}: {kind}',flush=True);scenes.append(make_still(kind,i))
    music=WORK/'music.wav';make_music(music)
    # Build animated, gently moving stills and crossfade them on the transcript boundaries.
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning']
    for still in scenes: cmd += ['-loop','1','-framerate',str(FPS),'-i',str(still)]
    cmd += ['-i',str(VOICE),'-i',str(music)]
    fc=[]; durations=[b-a for a,b,_ in SCENES]
    fade=.28
    for i,d in enumerate(durations):
        d_stream=d+fade
        frames=round(d_stream*FPS);fc.append(f'[{i}:v]zoompan=z=1+0.028*on/{max(frames,1)}:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={frames}:s={W}x{H}:fps={FPS},trim=duration={d_stream:.3f},setpts=PTS-STARTPTS[v{i}]')
    current='v0'
    for i in range(1,len(durations)):
        out=f'x{i}';offset=SCENES[i][0]-fade
        fc.append(f'[{current}][v{i}]xfade=transition=fade:duration={fade}:offset={offset:.3f}[{out}]')
        current=out
    fc.append(f'[{current}]fps={FPS},scale={W}:{H},format=yuv420p[vout]')
    # Duck the score under the voice. The voice stays at original speed and position.
    fc.append('[10:a]volume=0.16,afade=t=in:st=0:d=1.5,afade=t=out:st=24.8:d=1.2[bed]')
    fc.append('[9:a]aresample=48000,apad=pad_dur=1.04,atrim=duration=26,volume=1.15[voice]')
    fc.append('[voice]asplit=2[voice_mix][voice_sc]')
    fc.append('[bed][voice_sc]sidechaincompress=threshold=0.025:ratio=8:attack=35:release=420:makeup=1[duck]')
    fc.append('[voice_mix][duck]amix=inputs=2:duration=longest:weights=1 0.45:normalize=0,alimiter=limit=0.93,atrim=duration=26[aout]')
    cmd += ['-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-t','26','-r',str(FPS),'-c:v','libx264','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-level:v','4.2','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(OUT)]
    print('Encoding H.264/AAC MP4…',flush=True);run(cmd)
    print(f'Wrote {OUT} ({OUT.stat().st_size/1048576:.1f} MiB)')

if __name__=='__main__': main()
