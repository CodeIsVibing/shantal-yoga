# Shantal Yoga Exercise Document

## Šta je projekat
Statična web stranica (`index.html`) za pravljenje Word dokumenta po uzoru na mesečne planove časa „Shantal Yoga“ (referenca: `~/Downloads/2025 02 Febrero_compressed.docx`). Interfejs je na španskom od v1.7.0 (03.11.2026, pre toga engleski), naziv je „Documento de ejercicios“ (ranije „Shantal Yoga Exercise Document“, pa „Photos to Word“). Sav tekst u interfejsu (dugmad, poruke, aria-label, title) piše se na španskom, sa „tú“ imperativom („Elige“, „Añade“). Nazivi u ovom fajlu ispod su često ostali na engleskom; u interfejsu važi španski. Raspored u tri kolone: levo Outline (pregled dokumenta, klik skače na red), u sredini A4 strana na kojoj se uređuje direktno, desno panel Document (broj delova/vežbi/slika, kvalitet, ime fajla, procena veličine, **Download Word file**; kartica File sa dugmadima „New document“ i „Open Word file“). Na užim ekranima levi panel nestaje (<1400 px), pa i desni (<1120 px) i tada izvoz ide preko plutajuće trake na dnu.

Hostuje se na GitHub Pages. Mora da radi i lokalno (`file://`), bez interneta.

## Glavni cilj
Word fajl mora biti **što manji**. Svaka slika se smanjuje tačno na veličinu u kojoj se prikazuje u dokumentu (cm × dpi), pa kompresuje u JPG. Test: 23 slike od 3,5 MB daju .docx od ~133 KB. Panel prikazuje procenu veličine (`estimate()`, gruba, obično malo veća od stvarne).

## Arhitektura
- Sve radi u browseru. Nema servera, build koraka ni bundlera.
- Jedina zavisnost: **JSZip 3.10.1** u `vendor/jszip.min.js` (lokalno, radi offline).
- `.docx` se pravi ručno (Open XML): `[Content_Types].xml`, `_rels/.rels`, `word/document.xml`, `word/styles.xml`, `word/_rels/document.xml.rels`, `word/media/logo.png`, `word/media/imageN.jpeg`.
- Rad se automatski čuva u IndexedDB (baza `slike-u-word`, ključ `doc`), zajedno sa originalnim slikama. Bez IndexedDB alat i dalje radi, samo se rad ne pamti.

## Logo
- Logo je **uvek isti** i ne može da se menja iz interfejsa. Ugrađen je kao base64 u `LOGO_B64` u `index.html`; izvor je `logo.png`.
- U referentnom dokumentu logo je JPEG sa crnom pozadinom (providnost izgubljena pri kompresiji), pa se u Word-u vidi crn pravougaonik. `logo.png` je iz njega rekonstruisan kao providan PNG (944×346). Ako se dobije originalni logo, zameniti `logo.png` i `LOGO_B64`.
- U Word-u: centriran, širina 8 cm, iznad naslova.

## Dokument (kao referenca)
- A4, levo/desno 3 cm, gore/dole 2,5 cm. Font Arial, crna boja.
- Sve je centrirano (od 2026-11-01, na zahtev korisnika): `w:jc="center"` u stilu `Normal`, pa ga nasleđuju Title, Heading1 i Heading2; redovi slika i logo su takođe centrirani. Pregled prati isto (`text-align:center`, `.row` centriran).
- Naslov: stil `Title`, 14 pt, podebljano.
- Deo: stil `Heading1`, 12 pt, podebljano i podvučeno (vidi se u Navigation panelu).
- Vežba: stil `Heading2`, 12 pt, obično slovo, `keepNext` kada ima slike (naziv ostaje uz slike).
- Slike vežbe: jedan paragraf po redu slika, inline slike razdvojene razmakom.

## Raspored slika (isti u pregledu i u Word-u)
`layoutRows(images, size)`: bira najmanji broj redova u kome svaki red može da popuni 15 cm širine na bar 65% izabrane visine (`SIZES`: Small 2,6 cm, Medium 4 cm, Large 6 cm). Slike se dele u ujednačene redove; red nikad nije viši od izabrane visine. Svaki red je zaseban paragraf u Word-u (razmak 0,12 cm, `keepNext` između redova), pa Word nikad sam ne prelama slike. Pregled koristi CSS `cm` jedinice pomnožene sa `--k` (na uskom ekranu sve se srazmerno smanjuje).

## Prelom strane i popunjavanje strana
`computeLayout()` pravi model dokumenta istim merama kao Word: red teksta 12 pt = 0,525 cm (Arial, `line=259`), razmak posle 0,282 cm, naslov 0,613 + 0,847 cm, red slika = visina + 0,09 cm. Visina strane za sadržaj je 24,7 cm. Lanci `keepNext` (deo + vežba + svi redovi slika) prelaze zajedno na novu stranu, osim ako su viši od strane. Kada lanac ne stane na dno strane za malo, njegove slike se smanje (najviše do `MIN_FIT` = 60%, uz rezervu 0,15 cm) da stane; tako na dnu strane ne ostaje 4 do 6 cm praznog prostora. Smanjene visine redova (`layout.rows`) koriste i pregled i izvoz. Pri kucanju `relayout()` ponovo gradi redove samo ako se visina nekog reda promenila (kursor ostaje na mestu). Redovi sa slikama u Word-u imaju jednostruki prored (`w:line="240"`), pa je red tačno visine slike + 0,09 cm. Duge nazive meri kroz canvas `measureText` (prelom u više redova). U pregledu se ubacuje traka `.pgbreak` („Page 2“) koja izgleda kao razmak između dva lista, a panel prikazuje broj strana. Provereno na snimku korisnikovog izvoza: prelom se poklapa.

## Otvaranje postojećeg .docx
`openDocx(file)`: dugme „Open Word file“, ⌘O ili prevlačenje .docx na stranu. Fajlovi iz ovog alata se čitaju po stilovima (`Title`, `Heading1`, ostalo vežba). Stariji planovi (kao Febrero) po formatiranju: prvi podebljan red bez podvlačenja je naslov, podebljano i podvučeno je deo, ostali tekst je vežba. Slike idu u poslednju vežbu; slike pre prvog teksta su logo i preskaču se, kao i skrivene slike manje od 2 mm. Neprepoznati formati (EMF, WMF) se preskaču i broje u obaveštenju. Za svaku vežbu bira se Small/Medium/Large koja daje visinu najbližu originalu. Otvaranje zamenjuje trenutni rad, uz „Undo“. Referenca Febrero se otvara sa 28 redova i 40 slika i izvozi u 249 KB (original 12 MB).

## Batch smanjenje (`batch.html`)
Zasebna stranica „Shrink documents“, link „Shrink many files“ u kartici File. Obrađuje .docx i .odt jedan po jedan (`PAUSE_BETWEEN` 400 ms između fajlova), sa ukupnim napretkom, napretkom trenutnog fajla po koracima i listom (Waiting, Working, Finished, Finished earlier, Failed, Add again).
- Smanjenje: za svaku sliku meri se najveća veličina prikaza u dokumentu (`wp:extent` + `a:srcRect` isecanje, VML `v:shape` style) i slika se svodi na tu veličinu pri 200 dpi/JPEG 82% (Balanced) ili 300 dpi/JPEG 88% (High quality, podrazumevano). Nepoznata veličina: najduža strana 2400 px. Slike sa providnošću ostaju PNG. Mršavi JPEG koji ne treba smanjivati se ne dira. Nova slika se uzima samo ako je bar 8% manja; slike ispod 30 KB, GIF, EMF/WMF/SVG ostaju iste.
- **Svaki izlaz je .docx** (od v1.3.0, na zahtev korisnika). `odtToDocx()` pretvara ODT u DOCX u browseru, pa se slike smanjuju istim postupkom kao za docx. Prenosi: stilove sa nasleđivanjem (podebljano, kurziv, podvučeno, precrtano, veličina, boja, font, gornji/donji indeks; poravnanje, razmaci, uvlačenje, prelom strane pre/posle), `text:h` kao Heading1-6, liste (tačka ili broj, ugnežđene), tabele (širine kolona, spojene ćelije, okviri), slike u veličini okvira (SVG i WebP se crtaju u PNG), tekst iz okvira za tekst, tab, razmake, prelom reda, zaglavlje i podnožje glavne strane, veličinu i margine strane. Ne prenosi: fusnote, komentare, plutajući raspored slika (sve slike postaju inline), sadržaj (TOC) kao polje.
- Ime izlaza: `.odt` postaje `.docx`; ako u listi već postoji .docx sa istim imenom, izlaz dobija „ (from odt)“ (`outPath()`).
- Promena ekstenzije slike (PNG u JPEG) ažurira sve `.rels` i `[Content_Types].xml`. `JSZip.defaults.createFolders = false`, bez praznih unosa za foldere.
- Ako .docx ne postane manji, snima se original (izlazni folder je kompletan). Pretvoreni ODT se uvek snima kao novi .docx.
- Čuvanje: Chrome/Edge biraju izlazni folder (File System Access, zadržava podfoldere); folder sa originalima se odbija (`isSameEntry` i provera istog imena i veličine). Ostali browseri preuzimaju svaki fajl odmah posle obrade.
- Nastavak: IndexedDB baza `shantal-batch` čuva `done` (ključ ime|veličina|vreme izmene), `queue`, `attempts`, `current`, folder handle-ove. Posle pada se nastavlja; fajl na kome je stranica pala dva puta se preskače. Bez handle-ova (fajlovi iz običnog izbora) korisnik ponovo dodaje fajlove, a gotovi se preskaču. Ako browser i dalje dozvoljava pristup folderima, nastavlja sam posle odbrojavanja od 3 s. Wake Lock drži ekran budnim tokom rada.
- Test: Febrero 11,8 MB postaje 661 KB (High quality); test ODT sa zaglavljem, listama, tabelom i SVG-om (2,7 MB) postaje .docx od 232 KB; pokvaren fajl se označi kao greška i rad ide dalje.

## Šabloni vežbi (`templates.html`, `templates-store.js`)
- Izvor: 101 plan u `New Yoga Files/` (privatno, u `.gitignore`). `tools/build.py` (koristi `tools/extract.py`) pravi `shantal-templates.zip` u korenu sajta (objavljen, korisnik je 03.11.2026 tražio da šabloni budu online): `templates.json` + `img/<sha1>.<ext>`. Pokretanje: `python3 tools/build.py "New Yoga Files" shantal-templates.zip`. Svi šabloni imaju veličinu „l“ (Large).
- Spajanje sličnih (od v1.5.0): grupe imena se spajaju (union-find). Dva naziva poza (sadrže ASANA ili su pisani velikim slovima, do 4 reči) spajaju se samo ako im je naziv pre „(“/„:“ isti po `skey()` (bez akcenata, bh/b, dh/d, k/c, w/v, dupla slova; sličnost ≥ 0,9) i ako su brojevi isti (I/II/III = 1/2/3); tako se VIRABHADRĀSANA 1/2/3, ARDHA CHANDRĀSANA/CHAKRĀSANA i BHUJANGĀSANA/BHUJANGENDRĀSANA ne mešaju. Ostali nazivi: reči bez stop-reči (i bez „prānāyama“) sa tolerancijom slovnih grešaka; spajaju se pri Jaccard ≥ 0,7, ili kada je jedan naziv glavni deo drugog („Viloma“ i „Viloma (respiración a intervalos)“), ili kada je kraći (≥3 reči) gotovo ceo sadržan u dužem (najviše dvostruko dužem). Zarez ne deli naziv, da nabrajanja („Ujjayi, Viloma, bhastrika“) ne spajaju različite tehnike.
- Najnovije ima prednost: sekcija, slike i veličina iz najnovijeg plana koji ih ima; naziv je najčešća varijanta, uz malu prednost novijih planova (jednokratna slovna greška u poslednjem planu ne pobeđuje).
- Višak koji se izbacuje: „Listado de Âsanas“ (spisak, nije plan), naslovi planova, ESTUDIO (i stihovi sutri), oznake kategorija (EQUILIBRIO, Tumbados…), delovi natpisa ispod slika, koraci „1º/2º“, rečenice koje počinju malim slovom.
- Izveštaj: `python3 tools/build.py "New Yoga Files" shantal-templates.zip izvestaj.txt` piše spojene grupe i ceo spisak.
- Pravila izvlačenja: sekcije se prepoznaju po nazivu (TOMA DE CONTACTO, PARTE/FASE DINÁMICA, ĀSANAS, PRĀNĀYAMA…, RELAJACIÓN, ESTUDIO; sa ili bez broja ispred), samo ako je red velikim slovima ili podebljan; „PARTE DINÁMICA: PAVANAS CUELLO“ daje sekciju i vežbu. ESTUDIO se preskače, kao i redovi duži od 160 znakova. Ključ vežbe: bez akcenata, interpunkcije i broja ispred; nazivi pisani velikim slovima (ili sa ASANA) grupišu se po delu pre „(“ ili „:“. Prikazni naziv je najčešća varijanta. Slike i veličina iz poslednjeg plana u kome vežba ima slike. Logo se izbacuje (`looks_like_logo`, poređenje sa `logo.png`).
- Rezultat (v1.5.0): 194 šablona iz 100 planova (172 se ponavlja, 22 jednom): TOMA DE CONTACTO 16, PARTE DINÁMICA 32, ĀSANAS 120, PRĀNĀYAMA 26; 243 slike, paket 4,0 MB. Ranije (v1.4.0) bilo je 350 bez spajanja.
- Čuvanje: IndexedDB `shantal-templates`, store `tpl` (id, name, section, size, images[{blob,w,h}], uses, lastUsed, updated). Import: ako šabloni već postoje, dijalog nudi „Replace all“ (briše sve pa uvozi, tek pošto je fajl uspešno pročitan; Undo vraća stare preko `replaceAll`) ili „Add to my templates“ (spaja po id-u). Export pravi isti .zip format. Sinhronizacija: `TemplateStore.sync()` (zovu je obe stranice) radi HEAD na `shantal-templates.zip`; kad se ETag/Last-Modified razlikuje od `localStorage['shantal-templates-pack']`, preuzima paket i radi „Replace all“. Lokalne izmene važe dok se paket na sajtu ne promeni. Redosled (`sort` u store-u, važi svuda): delovi po redu iz plana, unutar dela po abecedi (`localeCompare` 'es', bez razlike za akcente i velika slova). Promene se javljaju otvorenim stranicama preko `BroadcastChannel('shantal-templates')`.
- Na sajtu (http/https), ako je baza prazna, stranica pokušava da učita `shantal-templates.zip` iz korena sajta. Taj fajl NIJE objavljen (sadrži fotografije iz planova); objavljuje se samo uz izričitu potvrdu korisnika.
- Glavna stranica: kartica „Templates“ sa `<select>` grupisanim po sekcijama (levo; između 1120 i 1400 px desno; ispod 1120 px u traci na dnu). Izbor ubacuje vežbu na kraj njene sekcije (`insertTemplate`); ako sekcija ne postoji, prvo dodaje naslov sekcije. „Undo“ vraća.

## PDF
„Save as PDF“ (⌘P) pravi `#printRoot` sa stranama `.pp` (A4, tačno 29,7 cm, `overflow:hidden`) po istom modelu kao Word (`computeLayout`, isti prelomi i smanjene slike), slike se kompresuju po izabranom kvalitetu, pa `window.print()`. `@page{margin:0}` uklanja zaglavlja browsera; margine su padding strane. Ime PDF-a = naslov dokumenta. Test: 3 strane modela daju PDF od 3 strane, 207 KB.

## Favicon
`favicon.png` (128 px) i `favicon.svg` su ruža izdvojena iz loga (najveća povezana celina + detalji unutar nje), tesno isečena, bez pozadine. SVG u tamnoj temi browsera invertuje ružu u svetlu.

## Interfejs
- Nazivi (španski): „Título de sección“ (deo, interno `deo`), „Ejercicio“ (vežba, interno `vezba`), „Añadir fotos“, veličina „Pequeño / Mediano / Grande“, kvalitet „Más ligero“ (150 dpi) / „Para imprimir“ (300 dpi), u traci na dnu kraće „Ligero / Imprimir“. Šabloni se u interfejsu zovu „ejercicios“ (kartica „Ejercicios“, „Añadir un ejercicio (194)…“, „Gestionar ejercicios“, stranica `templates.html` sa naslovom „Ejercicios“); interno (kod, IndexedDB, fajlovi) i dalje „templates“. Batch stranica: „Reducir documentos“, link „Reducir muchos archivos“.
- Nov dokument ima samo „Título del documento“; sve ispod korisnik dodaje dugmadima „Título de sección“ i „Ejercicio con fotos“ (prazna strana pokazuje kratko uputstvo `.start-hint`).
- Kontrole vežbe (Pequeño/Mediano/Grande, Añadir fotos) plutaju u malom meniju iznad reda (`.line-tools`), da ne prekrivaju centriran naziv. Na mobilnom stoje ispod naziva.
- Sekcija „Shortcuts“ je uklonjena (prečice i dalje rade).
- Slike: dugme „Add photos“, prevlačenje na vežbu ili bilo gde na stranu (nova vežba), lepljenje sa ⌘V.
- Redosled slika: prevlačenje mišem, ili fokus na sliku pa Alt + strelice. Delete uklanja.
- Tastatura: Enter dodaje novu vežbu ispod, Backspace u praznom redu ga briše, strelice gore/dole menjaju red, ⌘S čuva.
- Brisanje nema potvrdu; umesto toga obaveštenje sa dugmetom „Undo“.

## Pravila za kod
- Statične stranice bez build koraka: `index.html`, `batch.html`, `templates.html`, deljeni `templates-store.js`, `vendor/`.
- Sav tekst u interfejsu na engleskom, jasne i opisne reči. Bez crtice „—“. Komentari u kodu na engleskom.
- Okruženje je uvek tamno, u svakom browseru (korisnik tražio 03.11.2026): tamne promenljive su u `@media all{…}` posle svetlih, nezavisno od teme sistema. List papira je uvek beo.
- Vidljiv fokus za tastaturu, responsivnost do mobilnog, `prefers-reduced-motion`.

## Status
- Korisnikov izvoz iz prve verzije prikazuje se ispravno (logo, naslov, delovi, slike); nije potvrđeno da je to bio Microsoft Word. Proveren izvoz: XML ispravan, macOS Quick Look prikazuje dokument isto kao referencu.
- Testirano u Chromium-u (desktop i mobilni, svetla i tamna tema). Safari i Firefox nisu ručno testirani.

## Moguća sledeća poboljšanja (raditi samo na zahtev)
- Ručni prelom strane pre izabranog dela.
- Opis ispod vežbe.

## Excel po godinama

`shantal-yoga-ejercicios.xlsx` (objavljen): tab po godini, kolona po mesecu, vežbe redom iz plana, obojene po sekciji, logo pored naslova, zamrznuta samo prva dva reda. Pravi ga `tools/yearly_xlsx.py` (koristi nazive šablona iz `build.py`); posle novih planova pokrenuti ponovo i objaviti.
