# تحضيري — الإعلان الثاني

الفيديو النهائي هو `tahdiri-ad-02.mp4`. أُعيد بناء المشاهد حول التعليق الصوتي العربي في `voiceover.mp3` (25 ثانية)، مع نقاط انتقال عند حدود الجمل في `voiceover.srt`. الملخص والوزاريات والمراجعة والإنجاز تظهر مع الجمل المطابقة؛ ويبدأ مشهد الشعار عند الخاتمة. مدة النسخة النهائية 26 ثانية لتوفير وقفة بصرية قصيرة بعد انتهاء التعليق.

## المواصفات

- MP4، H.264، AAC
- 1080×1920، عمودي 9:16، 30 FPS
- موسيقى خلفية أصلية هادئة مع نغمات انتقالية خفيفة، تخفيض تلقائي أثناء الكلام
- مصدر الواجهة: ألوان تحضيري وشعاره ومفردات الميزات الفعلية

## إعادة التصدير في Termux

تحتاج `ffmpeg` وPython 3. شغّل:

```sh
cd ~/tahdiri/promo/second
python render_ad.py
```

يُنشئ السكربت مشاهد متحركة وموسيقى مؤقتة خارج مجلد المشروع، ويكتب الملف النهائي دون استبدال الصوت الأصلي. إذا ظهرت مشكلة تحميل مكتبات FFmpeg داخل بيئة Codex، شغّل Python مع عزل متغيرات الربط المضافة من البيئة:

```sh
env -u LD_LIBRARY_PATH -u LD_PRELOAD python render_ad.py
```

تحقق من الخصائص باستخدام:

```sh
env -u LD_LIBRARY_PATH -u LD_PRELOAD ffprobe -v error -show_entries format=duration:stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels -of json tahdiri-ad-02.mp4
```
