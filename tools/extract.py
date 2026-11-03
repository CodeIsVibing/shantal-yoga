"""Parse Shantal Yoga .docx plans into title / sections / exercises with image refs (same rules as openDocx)."""
import sys, re, zipfile, posixpath
from xml.etree import ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
WP='{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
V='{urn:schemas-microsoft-com:vml}'
def on(el):
    if el is None: return False
    v=el.get(W+'val'); return v not in ('0','false','none')
def parse(path):
    z=zipfile.ZipFile(path)
    rels={}
    try:
        for r in ET.fromstring(z.read('word/_rels/document.xml.rels')):
            if r.get('TargetMode')=='External': continue
            rels[r.get('Id')]=posixpath.normpath(posixpath.join('word',r.get('Target')))
    except KeyError: pass
    root=ET.fromstring(z.read('word/document.xml'))
    body=root.find(W+'body')
    title=''; blocks=[]; seen=False
    for p in body.iter(W+'p'):
        st=p.find(f'{W}pPr/{W}pStyle'); style=(st.get(W+'val') if st is not None else '').lower().replace(' ','')
        text=''
        for n in p.iter():
            if n.tag==W+'t' and n.text: text+=n.text
            elif n.tag==W+'tab': text+=' '
        text=re.sub(r'\s+',' ',text).strip()
        if not re.search(r'\w',text): text=''
        runs=[r for r in p.iter(W+'r') if ''.join(t.text or '' for t in r.iter(W+'t')).strip()]
        def every(tag): return bool(runs) and all(on(r.find(f'{W}rPr/{W}{tag}')) for r in runs)
        imgs=[]
        for d in p.iter(W+'drawing'):
            blip=d.find(f'.//{A}blip'); ext=d.find(f'.//{WP}extent')
            if blip is None or ext is None: continue
            cx,cy=int(ext.get('cx')),int(ext.get('cy'))
            if cx<72000 or cy<72000: continue
            t=rels.get(blip.get(R+'embed'))
            if t: imgs.append((t,cy/360000,cx/360000))
        for im in p.iter(V+'imagedata'):
            t=rels.get(im.get(R+'id'))
            if t: imgs.append((t,0,0))
        if text:
            if not title and not blocks and (style=='title' or (not style.startswith('heading') and every('b') and not every('u'))): title=text
            elif style=='heading1' or (every('b') and every('u')): blocks.append({'type':'deo','text':text,'images':[]})
            else: blocks.append({'type':'vezba','text':text,'images':[]})
            seen=True
        if imgs and seen:
            if not blocks or blocks[-1]['type']!='vezba': blocks.append({'type':'vezba','text':'','images':[]})
            blocks[-1]['images']+=imgs
    return z,title,blocks
if __name__=='__main__':
    for f in sys.argv[1:]:
        z,t,b=parse(f); print('##',f.split('/')[-1],'|',t)
        for x in b: print('  ','==' if x['type']=='deo' else '  ',x['text'][:70],len(x['images']) or '')
