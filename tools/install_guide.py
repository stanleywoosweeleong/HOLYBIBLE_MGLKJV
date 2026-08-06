#!/usr/bin/env python3
"""Installation instructions, one block per platform, Mongolian then English.

Written so that a pastor holding only an iPhone can read the Android steps aloud
to somebody else. Menu paths verified against the browsers' own current wording.
"""

GUIDE = [
 ("android", "Android", """
<h5>Android утас, таблет (Chrome)</h5>
<ol>
<li><b>Chrome</b> хөтчийг нээнэ. (Samsung Internet ч болно — доор үзнэ үү.)</li>
<li>Дээд талын хаягийн мөрөнд аппын хаягийг бичнэ.</li>
<li>Библийн бичвэр ачаалж дуустал хүлээнэ. <b>Анх удаа интернэт хэрэгтэй</b> —
    ойролцоогоор 2 МБ.</li>
<li>Баруун дээд буланд байгаа <b>⋮</b> (гурван цэг) товчийг дарна.</li>
<li>Цэснээс <b>«Install app»</b> эсвэл <b>«Add to Home screen»</b> —
    монголоор <b>«Апп суулгах»</b> / <b>«Нүүр дэлгэцэд нэмэх»</b> — гэснийг сонгоно.</li>
<li>Гарч ирэх цонхон дээр <b>«Install»</b> / <b>«Суулгах»</b> дарна.</li>
<li>Нүүр дэлгэцэд дүрс гарч ирнэ. Түүнийг дарж нээнэ.</li>
</ol>
<div class="tip">Хэрэв ⋮ цэсэнд «Install app» харагдахгүй бол: хуудсыг бүрэн ачаалж
дуустал хүлээгээд, дахин оролдоно уу. Chrome-ыг шинэчлэх шаардлагатай байж болно.</div>
<h5>Samsung Internet хөтөч</h5>
<ol>
<li>Доод талын <b>≡</b> цэсийг дарна.</li>
<li><b>«Add page to»</b> → <b>«Home screen»</b> сонгоно.</li>
</ol>
<div class="tip">Суулгасны дараа интернэт <b>хэрэггүй</b>. Утсанд сүлжээ байхгүй газарт
ч Библи бүрэн ажиллана.</div>
""", """
<h5>Android phone or tablet (Chrome)</h5>
<ol>
<li>Open <b>Chrome</b>. (Samsung Internet also works — see below.)</li>
<li>Type the app address into the bar at the top.</li>
<li>Wait until the Bible text has finished loading. <b>Internet is needed this
    first time only</b> — about 2 MB.</li>
<li>Tap the <b>⋮</b> (three dots) at the top right.</li>
<li>Choose <b>Install app</b>, or <b>Add to Home screen</b> if that is what it says.</li>
<li>Tap <b>Install</b> in the box that appears.</li>
<li>An icon appears on the home screen. Open it from there.</li>
</ol>
<div class="tip">If <b>Install app</b> is missing from the menu, let the page finish
loading and try again; Chrome may also need updating.</div>
<h5>Samsung Internet</h5>
<ol>
<li>Tap the <b>≡</b> menu at the bottom.</li>
<li>Choose <b>Add page to</b> → <b>Home screen</b>.</li>
</ol>
<div class="tip">After installing, no internet is needed. The Bible works completely
offline, anywhere.</div>
"""),

 ("ios", "iPhone · iPad", """
<h5>iPhone, iPad (заавал Safari)</h5>
<div class="warn"><b>Заавал Safari ашиглана.</b> iPhone дээр Chrome эсвэл бусад
хөтчөөр апп суулгах боломжгүй.</div>
<ol>
<li><b>Safari</b> нээнэ.</li>
<li>Аппын хаягийг бичиж орно.</li>
<li>Библийн бичвэр ачаалж дуустал хүлээнэ. <b>Анх удаа интернэт хэрэгтэй.</b></li>
<li>Дэлгэцийн <b>доод</b> талд байгаа <b>Хуваалцах</b> товчийг дарна — дээш заасан
    сумтай дөрвөлжин <b>⬆</b>. (iPad дээр баруун <b>дээд</b> талд байна.)</li>
<li>Цэсийг доош гүйлгэж <b>«Add to Home Screen»</b> — <b>«Нүүр дэлгэцэд нэмэх»</b> —
    гэснийг олж дарна.</li>
<li>Баруун дээд буланд <b>«Add»</b> / <b>«Нэмэх»</b> дарна.</li>
<li>Нүүр дэлгэцэд дүрс гарна. <b>Үүнээс нээж хэрэглэнэ.</b></li>
</ol>
<div class="warn"><b>Энэ алхмыг заавал хийнэ.</b> Зөвхөн Safari-д хавчуурга (bookmark)
болгож үлдээвэл, долоо хоног нээхгүй тохиолдолд Apple таны тэмдэглэл, өнгө,
татсан Англи хувилбарыг устгадаг. Нүүр дэлгэцэд нэмсэн апп энэ дүрэмд
<b>хамаарахгүй</b>.</div>
""", """
<h5>iPhone or iPad (Safari only)</h5>
<div class="warn"><b>Safari is required.</b> Chrome and other browsers on iPhone
cannot install the app.</div>
<ol>
<li>Open <b>Safari</b>.</li>
<li>Go to the app address.</li>
<li>Wait for the Bible text to finish loading. <b>Internet is needed this first
    time.</b></li>
<li>Tap the <b>Share</b> button at the <b>bottom</b> of the screen — the square with
    an arrow pointing up <b>⬆</b>. (On iPad it is at the <b>top right</b>.)</li>
<li>Scroll down the menu and tap <b>Add to Home Screen</b>.</li>
<li>Tap <b>Add</b> at the top right.</li>
<li>An icon appears on the home screen. <b>Always open it from there.</b></li>
</ol>
<div class="warn"><b>Do not skip this step.</b> If the app is only bookmarked in
Safari, Apple deletes your notes, highlights and downloaded English text after
seven days without opening it. An app added to the Home Screen is exempt.</div>
"""),

 ("windows", "Windows", """
<h5>Windows (Chrome)</h5>
<ol>
<li><b>Chrome</b> нээж, аппын хаягаар орно.</li>
<li>Хуудас бүрэн ачаалахыг хүлээнэ.</li>
<li>Хаягийн мөрний баруун талд <b>суулгах дүрс</b> (дэлгэц дээр доош сум) гарч ирвэл
    түүнийг дарна.</li>
<li>Эсвэл баруун дээд <b>⋮</b> → <b>«Cast, save, and share»</b> →
    <b>«Install page as app…»</b> сонгоно.</li>
<li><b>«Install»</b> дарна.</li>
<li>Апп Start цэс болон ажлын хэсэгт нэмэгдэнэ.</li>
</ol>
<h5>Windows (Microsoft Edge)</h5>
<ol>
<li>Баруун дээд <b>⋯</b> → <b>«Apps»</b> → <b>«Install this site as an app»</b>.</li>
<li><b>«Install»</b> дарна.</li>
</ol>
<div class="tip">Firefox дээр апп болгон суулгах боломжгүй. Гэхдээ хөтчөөр
хэвийн уншиж болно.</div>
""", """
<h5>Windows (Chrome)</h5>
<ol>
<li>Open <b>Chrome</b> and go to the app address.</li>
<li>Let the page finish loading.</li>
<li>If an <b>install icon</b> (a screen with a down arrow) appears at the right end
    of the address bar, click it.</li>
<li>Otherwise click <b>⋮</b> at the top right → <b>Cast, save, and share</b> →
    <b>Install page as app…</b></li>
<li>Click <b>Install</b>.</li>
<li>The app is added to the Start menu and can be pinned to the taskbar.</li>
</ol>
<h5>Windows (Microsoft Edge)</h5>
<ol>
<li>Click <b>⋯</b> at the top right → <b>Apps</b> → <b>Install this site as an app</b>.</li>
<li>Click <b>Install</b>.</li>
</ol>
<div class="tip">Firefox cannot install web apps, but the site still reads normally
in it.</div>
"""),

 ("mac", "Mac", """
<h5>Mac (Safari 17 ба түүнээс дээш)</h5>
<ol>
<li><b>Safari</b>-гаар аппын хаягаар орно.</li>
<li>Дээд цэснээс <b>File</b> → <b>«Add to Dock…»</b> сонгоно.</li>
<li>Нэрийг шалгаад <b>«Add»</b> дарна.</li>
<li>Апп Dock болон Launchpad-д гарч ирнэ.</li>
</ol>
<h5>Mac (Chrome эсвэл Edge)</h5>
<ol>
<li>Аппын хаягаар орно.</li>
<li>Хаягийн мөрний <b>суулгах дүрс</b>, эсвэл <b>⋮</b> →
    <b>«Cast, save, and share»</b> → <b>«Install page as app…»</b>.</li>
<li><b>«Install»</b> дарна. Апп Applications фолдерт нэмэгдэнэ.</li>
</ol>
<div class="tip">macOS Sonoma-с өмнөх хувилбарын Safari дээр «Add to Dock» байхгүй.
Тэр тохиолдолд Chrome ашиглана уу.</div>
""", """
<h5>Mac (Safari 17 and later)</h5>
<ol>
<li>Open the app address in <b>Safari</b>.</li>
<li>From the menu bar choose <b>File</b> → <b>Add to Dock…</b></li>
<li>Check the name and click <b>Add</b>.</li>
<li>The app appears in the Dock and in Launchpad.</li>
</ol>
<h5>Mac (Chrome or Edge)</h5>
<ol>
<li>Go to the app address.</li>
<li>Click the <b>install icon</b> in the address bar, or <b>⋮</b> →
    <b>Cast, save, and share</b> → <b>Install page as app…</b></li>
<li>Click <b>Install</b>. The app is added to your Applications folder.</li>
</ol>
<div class="tip">Safari before macOS Sonoma has no <b>Add to Dock</b>. Use Chrome on
those machines.</div>
"""),

 ("after", "Дараа нь · After", """
<h5>Суулгасны дараа</h5>
<ol>
<li>Аппыг нэг удаа <b>интернэттэй үед</b> нээнэ. Бичвэр бүрэн хадгалагдана.</li>
<li>Хүсвэл <b>Тохиргоо</b>-оос Англи хувилбар (1.2 МБ) болон Судалгааны багц
    (2.8 МБ) татаж болно. Эдгээрт интернэт нэг удаа хэрэгтэй.</li>
<li>Үүний дараа <b>интернэт огт шаардлагагүй</b>.</li>
</ol>
<h5>Хуваалцах</h5>
<ol>
<li>Аппын доод хэсгийн <b>QR код</b>-ыг бусдад уншуулж болно.</li>
<li>Эсвэл <b>«Холбоосыг хуулах»</b> дарж Messenger, WhatsApp-аар илгээнэ.</li>
<li>Сүлжээгүй газарт: нэг файлтай хувилбарыг (standalone) шууд илгээж болно.</li>
</ol>
""", """
<h5>After installing</h5>
<ol>
<li>Open the app once <b>while online</b>. The text is then stored on the device.</li>
<li>Optionally add the English KJV (1.2 MB) and the study pack (2.8 MB) from
    <b>Settings</b>. Each needs internet once.</li>
<li>After that <b>no internet is needed at all</b>.</li>
</ol>
<h5>Sharing it</h5>
<ol>
<li>Show someone the <b>QR code</b> further down this screen.</li>
<li>Or use <b>Copy link</b> and send it by Messenger or WhatsApp.</li>
<li>Where there is no signal at all, send the single-file version instead.</li>
</ol>
"""),
]
