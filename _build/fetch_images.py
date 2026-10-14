"""Stáhne obrázky ze starého webu do img/wp/ (max 1600 px), mapu url -> soubor do _research/img_map.json."""
import json, os, re, sys, hashlib, unicodedata, urllib.parse, subprocess, concurrent.futures as cf
from PIL import Image, ImageOps
urls = json.load(open(sys.argv[1]))
OUT = 'img/wp'; os.makedirs(OUT, exist_ok=True)
mp = json.load(open('_research/img_map.json')) if os.path.exists('_research/img_map.json') else {}
def name(u):
    b = urllib.parse.unquote(u.split('/')[-1])
    b = unicodedata.normalize('NFKD', b).encode('ascii', 'ignore').decode()
    stem, ext = os.path.splitext(b)
    stem = re.sub(r'[^A-Za-z0-9]+', '-', stem).strip('-').lower()[:60] or 'img'
    return f"{stem}-{hashlib.sha1(u.encode()).hexdigest()[:6]}{ext.lower() if ext.lower() in ('.jpg','.jpeg','.png','.webp') else '.jpg'}"
def get(u):
    if u in mp and os.path.exists(os.path.join(OUT, mp[u])): return u, mp[u]
    fn = name(u); p = os.path.join(OUT, fn)
    r = subprocess.run(['curl', '-sfL', '-A', 'Mozilla/5.0', '--max-time', '60', '-o', p, u])
    if r.returncode or not os.path.exists(p): return u, None
    try:
        im = ImageOps.exif_transpose(Image.open(p)); im.load()
        if max(im.size) > 1600:
            im.thumbnail((1600, 1600), Image.LANCZOS)
            if fn.endswith(('.jpg', '.jpeg')) and im.mode != 'RGB': im = im.convert('RGB')
            im.save(p, quality=86)
    except Exception as e:
        os.remove(p); return u, None
    return u, fn
with cf.ThreadPoolExecutor(8) as ex:
    for u, fn in ex.map(get, urls):
        if fn: mp[u] = fn
        else: print('CHYBA', u)
json.dump(mp, open('_research/img_map.json', 'w'), indent=0, ensure_ascii=False)
print(len(mp), 'obrázků')
