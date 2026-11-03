// Exercise templates, shared by index.html and templates.html.
// Stored in this browser (IndexedDB "shantal-templates"); moved between browsers as a .zip pack:
// templates.json + img/*. Pages that are open at the same time hear about changes on a BroadcastChannel.
const TemplateStore = (() => {
  const SECTIONS = ['TOMA DE CONTACTO', 'PARTE DINÁMICA', 'ĀSANAS', 'PRĀNĀYAMA, MEDITACIÓN, RELAJACIÓN'];
  const channel = 'BroadcastChannel' in window ? new BroadcastChannel('shantal-templates') : null;
  let dbp;
  const db = () => dbp ||= new Promise((res, rej) => {
    const r = indexedDB.open('shantal-templates', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('tpl', { keyPath: 'id' });
    r.onsuccess = () => res(r.result);
    r.onerror = () => rej(r.error);
  });
  async function run(mode, fn) {
    const t = (await db()).transaction('tpl', mode);
    const req = fn(t.objectStore('tpl'));
    await new Promise((res, rej) => { t.oncomplete = res; t.onerror = () => rej(t.error); t.onabort = () => rej(t.error); });
    return req?.result;
  }
  const changed = () => channel?.postMessage('changed');

  // Accent-, case- and punctuation-free form, used to match section headings and names
  const plain = s => (s || '').normalize('NFKD').replace(/[̀-ͯ]/g, '').toUpperCase().replace(/[^A-Z0-9]+/g, ' ').trim();
  const sectionRank = s => { const i = SECTIONS.findIndex(x => plain(x) === plain(s)); return i < 0 ? SECTIONS.length : i; };
  const sort = list => list.sort((a, b) => sectionRank(a.section) - sectionRank(b.section) || (b.uses || 0) - (a.uses || 0) || a.name.localeCompare(b.name));

  async function all() { return sort(await run('readonly', s => s.getAll()) || []); }
  async function put(t) { t.updated = Date.now(); await run('readwrite', s => s.put(t)); changed(); }
  async function remove(id) { await run('readwrite', s => s.delete(id)); changed(); }
  const newId = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);

  const MIME = { jpeg: 'image/jpeg', jpg: 'image/jpeg', png: 'image/png', gif: 'image/gif', bmp: 'image/bmp', webp: 'image/webp' };

  // Adds the templates from a pack (a template with the same id is replaced), or replaces them all
  async function importZip(file, onProgress = () => {}, replace = false) {
    const zip = await JSZip.loadAsync(file);
    const meta = JSON.parse(await zip.file('templates.json')?.async('string') || 'null');
    if (meta?.format !== 'shantal-templates') throw new Error('This is not a templates file.');
    const list = meta.templates || [];
    if (replace) await run('readwrite', s => s.clear());   // only after the file was read successfully
    const cache = new Map();
    for (const [i, t] of list.entries()) {
      if (i % 10 === 0) onProgress(i / list.length);
      const images = [];
      for (const im of t.images || []) {
        let blob = cache.get(im.file);
        if (!blob) {
          const f = zip.file(im.file);
          if (!f) continue;
          blob = new Blob([await f.async('arraybuffer')], { type: MIME[im.file.split('.').pop().toLowerCase()] || 'image/jpeg' });
          cache.set(im.file, blob);
        }
        images.push({ blob, w: im.w, h: im.h });
      }
      await run('readwrite', s => s.put({ id: t.id || newId(), name: t.name || '', section: t.section || '', size: t.size || 'm', images, uses: t.uses || 0, lastUsed: t.lastUsed || '', updated: Date.now() }));
    }
    onProgress(1);
    changed();
    return list.length;
  }

  async function exportZip() {
    const zip = new JSZip();
    const list = await all();
    const ext = b => ({ 'image/png': 'png', 'image/gif': 'gif', 'image/bmp': 'bmp', 'image/webp': 'webp' }[b.type] || 'jpeg');
    const templates = list.map(t => ({
      id: t.id, name: t.name, section: t.section, size: t.size, uses: t.uses, lastUsed: t.lastUsed,
      images: t.images.map((im, i) => {
        const file = `img/${t.id}-${i + 1}.${ext(im.blob)}`;
        zip.file(file, im.blob);
        return { file, w: im.w, h: im.h };
      })
    }));
    zip.file('templates.json', JSON.stringify({ format: 'shantal-templates', version: 1, templates }));
    return zip.generateAsync({ type: 'blob', compression: 'DEFLATE' });
  }

  // Puts back an earlier set of templates (used by Undo after Replace all)
  async function replaceAll(list) {
    await run('readwrite', s => { s.clear(); list.forEach(t => s.put(t)); });
    changed();
  }

  function onChange(fn) {
    channel?.addEventListener('message', fn);
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') fn(); });
  }

  return { SECTIONS, plain, all, put, remove, newId, importZip, exportZip, replaceAll, onChange };
})();
