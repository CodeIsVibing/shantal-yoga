"""Build shantal-templates.zip: one template per exercise found in the plans, repeated or not.

Similar names are merged into one template (accents, punctuation, numbering, small spelling
differences and extra words in brackets do not matter). The newest plan wins: a template takes
its name, section and photos from the most recent plan that has them. Every template uses Large photos.

Usage: python3 tools/build.py "New Yoga Files" shantal-templates.zip [report.txt]
"""
import sys, re, glob, json, hashlib, zipfile, unicodedata, collections, io, os, difflib
sys.path.insert(0, os.path.dirname(__file__))
from extract import parse
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
REPORT = sys.argv[3] if len(sys.argv) > 3 else None
ORDER = ['TOMA DE CONTACTO', 'PARTE DINÁMICA', 'ĀSANAS', 'PRĀNĀYAMA, MEDITACIÓN, RELAJACIÓN']


def plain(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).upper()


SECTIONS = [(r'^(\d+\.|[A-D]\.)?\s*TOMA DE CONTACTO', 'TOMA DE CONTACTO'),
            (r'^(\d+\.|[A-D]\.)?\s*(PARTE|FASE) DINAMICA', 'PARTE DINÁMICA'),
            (r'^(\d+\.|[A-D]\.)?\s*ASANAS\b', 'ĀSANAS'),
            (r'^(\d+\.|[A-D]\.)?\s*PRANAYAMA[\s,]*(MEDI\w*CION)?[\s,]*(Y\s+)?(RELAJACION)?\.?', 'PRĀNĀYAMA, MEDITACIÓN, RELAJACIÓN'),
            (r'^RELAJACION\.?$', 'PRĀNĀYAMA, MEDITACIÓN, RELAJACIÓN'),
            (r'^ESTUDIO\b', 'ESTUDIO')]


def section_of(text):
    p = plain(text).strip()
    for rx, name in SECTIONS:
        m = re.match(rx, p)
        if m:
            return name, (text[m.end():].lstrip(' :.-').strip() if name != 'ESTUDIO' else ''), m.end()
    return None, None, 0


NUM = re.compile(r'^\s*\d+\s*[.)-]\s*')
STOP = set('EL LA LOS LAS DE DEL Y E A AL EN CON POR PARA UN UNA O SU SUS SE LO QUE MI PRANAYAMA'.split())


def clean_name(t):
    t = re.sub(r'^[^\w(¿¡]+', '', t)
    return re.sub(r'\s*[:.,;]\s*$', '', NUM.sub('', t)).strip()


ROMAN = {'I': '1', 'II': '2', 'III': '3', 'IV': '4'}


def tokens(s):
    return [ROMAN.get(w, w) for w in re.split(r'[^A-Z0-9]+', plain(s)) if w and w not in STOP]


def same_word(a, b):
    if a == b:
        return True
    if a.isdigit() or b.isdigit():
        return False
    short, long_ = sorted((a, b), key=len)
    if len(short) >= 3 and long_.startswith(short) and len(long_) - len(short) <= 2:     # LOT / LOTO, ALTERNA / ALTERNADA
        return True
    return min(len(a), len(b)) >= 5 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.9


def matched(a, b):
    """How many words of a have a (fuzzy) partner in b."""
    left = list(b)
    n = 0
    for w in a:
        for i, v in enumerate(left):
            if same_word(w, v):
                n += 1
                del left[i]
                break
    return n


def base_of(name):
    return re.split(r'[(:.]', NUM.sub('', name))[0]


def skey(words):
    """Pose name as one string that ignores transliteration: bh/b, dh/d, k/c, w/v and doubled letters."""
    s = ''.join(words).replace('K', 'C').replace('W', 'V')
    s = re.sub(r'([BCDGJPST])H', r'\1', s)
    return re.sub(r'(.)\1+', r'\1', s)


def is_pose_name(base):
    words = [w for w in re.findall(r'[^\W\d_]+', base)]
    return 'ASANA' in plain(base) or (bool(words) and 0 < len(tokens(base)) <= 4 and all(w.isupper() or plain(w) in STOP for w in words))


def similar(a, b):
    ta, tb = a['tok'], b['tok']
    if not ta or not tb:
        return False
    # Pose names: the same name before "(" or ":" is the same exercise, whatever the translation says
    ba, bb = a['base'], b['base']
    if a['sanskrit'] and b['sanskrit']:              # two pose names: only the same pose name counts
        if not ba or not bb or [w for w in ba if w.isdigit()] != [w for w in bb if w.isdigit()]:
            return False
        return difflib.SequenceMatcher(None, skey(ba), skey(bb)).ratio() >= 0.9
    # "Viloma" and "Viloma (respiración a intervalos)": a name that is the other one's main part
    for x, y in ((a, b), (b, a)):
        if y['base'] and len(y['base']) < len(y['tok']) and len(x['tok']) == len(y['base']) and matched(x['tok'], y['base']) == len(x['tok']):
            return True
    m = matched(ta, tb) if len(ta) <= len(tb) else matched(tb, ta)
    small, big = sorted((len(ta), len(tb)))
    if m / (small + big - m) >= 0.7:
        return True
    return small >= 3 and big <= 2 * small and m / small >= 0.85


def doc_rank(path):
    m = re.match(r'(\d{4}) (\d{2})', os.path.basename(path))
    return int(m.group(1)) * 100 + int(m.group(2)) if m else 0      # undated files count as the oldest


# ---------- Read every plan ----------
_logo = Image.open(os.path.join(os.path.dirname(__file__), '..', 'logo.png')).convert('RGBA')
_bg = Image.new('RGBA', _logo.size, 'white'); _bg.paste(_logo, (0, 0), _logo)
LOGO_REF = list(_bg.convert('L').resize((64, 24)).getdata())


def looks_like_logo(im):
    """The logo sometimes sits after the first line of text; never use it as an exercise photo."""
    if not 2.3 < im.width / im.height < 3.2:
        return False
    g = list(im.convert('L').resize((64, 24)).getdata())
    d = min(sum(abs(x - y) for x, y in zip(g, LOGO_REF)), sum(abs(255 - x - y) for x, y in zip(g, LOGO_REF))) / len(g)
    return d < 30


# Only session plans: the asana catalogue ("Listado de Âsanas") is a reference list, not a plan
docs = sorted((f for f in glob.glob(SRC + '/*.docx') if not plain(os.path.basename(f)).startswith('LISTADO')), key=lambda f: (doc_rank(f), f))
# Headings and labels that are not exercises
JUNK = re.compile(r'^(SESION DE YOGA|LISTADO DE|ESTUDIO)|^\(|^\d+ [A-Z]|^\d+\s?[ºO°] |^(SIDDHASANA VAJRASANA|PRANATASANA NINO)|^(TUMBADOS|SENTADOS|DE PIE|BOCA ABAJO|EQUILIBRIO|EXTENSIONES|FLEXIONES|FUERZA|INVERTIDAS|LATERALIZACIONES|TORSIONES|RELAJACION|POSTURA|RESPIRACION|MANTRAS)$')
groups = collections.OrderedDict()          # exact key -> occurrences
for f in docs:
    z, title, blocks = parse(f)
    sec = ''
    for b in blocks:
        name, rest, end = section_of(b['text']) if b['text'] else (None, None, 0)
        letters = [c for c in b['text'] if c.isalpha()]
        upper = sum(c.isupper() for c in letters) / max(1, len(letters))
        head = b['text'][:end]
        head_letters = [c for c in head if c.isalpha()]
        head_upper = sum(c.isupper() for c in head_letters) / max(1, len(head_letters))
        if name and (len(b['text']) < 60 or head_upper >= 0.8) and (b['type'] == 'deo' or upper >= 0.8 or head_upper >= 0.8 or not rest):
            sec = name
            if not rest:
                continue
            b = dict(b, text=rest)
        text = clean_name(b['text'])
        if sec == 'ESTUDIO' or len(text) > 160 or len(re.sub(r'[^A-Za-zÀ-ÿĀ-ž]', '', text)) < 3 or JUNK.search(plain(text).strip()) or text[:1].islower():
            continue
        k = ' '.join(tokens(text))
        if not k:
            continue
        groups.setdefault(k, []).append({'rank': doc_rank(f), 'doc': f, 'name': text, 'section': sec or 'ĀSANAS', 'images': b['images']})

# ---------- Merge similar names (union-find) ----------
items = []
for k, occ in groups.items():
    newest = max(occ, key=lambda o: o['rank'])
    base = base_of(newest['name'])
    items.append({'key': k, 'occ': occ, 'tok': tokens(newest['name']), 'base': tokens(base),
                  'sanskrit': is_pose_name(base)})
parent = list(range(len(items)))


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


for i in range(len(items)):
    for j in range(i + 1, len(items)):
        if find(i) != find(j) and similar(items[i], items[j]):
            parent[find(j)] = find(i)
clusters = collections.defaultdict(list)
for i, it in enumerate(items):
    clusters[find(i)].append(it)

# ---------- One template per cluster; the newest plan wins ----------
pack = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
seen_imgs, zips, templates, report = {}, {}, [], []
for members in clusters.values():
    occ = sorted((o for m in members for o in m['occ']), key=lambda o: o['rank'])
    newest = occ[-1]
    imgs = []
    for o in reversed(occ):                                  # newest plan that has usable photos
        if not o['images']:
            continue
        z = zips.setdefault(o['doc'], zipfile.ZipFile(o['doc']))
        found = []
        for path, hcm, wcm in o['images']:
            try:
                data = z.read(path)
            except KeyError:
                continue
            ext = path.rsplit('.', 1)[-1].lower()
            if ext not in ('png', 'jpeg', 'jpg', 'gif', 'bmp'):
                continue
            try:
                im = Image.open(io.BytesIO(data)); w, h = im.size
            except Exception:
                continue
            if looks_like_logo(im):
                continue
            hsh = hashlib.sha1(data).hexdigest()[:16]
            fn = f'img/{hsh}.{"jpeg" if ext == "jpg" else ext}'
            if hsh not in seen_imgs:
                pack.writestr(fn, data); seen_imgs[hsh] = fn
            found.append({'file': fn, 'w': w, 'h': h})
        if found:
            imgs = found
            break
    used_in = sorted({o['doc'] for o in occ}, key=doc_rank)
    key = ' '.join(sorted(m['key'] for m in members))
    # Name: the most used spelling, newer plans count a little more, so a one-off typo in the latest plan does not win
    top = max(o['rank'] for o in occ) or 1
    score = collections.Counter()
    for o in occ:
        score[o['name']] += 1 + (o['rank'] / top) ** 8
    name = max(score.items(), key=lambda kv: (kv[1], -len(kv[0])))[0]
    templates.append({'id': hashlib.sha1(key.encode()).hexdigest()[:10], 'name': name, 'section': newest['section'],
                      'size': 'l', 'images': imgs, 'uses': len(used_in), 'lastUsed': os.path.basename(used_in[-1]).replace('.docx', '')})
    if len(members) > 1:
        report.append(f"{name}  <=  " + ' | '.join(sorted({o['name'] for o in occ} - {name})))

templates.sort(key=lambda t: (ORDER.index(t['section']) if t['section'] in ORDER else 9, -t['uses'], t['name']))
pack.writestr('templates.json', json.dumps({'format': 'shantal-templates', 'version': 2, 'templates': templates}, ensure_ascii=False, indent=1))
pack.close()

rep = sum(1 for t in templates if t['uses'] > 1)
print(f'docs {len(docs)}  names {len(items)}  templates {len(templates)}  merged groups {len(report)}  repeated {rep}  once {len(templates) - rep}  '
      f'images {len(seen_imgs)}  with photos {sum(1 for t in templates if t["images"])}  pack {os.path.getsize(OUT) / 1048576:.1f} MB')
if REPORT:
    with open(REPORT, 'w') as fh:
        fh.write('MERGED\n' + '\n'.join(sorted(report)) + '\n\nALL\n')
        fh.write('\n'.join(f"{t['section'][:12]:12} {t['uses']:>3}x {len(t['images']):>2}img  {t['name']}" for t in templates))
