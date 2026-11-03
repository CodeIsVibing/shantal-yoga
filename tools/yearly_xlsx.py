"""Build the yearly exercises workbook: one sheet per year, one column per month, exercises colored by plan section.

Names are the merged template names from build.py, so the same exercise reads the same everywhere.
Usage: python3 tools/yearly_xlsx.py . shantal-yoga-ejercicios.xlsx /tmp/pack.zip   (the last file is a throwaway pack)
"""
import sys, os, re, runpy, collections
P, OUT, TMP = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, P + '/tools')
import extract
pos = {}
_parse = extract.parse
def parse(path):
    z, t, blocks = _parse(path)
    for i, b in enumerate(blocks): pos[id(b['images'])] = i
    return z, t, blocks
extract.parse = parse
sys.argv = ['build.py', P + '/New Yoga Files', TMP]
g = runpy.run_path(P + '/tools/build.py')
ORDER = g['ORDER']
per_doc = collections.defaultdict(list)
for members in g['clusters'].values():
    occ = [o for m in members for o in m['occ']]
    top = max(o['rank'] for o in occ) or 1
    score = collections.Counter()
    for o in occ: score[o['name']] += 1 + (o['rank'] / top) ** 8
    name = max(score.items(), key=lambda kv: (kv[1], -len(kv[0])))[0]
    for o in occ: per_doc[o['doc']].append((pos[id(o['images'])], name, o['section']))
MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
years = collections.defaultdict(dict)
for doc, items in per_doc.items():
    m = re.match(r'(\d{4}) (\d{2})', os.path.basename(doc))
    if not m: continue
    seen, out = set(), []
    for _, n, sec in sorted(items):
        if n not in seen: seen.add(n); out.append((n, sec))
    years[int(m.group(1))][int(m.group(2))] = out

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XImage
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.page import PageMargins
from openpyxl.workbook.properties import CalcProperties
EMU = 9525
INK, MUTED, HEAD, LINE = '1D1D1F', '86868B', '2C2C2E', 'FFFFFF'
# Section tint (cell) and strong color (left bar + legend); names as in the plans
SEC = {'TOMA DE CONTACTO': ('EAF2FB', '4A86C5'), 'PARTE DINÁMICA': ('FDF0E2', 'D9822B'),
       'ĀSANAS': ('EAF5EA', '4E9A55'), 'PRĀNĀYAMA, MEDITACIÓN, RELAJACIÓN': ('F1ECF8', '8467B3')}
LABEL = {'TOMA DE CONTACTO': 'Toma de contacto', 'PARTE DINÁMICA': 'Parte dinámica', 'ĀSANAS': 'Āsanas',
         'PRĀNĀYAMA, MEDITACIÓN, RELAJACIÓN': 'Prānāyama, meditación, relajación'}
white = Side(style='thin', color=LINE)
COLW = 30; COLPX = int(COLW * 7 + 5)
LOGO_H = 24; LOGO_W = round(LOGO_H * 944 / 346)
wb = Workbook(); wb.remove(wb.active)
for y in sorted(years):
    ws = wb.create_sheet(str(y))
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = HEAD
    months = sorted(years[y]); last = len(months) + 1
    ws.column_dimensions['A'].width = 4.5
    for c in range(2, last + 1): ws.column_dimensions[L(c)].width = COLW
    # Row 1: title, logo right after it
    ws.row_dimensions[1].height = 30
    ws['B1'] = f'Sesiones de yoga · {y}'
    ws['B1'].font = Font(name='Arial', size=13, bold=True, color=INK)
    ws['B1'].alignment = Alignment(vertical='center')
    logo = XImage(P + '/logo.png')
    logo.anchor = OneCellAnchor(_from=AnchorMarker(col=2, colOff=4 * EMU, row=0, rowOff=8 * EMU),
                                ext=XDRPositiveSize2D(LOGO_W * EMU, LOGO_H * EMU))
    ws.add_image(logo)
    # Row 2: months
    H = 2
    ws.row_dimensions[H].height = 24
    for text, col in [('Nº', 'A')] + [(MESES[m - 1], L(i + 2)) for i, m in enumerate(months)]:
        c = ws[f'{col}{H}']; c.value = text
        c.font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor=HEAD)
        c.alignment = Alignment(horizontal='center', vertical='center')
    rows = max(len(years[y][m]) for m in months)
    for i in range(rows):
        r = H + 1 + i
        c = ws.cell(r, 1, i + 1)
        c.font = Font(name='Arial', size=9, color=MUTED); c.alignment = Alignment(horizontal='center', vertical='top')
        for j, m in enumerate(months):
            items = years[y][m]
            c = ws.cell(r, j + 2)
            c.alignment = Alignment(wrap_text=True, vertical='top', indent=1)
            c.font = Font(name='Arial', size=10, color=INK)
            if i < len(items):
                n, sec = items[i]
                tint, strong = SEC.get(sec, ('F5F5F7', '86868B'))
                c.value = n
                c.fill = PatternFill('solid', fgColor=tint)
                c.border = Border(left=Side(style='thick', color=strong), bottom=white, top=white)
    T = H + rows + 1
    ws.row_dimensions[T].height = 24
    c = ws.cell(T, 1, 'Σ'); c.font = Font(name='Arial', size=10, bold=True, color=MUTED); c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = Border(top=Side(style='medium', color=HEAD))
    for j in range(len(months)):
        col = L(j + 2)
        c = ws.cell(T, j + 2, f'=COUNTA({col}{H + 1}:{col}{T - 1})&" ejercicios"')
        c.font = Font(name='Arial', size=10, bold=True, color=INK)
        c.alignment = Alignment(horizontal='left', vertical='center', indent=1)
        c.border = Border(top=Side(style='medium', color=HEAD))
    # Legend under the table
    r = T + 2
    ws.cell(r, 2, 'Secciones del plan').font = Font(name='Arial', size=10, bold=True, color=MUTED)
    for k, (sec, (tint, strong)) in enumerate(SEC.items()):
        c = ws.cell(r + 1 + k, 2, LABEL[sec])
        c.font = Font(name='Arial', size=10, color=INK)
        c.fill = PatternFill('solid', fgColor=tint)
        c.alignment = Alignment(indent=1, vertical='center')
        c.border = Border(left=Side(style='thick', color=strong), bottom=white)
        ws.row_dimensions[r + 1 + k].height = 20
    ws.freeze_panes = f'B{H + 1}'
    ws.print_title_rows = f'{H}:{H}'
    ws.page_setup.orientation = 'landscape'; ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.5, bottom=0.5)
    ws.oddFooter.center.text = f'Shantal Yoga · {y} · &P / &N'
wb.active = len(wb.sheetnames) - 1
wb.calculation = CalcProperties(fullCalcOnLoad=True)
wb.save(OUT)
secs = collections.Counter(s for ms in years.values() for items in ms.values() for _, s in items)
print('ok', len(wb.sheetnames), dict(secs))
