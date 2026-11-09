# تحضيري — معاينة الإعلان الثاني V2

ملف `tahdiri-ad-02-v2-preview.mp4` هو معاينة مستقلة للمراجعة. الملف السابق `tahdiri-ad-02.mp4` محفوظ كما هو. أُعيد بناء مشاهد المعاينة حول توقيت الجمل في `voiceover.srt`، مع الإبقاء على المزيج الصوتي الأصلي. واجهات المنتج تمثيل مبني على مكونات التطبيق وبياناته، وليست لقطات شاشة فعلية. Contact Sheet: `tahdiri-ad-02-v2-contact-sheet.png`.

## المواصفات

- MP4، H.264، AAC
- 1080×1920، عمودي 9:16، 30 FPS
- التعليق الصوتي والموسيقى من المزيج الأصلي، دون تغيير المحتوى أو التوقيت
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

صفحة `index.html` تعرض معاينة V2 وContact Sheet ورابط تحميل الفيديو ونص التوقيت.
