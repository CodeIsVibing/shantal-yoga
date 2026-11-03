"""Build shantal-templates.zip: one template per exercise found in the plans, repeated or not.

Usage: python3 tools/build.py "New Yoga Files" templates-pack/shantal-templates.zip
"""
import sys, re, glob, json, hashlib, zipfile, unicodedata, collections, io, os
sys.path.insert(0, os.path.dirname(__file__))
from extract import parse
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
def plain(s): return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).upper()
SECTIONS = [(r'^(\d+\.|[A-D]\.)?\s*TOMA DE CONTACTO', 'TOMA DE CONTACTO'), (r'^(\d+\.|[A-D]\.)?\s*(PARTE|FASE) DINAMICA', 'PARTE DINÁMICA'),
            (r'^(\d+\.|[A-D]\.)?\s*ASANAS\b', 'ĀSANAS'), (r'^(\d+\.|[A-D]\.)?\s*PRANAYAMA[\s,]*(MEDI\w*CION)?[\s,]*(Y\s+)?(RELAJACION)?\.?', 'PRĀNĀYAMA, MEDITACIÓN, RELAJACIÓN'),
            (r'^RELAJACION\.?$', 'PRĀNĀYAMA, MEDITACIÓN, RELAJACIÓN'), (r'^ESTUDIO\b', 'ESTUDIO')]
def section_of(text):
    p = plain(text).strip()
    for rx, name in SECTIONS:
        m = re.match(rx, p)
        if m: return name, text[m.end():].lstrip(' :.-').strip() if name != 'ESTUDIO' else ''
    return None, None
NUM = re.compile(r'^\s*\d+\s*[.)-]\s*')
def key_of(name):
    name = NUM.sub('', name)
    p = plain(name)
    base_orig = re.split(r'[(:]', name)[0]
    if base_orig.upper() == base_orig or 'ASANA' in plain(base_orig):   # uppercase sanskrit names: group by the part before "(" or ":"
        p = plain(base_orig)
    return re.sub(r'[^A-Z0-9]+', '', p)
SIZES = {'s': 2.6, 'm': 4, 'l': 6}
# The logo sometimes sits after the first line of text; never use it as an exercise photo
_logo = Image.open(os.path.join(os.path.dirname(__file__), '..', 'logo.png')).convert('RGBA')
_bg = Image.new('RGBA', _logo.size, 'white'); _bg.paste(_logo, (0, 0), _logo)
LOGO_REF = list(_bg.convert('L').resize((64, 24)).getdata())
def looks_like_logo(im):
    if not 2.3 < im.width / im.height < 3.2: return False
    g = list(im.convert('L').resize((64, 24)).getdata())
    d = min(sum(abs(x - y) for x, y in zip(g, LOGO_REF)), sum(abs(255 - x - y) for x, y in zip(g, LOGO_REF))) / len(g)
    return d < 30
groups = collections.OrderedDict()
docs = sorted(glob.glob(SRC + '/*.docx'))
for f in docs:
    z, title, blocks = parse(f)
    sec = ''
    for b in blocks:
        name, rest = section_of(b['text']) if b['text'] else (None, None)
        letters = [c for c in b['text'] if c.isalpha()]
        upper = sum(c.isupper() for c in letters) / max(1, len(letters))
        if name and len(b['text']) < 60 and (b['type'] == 'deo' or upper >= 0.8 or not rest):
            sec = name
            if not rest: continue
            b = dict(b, text=rest)
        if sec == 'ESTUDIO' or not b['text'] or len(b['text']) > 160: continue
        k = key_of(b['text'])
        if len(k) < 3: continue
        g = groups.setdefault(k, {'names': collections.Counter(), 'sections': collections.Counter(), 'docs': [], 'occ': []})
        g['names'][re.sub(r'\s*[:.]\s*$', '', NUM.sub('', b['text'])).strip()] += 1
        g['sections'][sec or 'ĀSANAS'] += 1
        if os.path.basename(f) not in g['docs']: g['docs'].append(os.path.basename(f))
        g['occ'].append((f, b['images']))
pack = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
seen_imgs = {}; templates = []
zips = {}
for k, g in groups.items():
    with_img = [o for o in g['occ'] if o[1]]
    imgs = []; size = 'm'
    if with_img:
        f, refs = with_img[-1]                       # latest plan that has photos for this exercise
        z = zips.setdefault(f, zipfile.ZipFile(f))
        hs = []
        for path, hcm, wcm in refs:
            try: data = z.read(path)
            except KeyError: continue
            ext = path.rsplit('.', 1)[-1].lower()
            if ext not in ('png', 'jpeg', 'jpg', 'gif', 'bmp'): continue
            try: im = Image.open(io.BytesIO(data)); w, h = im.size
            except Exception: continue
            if looks_like_logo(im): continue
            hsh = hashlib.sha1(data).hexdigest()[:16]
            fn = f'img/{hsh}.{ "jpeg" if ext == "jpg" else ext}'
            if hsh not in seen_imgs: pack.writestr(fn, data); seen_imgs[hsh] = fn
            imgs.append({'file': fn, 'w': w, 'h': h}); hs.append(hcm)
        if hs and max(hs): size = min(SIZES, key=lambda s: abs(SIZES[s] - max(hs)))
    name = max(g['names'].items(), key=lambda kv: (kv[1], -len(kv[0])))[0]
    templates.append({'id': hashlib.sha1(k.encode()).hexdigest()[:10], 'name': name, 'section': g['sections'].most_common(1)[0][0],
                      'size': size, 'images': imgs, 'uses': len(g['docs']), 'lastUsed': g['docs'][-1].replace('.docx', '')})
order = ['TOMA DE CONTACTO', 'PARTE DINÁMICA', 'ĀSANAS', 'PRĀNĀYAMA, MEDITACIÓN, RELAJACIÓN']
templates.sort(key=lambda t: (order.index(t['section']) if t['section'] in order else 9, -t['uses'], t['name']))
pack.writestr('templates.json', json.dumps({'format': 'shantal-templates', 'version': 1, 'templates': templates}, ensure_ascii=False, indent=1))
pack.close()
rep = sum(1 for t in templates if t['uses'] > 1)
print(f'docs {len(docs)}  templates {len(templates)}  repeated {rep}  once {len(templates)-rep}  images {len(seen_imgs)}  with photos {sum(1 for t in templates if t["images"])}  pack {os.path.getsize(OUT)/1048576:.1f} MB')
for sct in order:
    ts = [t for t in templates if t['section'] == sct]
    print(f'\n[{sct}] {len(ts)}')
    for t in ts[:14]: print(f"  {t['uses']:>3}x {len(t['images']):>2}img {t['size']}  {t['name'][:70]}")
