# Shantal Yoga · Photos to Word

## Šta je projekat
Statična web stranica (`index.html`) za pravljenje Word dokumenta po uzoru na mesečne planove časa „Shantal Yoga“ (referenca: `~/Downloads/2025 02 Febrero_compressed.docx`). Interfejs je na engleskom („Photos to Word“). Raspored u tri kolone: levo Outline (pregled dokumenta, klik skače na red), u sredini A4 strana na kojoj se uređuje direktno, desno panel Document (broj delova/vežbi/slika, kvalitet, ime fajla, procena veličine, **Download Word file**, prečice). Na užim ekranima levi panel nestaje (<1400 px), pa i desni (<1120 px) i tada izvoz ide preko plutajuće trake na dnu.

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
- U Word-u: desno poravnat, širina 8 cm, iznad naslova.

## Dokument (kao referenca)
- A4, levo/desno 3 cm, gore/dole 2,5 cm. Font Arial, crna boja.
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

## Interfejs
- Nazivi: „Section heading“ (deo, interno `deo`), „Exercise“ (vežba, interno `vezba`), „Add photos“, veličina „Small / Medium / Large“, kvalitet „Smaller file“ (150 dpi) / „Print quality“ (300 dpi).
- Nov dokument počinje sa četiri dela iz reference (`STARTER_SECTIONS`) i praznom vežbom ispod svakog.
- Slike: dugme „Add photos“, prevlačenje na vežbu ili bilo gde na stranu (nova vežba), lepljenje sa ⌘V.
- Redosled slika: prevlačenje mišem, ili fokus na sliku pa Alt + strelice. Delete uklanja.
- Tastatura: Enter dodaje novu vežbu ispod, Backspace u praznom redu ga briše, strelice gore/dole menjaju red, ⌘S čuva.
- Brisanje nema potvrdu; umesto toga obaveštenje sa dugmetom „Undo“.

## Pravila za kod
- Ostati na jednom statičnom HTML fajlu (plus `vendor/`) osim ako korisnik ne traži drugačije.
- Sav tekst u interfejsu na engleskom, jasne i opisne reči. Bez crtice „—“. Komentari u kodu na engleskom.
- Svetla i tamna tema za okruženje; list papira je uvek beo.
- Vidljiv fokus za tastaturu, responsivnost do mobilnog, `prefers-reduced-motion`.

## Status
- Korisnikov izvoz iz prve verzije prikazuje se ispravno (logo, naslov, delovi, slike); nije potvrđeno da je to bio Microsoft Word. Proveren izvoz: XML ispravan, macOS Quick Look prikazuje dokument isto kao referencu.
- Testirano u Chromium-u (desktop i mobilni, svetla i tamna tema). Safari i Firefox nisu ručno testirani.

## Moguća sledeća poboljšanja (raditi samo na zahtev)
- Ručni prelom strane pre izabranog dela.
- Opis ispod vežbe.
