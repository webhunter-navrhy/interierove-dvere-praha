"""Z obsahu dvere-vascodoors.cz (_research/) vyrobí _data/models.json, pages.json, realizace.json.

  python3 _build/wp2json.py dvere-vascodoors.cz _research/raw_pages.json _research/pages_raw_blocks.json
  python3 _build/make_data.py
Texty se přebírají 1:1, mění se jen sazba. Obrázky přes _research/img_map.json (img/wp/).
"""
import html
import json
import re

from bs4 import BeautifulSoup

R = '_research/'
OLD = 'https://www.dvere-vascodoors.cz'
raw = {p['id']: p for p in json.load(open(R + 'pages_raw_blocks.json'))}
imap = json.load(open(R + 'img_map.json'))


def meta(pid):
    h = open(f'{R}html/{pid}.html', errors='ignore').read()
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', h)
    return (html.unescape(t.group(1).strip()) if t else ''), (html.unescape(d.group(1)) if d else '')


def im(u):
    return ('wp/' + imap[u]) if u in imap else None


def fix_links(s):
    s = s.replace('href="@/sortiment-dveri/stavebni-pouzdra/"', 'href="@/stavebni-pouzdra/"')
    s = re.sub(r'href="/(?!/)', 'href="@/', s)
    s = re.sub(r'href="@/([^"]+\.(?:pdf|html))"', lambda m: f'href="{OLD}/{m.group(1)}"', s)
    s = s.replace('?utm_source=chatgpt.com', '')
    return s


PLAIN = re.compile(r'^[^<]{1,45}$')


def clean_blocks(blocks):
    """Mapování obrázků, odkazů a rozpoznání nadtitulků / čísel kroků / otázek FAQ."""
    out = []
    for i, b in enumerate(blocks):
        b = dict(b)
        nxt = blocks[i + 1] if i + 1 < len(blocks) else None
        if b['t'] == 'img':
            b['src'] = im(b['src'])
            if not b['src']:
                continue
        if b['t'] == 'gallery':
            items = [dict(x, src=im(x['src'])) for x in b['items'] if im(x['src'])]
            seen, uniq = set(), []
            for x in items:
                if x['src'] not in seen:
                    seen.add(x['src']); uniq.append(x)
            if not uniq:
                continue
            b['items'] = uniq
        if b['t'] == 'cards':
            for x in b['items']:
                x['img'] = im(x['img']) if x.get('img') else None
                if x.get('href'):
                    x['href'] = fix_links(f'href="{x["href"]}"')[6:-1]
        if b['t'] in ('p',):
            b['h'] = fix_links(b['h'])
            txt = b['h'].strip()
            if re.fullmatch(r'\d', txt) and nxt and nxt['t'] == 'h':
                b['t'] = 'num'
            elif PLAIN.match(txt) and not txt.endswith(('.', ':', '?', '!', ')')) and nxt and (
                    nxt['t'] == 'h' or (nxt['t'] == 'p' and PLAIN.match(nxt['h'].strip() or 'x') and i + 2 < len(blocks) and blocks[i + 2]['t'] == 'h')):
                b['t'] = 'kicker'
            elif txt.endswith('?') and '<' not in txt and len(txt) < 160 and nxt and nxt['t'] == 'p':
                b['t'] = 'q'
        if b['t'] in ('ul', 'ol'):
            b['items'] = [fix_links(x) for x in b['items']]
        if b['t'] == 'table':
            b['rows'] = [[fix_links(c) for c in r] for r in b['rows']]
        if b['t'] == 'btn':
            b['href'] = fix_links(f'href="{b["href"]}"')[6:-1]
        out.append(b)
    # sloučit nadtitulek + další nadtitulek (např. „POSTUP“ + „Jak probíhá spolupráce“) -> jeden
    res = []
    for b in out:
        if b['t'] == 'kicker' and res and res[-1]['t'] == 'kicker':
            res[-1]['h'] = b['h']
            continue
        res.append(b)
    return res


# ---------- modely ----------
KATALOG = [  # pořadí a krátké popisy z /dvere-interierove/
    (9262, 'Braga', 'folie', 'Robustní model s výraznou strukturou povrchu a možností falcového, bezfalcového i posuvného provedení.', 'Braga'),
    (9297, 'Evora', 'folie', 'Elegantní model s přírodní inspirací a jemnou strukturou povrchu pro moderní i klasické interiéry.', 'Evora'),
    (9364, 'Ibiza', 'folie', 'Lehký a svěží model s hladkým povrchem, vhodný pro moderní a světlé interiéry.', 'Ibiza'),
    (9382, 'Leon', 'folie', 'Moderní a dynamický design kombinující jednoduchost s výraznou strukturou povrchu.', 'Leon'),
    (9280, 'Santiago', 'folie', 'Nadčasově elegantní dveře s čistými liniemi, minimalistickým designem a decentním dekorem.', 'Santiago'),
    (14766, 'Malaga', 'folie', 'Model s jemným a výrazným dekorem s přírodními prvky pro útulný a moderní interiér.', 'Malaga'),
    (14801, 'Torre', 'folie', 'Robustní a elegantní vzhled s jemným reliéfem na povrchu.', 'Torre'),
    (20841, 'Nero', 'folie', 'Výrazné interiérové dveře s moderním designem a charakteristickým tmavým dekorem.', 'Nero'),
    (16621, 'Primo', 'cpl', 'Klasický design s jemnou strukturou povrchu vhodný do různých typů interiérů.', 'Primo'),
    (9177, 'Faro', 'cpl', 'Elegantní minimalistický model s univerzálním vzhledem pro moderní i tradiční interiéry.', 'Faro'),
    (9346, 'Rego', 'cpl', 'Čistý a jednoduchý design doplněný jemnou strukturou povrchu a moderním provedením.', 'Rego'),
    (9317, 'Ventura', 'cpl', 'Model kombinující tradiční prvky s moderním designem a elegantním hladkým povrchem.', 'Ventura'),
    (20854, 'Nero GT', 'cpl', 'Výrazný moderní model s charakterem a tmavým dekorem pro současné interiéry.', 'Nero-GT'),
    (27088, 'Presto', 'cpl', 'Minimalistický design s hladkým povrchem, který podtrhuje čistotu moderního interiéru.', 'Presto'),
    (27104, 'Presto Alto', 'cpl', 'Minimalistické dveře s hladkým povrchem a čistým moderním vzhledem.', 'Presto-ALTO'),
    (27069, 'Braga Lido', 'folie', '', None),
    (14523, 'Teo', 'folie', '', None),
]
PRICE = re.compile(r'(\d{1,2}[ .]?\d{3})\s*(?:,-)?\s*(?:Kč|,-)')


def cena(s):
    m = PRICE.search(s.replace('\xa0', ' '))
    return (int(re.sub(r'\D', '', m.group(1))), m) if m else (None, None)


def kc(n):
    return f'{n:,}'.replace(',', '\u00a0') + '\u00a0Kč'


models = []
for pid, name, typ, kratce, interier in KATALOG:
    p = raw[pid]
    bl = p['blocks']
    gals = [b for b in bl if b['t'] == 'gallery']
    table = next((b for b in bl if b['t'] == 'table'), None)
    dost, od = '', None
    if table:
        for r in table['rows']:
            k = re.sub('<[^>]+>', '', r[0]).strip()
            v = re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', r[1])).strip()
            if k == 'Dostupnost':
                dost = re.sub(r'U Vás\s*|\s*dní', '', v).replace(' – ', '–').replace(' - ', '–').strip()
            if k == 'Cena':
                od = cena(v.replace(' ', ' ').replace('3 ', '3 '))[0] or cena(re.sub(r'(\d)\s+(\d{3})', r'\1 \2', v))[0]
    varianty, dekory = [], []
    for g in gals:
        titles = [x['title'] for x in g['items']]
        if sum(1 for t in titles if cena(t)[0]) >= max(1, len(titles) // 2):
            cnt = {}
            for x in g['items']:
                c, m = cena(x['title'])
                nm = x['title'][:m.start()] if m else x['title']
                nm = re.sub(r'[\s:\-–,]+$', '', nm).strip()
                nm = re.sub(r'^BRAGA', 'Braga', nm).replace('PRESTO', 'Presto').replace('LIDO', 'Lido')
                cnt[nm] = cnt.get(nm, 0) + 1
                varianty.append({'nazev': nm, 'cena': c, 'img': im(x['src'])})
            seen = {}
            for v in varianty:
                if cnt.get(v['nazev'], 0) > 1:
                    seen[v['nazev']] = seen.get(v['nazev'], 0) + 1
                    v['nazev'] = f"{v['nazev']} · provedení {seen[v['nazev']]}"
        else:
            for x in g['items']:
                t = re.sub(r'^\d+\s+', '', x['title']).strip()
                t = ' '.join(w[:1].upper() + w[1:].lower() for w in t.split())
                dekory.append({'nazev': t, 'img': im(x['src'])})
    varianty = [v for v in varianty if v['img']]
    if od is None and varianty:
        od = min(v['cena'] for v in varianty if v['cena'])
    # popis = první delší odstavec; výbava = vše za nadpisem POPIS (u Tea za posledním nadpisem)
    popis = next((re.sub('<[^>]+>', '', b['h']) for b in bl if b['t'] == 'p' and len(b['h']) > 120), '')
    idx = next((i for i, b in enumerate(bl) if b['t'] == 'h' and b['x'].upper().startswith(('POPIS', 'INTERIEROVÉ DVEŘE VASCO'))), None)
    vybava = clean_blocks(bl[idx + 1:]) if idx is not None else []
    vybava = [b for b in vybava if not (b['t'] == 'p' and re.sub('<[^>]+>', '', b['h']).strip() == popis.strip())]
    seo, desc = meta(pid)
    slug = p['path'].strip('/')
    models.append({
        'id': pid, 'slug': slug, 'nazev': name, 'typ': typ, 'kratce': kratce or popis.split('. ')[0] + '.',
        'popis': popis, 'od': od, 'od_txt': kc(od) if od else '', 'dostupnost': dost or '14–21',
        'varianty': varianty, 'dekory': [d for d in dekory if d['img']], 'vybava': vybava,
        'interier': ('wp/' + imap[f'https://www.dvere-vascodoors.cz/wp-content/uploads/2026/02/Interierove-dvere-{interier}.png'])
        if interier and f'https://www.dvere-vascodoors.cz/wp-content/uploads/2026/02/Interierove-dvere-{interier}.png' in imap else None,
        'v_katalogu': bool(interier),
        'seo_title': seo, 'description': desc or (popis[:155].rsplit(' ', 1)[0] + '…' if popis else ''),
    })
from PIL import Image
for m in models:
    for v in m['varianty']:
        v['cena_txt'] = kc(v['cena']) if v['cena'] else ''
        w, h = Image.open('img/' + v['img']).size
        v['r'] = round(w / h, 3)
    # hlavní provedení = první samostatné křídlo (ne sada více dveří vedle sebe)
    m['hlavni'] = next((i for i, v in enumerate(m['varianty']) if v['r'] < .6), 0)
json.dump(models, open('_data/models.json', 'w'), ensure_ascii=False, indent=1)

# ---------- obsahové stránky ----------
OBSAH = {
    14258: ('Bezfalcové dveře', 'Sortiment'), 14260: ('Posuvné dveře', 'Sortiment'),
    29071: ('Masivní dveře na zakázku', 'Sortiment'), 14345: ('Kování – kliky', 'Sortiment'),
    14305: ('Obložkové zárubně', 'Sortiment'), 27753: ('Dekory zárubní Vasco Doors', 'Obložkové zárubně'),
    14302: ('Stavební pouzdra Scrigno', 'Sortiment'), 27679: ('Stavební pouzdra ECLISSE', 'Stavební pouzdra'),
    14285: ('Bezpečnostní dveře', 'Sortiment'), 14293: ('Dveře Boulit', 'Sortiment'),
    15136: ('Systém pro posuvné skleněné dveře', 'Posuvné dveře'), 28918: ('Ochrana osobních údajů', ''),
}
pages = []
for pid, (nazev, rubrika) in OBSAH.items():
    p = raw[pid]
    seo, desc = meta(pid)
    bl = clean_blocks(p['blocks'])
    # první nadpis = h1 stránky, pokud je hned na začátku (za případným nadtitulkem)
    lead_kicker = None
    if bl and bl[0]['t'] == 'kicker':
        lead_kicker = re.sub('<[^>]+>', '', bl.pop(0)['h'])
    h1 = nazev
    if bl and bl[0]['t'] == 'h':
        h1 = bl.pop(0)['x']
    first_img = next((b['src'] for b in bl if b['t'] == 'img'), None) or next(
        (b['items'][0]['src'] for b in bl if b['t'] == 'gallery'), None)
    pages.append({'id': pid, 'path': p['path'].strip('/'), 'nazev': nazev, 'rubrika': rubrika, 'h1': h1,
                  'kicker': lead_kicker, 'seo_title': seo or nazev, 'description': desc, 'blocks': bl,
                  'og': first_img})
json.dump(pages, open('_data/pages.json', 'w'), ensure_ascii=False, indent=1)

# ---------- realizace ----------
rl, seen = [], set()
for b in raw[14050]['blocks']:
    if b['t'] == 'gallery':
        for x in b['items']:
            s = im(x['src'])
            if s and s not in seen:
                seen.add(s); rl.append({'img': s, 'nazev': x.get('title') or ''})
json.dump(rl, open('_data/realizace.json', 'w'), ensure_ascii=False, indent=1)
print(len(models), 'modelů,', len(pages), 'stránek,', len(rl), 'realizací')
for m in models:
    print(f"  {m['nazev']:12} {m['typ']:5} od {m['od']} | {len(m['varianty'])} var | {len(m['dekory'])} dek | {len(m['vybava'])} výbava | {m['dostupnost']}")
