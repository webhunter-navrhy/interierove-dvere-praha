#!/usr/bin/env python3
"""Mail klienta (UID 13629, 17. 10. 2026) -> _data/blog.json. Použití: make_blog.py <mail.txt> [--list]"""
import json, re, sys, os
txt = open(sys.argv[1], encoding="utf-8").read()
txt = txt.split("\n" + "-" * 60 + "\n", 1)[-1] if "Předmět:" in txt[:400] else txt
txt = txt.split("Pod každý článek dal")[0]
parts = re.split(r"\n\s*ČLÁNEK (\d)\s*\n", "\n" + txt)
clanky = {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts), 2)}

META = {1: ("Jak vybrat interiérové dveře? Rady z praxe | Rady z praxe",
            "Jak vybrat interiérové dveře: způsob otevírání, falc nebo bezfalc, zaměření, panty a zámek, podlaha i cena celého kompletu. Rady člověka, který dveře prodává i montuje.",
            "jak-vybrat-interierove-dvere")}
TOP_NADPIS = re.compile(r"^(Dveře|Posuvné dveře|Falcové|Interiérové dveře|Jak vybrat)")
# ruční výjimky: řádky, které jsou odstavec, i když vypadají jako nadpis
NENI_NADPIS = {"Jaký chcete dekor?", "Znamená to ale, že jsou automaticky lepší?", "A co magnetický zámek?x"}
SLUZBY = []

def blok_kam(radek):
    return radek

out = []
for n in sorted(clanky):
    t = clanky[n]
    meta = {}
    for k in ("TITLE", "META DESCRIPTION", "URL"):
        m = re.search(r"^" + k + r":\s*(.+)$", t, re.M)
        if m:
            meta[k] = m.group(1).strip()
            t = t.replace(m.group(0), "", 1)
    if n == 1:
        meta["TITLE"], meta["META DESCRIPTION"], slug = META[1][0], META[1][1], META[1][2]
        meta["URL"] = f"/blog/{slug}/"
    odst = [p.strip() for p in re.split(r"\n\s*\n", t.strip()) if p.strip()]
    h1 = odst.pop(0)
    out.append(dict(n=n, slug=meta["URL"].strip("/").split("/")[-1], title=meta["TITLE"], description=meta["META DESCRIPTION"], h1=h1, odst=odst))
json.dump(out, open("/tmp/blog_raw.json", "w"), ensure_ascii=False, indent=1)
if "--list" in sys.argv:
    for c in out:
        print("=====", c["n"], c["slug"], "|", c["title"], "|", c["h1"])
        for i, p in enumerate(c["odst"]):
            if len(p) < 90: print(f"{i:3} {len(p):3} {p}")

# ---- blok-model -------------------------------------------------------------
KONCE = (".", ",", ":", ";", "“")
Q_PARA = {"Znamená to ale, že jsou automaticky lepší?", "Proč?", "Dveře do stavebního pouzdra, nebo posuvné po stěně?",
          "Chcete na stěnu pověsit obraz, poličku, televizi nebo jiný předmět?", "To je častá otázka.",
          "Plánujete posuvné dveře do stavebního pouzdra v Praze?", "Proč je výška podlahy pro dveře tak důležitá?"}
H_RUCNE = {"Posuvné dveře dokážou vyřešit prostor. Ale ne vždy.",
           "Dveře se nevybírají samostatně. Souvisí s podlahou i celým interiérem.",
           "Skryté panty vypadají krásně. Mají ale také svoje „ale“",
           "Nejdříve způsob otevírání, potom design"}
OPRAVY = {"uvažžoval": "uvažoval"}
ODKAZY = [("Jak vybrat interiérové dveře – rady z praxe", "blog/jak-vybrat-interierove-dvere/"),
          ("Falcové nebo bezfalcové dveře – co vybrat?", "blog/falcove-nebo-bezfalcove-dvere/"),
          ("Posuvné dveře do pouzdra, nebo na stěnu?", "blog/posuvne-dvere-do-pouzdra-nebo-na-stenu/"),
          ("Dveře do stavebního pouzdra – co musí být připravené před montáží", "blog/dvere-do-stavebniho-pouzdra-priprava/"),
          ("Interiérové dveře při rekonstrukci staršího bytu v Praze", "blog/interierove-dvere-rekonstrukce-bytu-praha/"),
          ("náš showroom interiérových dveří v Praze", "kontakt/"), ("našem showroomu v Praze", "kontakt/")]

def jako_nadpis(p):
    if p in H_RUCNE: return True
    if len(p) > 75 or p.startswith("„") or p[0].islower() or p in Q_PARA: return False
    if p.endswith("?"): return True
    return not p.endswith(KONCE)

def linkuj(p):
    for text, cil in ODKAZY:
        p = p.replace(text, f'<a href="@/{cil}">{text}</a>', 1)
    return p

def bloky(odst):
    for k, x in enumerate(odst):
        if x.startswith("Interní odkazy"): odst = odst[:k]; break
    for a, b in OPRAVY.items(): odst = [p.replace(a, b) for p in odst]
    out, i = [], 0
    while i < len(odst):
        p = odst[i]
        if p.endswith(":") and i + 2 < len(odst) and len(odst[i + 1]) < 70 and (odst[i + 1].endswith((",", ";")) or odst[i + 1].startswith("„")) and len(odst[i + 2]) < 70:
            pol = []
            j = i + 1
            if odst[j].startswith("„"):
                while j < len(odst) and odst[j].startswith("„"): pol.append(odst[j]); j += 1
            else:
                while j < len(odst) and odst[j].endswith((",", ";")): pol.append(odst[j]); j += 1
                pol.append(odst[j]); j += 1
            cap = lambda s: s[0].upper() + s[1:]
            if len(pol) < 2:
                i += 1; continue
            out.append({"t": "p", "h": linkuj(p)})
            out.append({"t": "ul", "items": [cap(x.rstrip(",;")) + ("" if x.startswith("„") else "") for x in pol]})
            i = j; continue
        if jako_nadpis(p) and i + 1 < len(odst):
            out.append({"t": "h", "l": 2, "x": p})
        else:
            out.append({"t": "p", "h": linkuj(p)})
        i += 1
    return out

KRATKY = {"jak-vybrat-interierove-dvere":"Jak vybrat dveře","falcove-nebo-bezfalcove-dvere":"Falcové nebo bezfalcové","posuvne-dvere-do-pouzdra-nebo-na-stenu":"Posuvné dveře","dvere-do-stavebniho-pouzdra-priprava":"Dveře do pouzdra","interierove-dvere-rekonstrukce-bytu-praha":"Rekonstrukce bytu"}
hotovo = []
for c in out:
    hotovo.append({"slug": c["slug"], "path": "blog/" + c["slug"], "title": c["title"], "description": c["description"],
                   "h1": c["h1"], "kratky": KRATKY[c["slug"]], "blocks": bloky(c["odst"])})
if "--list" not in sys.argv:
    os.makedirs("_data", exist_ok=True)
    json.dump({"autor": "Josef Šťastný", "autor_radek": "dveřím, podlahám a realizacím interiérů se věnuje od roku 2003",
               "clanky": hotovo}, open("_data/blog.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for h in hotovo:
        print(h["slug"], len(h["blocks"]), "bloků,", sum(b["t"] == "h" for b in h["blocks"]), "nadpisů,", sum(b["t"] == "ul" for b in h["blocks"]), "seznamů")
