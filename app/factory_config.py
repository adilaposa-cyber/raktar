"""
Szerelde RFID konfiguráció – a valódi gyári alaprajz alapján.

10 db HK olvasó pozíciója és az összes szerelőállás.
Forrás: feltöltött szerelde alaprajz (4270 JD + 4392 KSR sorok).
"""

# ── Szerelési sorok állásai ───────────────────────────────────────────────────
ASSEMBLY_LINES = {
    "4270": {
        "name": "4270 John Deere futómű szerelde",
        "positions": ["1423", "1424", "1425", "1426", "1427", "1428", "1429"],
        "color": "#2563eb",
    },
    "4392": {
        "name": "4392 Középsorozatú futómű szerelde",
        "positions": ["1323", "1324", "1325", "1326", "1327", "1328", "1329", "1330"],
        "color": "#d97706",
    },
}

# ── Speciális zónák ───────────────────────────────────────────────────────────
SPECIAL_ZONES = [
    {"id": "HÁTRALÉKOS", "name": "Hátralékos kocsik",  "color": "#3b82f6"},
    {"id": "RAKTÁR",     "name": "Szereldei raktár",   "color": "#8b5cf6"},
    {"id": "KÉSZ",       "name": "Kész hidak",          "color": "#22c55e"},
    {"id": "FOLYOSÓ",    "name": "Folyosó / tranzit",   "color": "#6b7280"},
]

# ── HK olvasók pozíciói ───────────────────────────────────────────────────────
# SVG koordináták: viewBox="0 0 960 480"
# x, y = az olvasó ikon középpontja az SVG-n
HK_READERS = [
    {
        "id": "HK01",
        "name": "HK01 – KSR bal bejárat",
        "zone": "KSR-1323",
        "covers": ["HÁTRALÉKOS", "1323"],    # melyik pozíciók között detektál
        "svg_x": 115, "svg_y": 390,
        "description": "Komissiózó kocsik bejárata a KSR sorba (bal)",
    },
    {
        "id": "HK02",
        "name": "HK02 – JD 1424 bejárat",
        "zone": "JD-1424",
        "covers": ["HÁTRALÉKOS", "1424"],
        "svg_x": 272, "svg_y": 110,
        "description": "JD sor – 1424 állás bejárata",
    },
    {
        "id": "HK03",
        "name": "HK03 – Szereldei raktár",
        "zone": "RAKTÁR",
        "covers": ["1424", "1425", "RAKTÁR"],
        "svg_x": 385, "svg_y": 110,
        "description": "Szereldei raktár bejárati kapuja",
    },
    {
        "id": "HK04",
        "name": "HK04 – JD 1426 bejárat",
        "zone": "JD-1426",
        "covers": ["1425", "1426"],
        "svg_x": 510, "svg_y": 100,
        "description": "JD sor – 1425/1426 állás közötti RFID kapu",
    },
    {
        "id": "HK05",
        "name": "HK05 – Középső folyosó",
        "zone": "FOLYOSÓ",
        "covers": ["1426", "1326", "1327"],
        "svg_x": 510, "svg_y": 248,
        "description": "JD és KSR sorok közötti folyosó",
    },
    {
        "id": "HK06",
        "name": "HK06 – JD 1428 bejárat",
        "zone": "JD-1428",
        "covers": ["1427", "1428"],
        "svg_x": 718, "svg_y": 110,
        "description": "JD sor – 1427/1428 állás közötti kapu",
    },
    {
        "id": "HK07",
        "name": "HK07 – JD jobb oldal",
        "zone": "JD-1429",
        "covers": ["1428", "1429", "KÉSZ"],
        "svg_x": 878, "svg_y": 210,
        "description": "JD sor jobb oldala – kész hidak zóna",
    },
    {
        "id": "HK08",
        "name": "HK08 – KSR 1427 bejárat",
        "zone": "KSR-1327",
        "covers": ["1326", "1327"],
        "svg_x": 576, "svg_y": 390,
        "description": "KSR sor – 1326/1327 állás köze",
    },
    {
        "id": "HK09",
        "name": "HK09 – KSR 1326 bejárat",
        "zone": "KSR-1326",
        "covers": ["1325", "1326"],
        "svg_x": 468, "svg_y": 390,
        "description": "KSR sor – 1325/1326 állás köze",
    },
    {
        "id": "HK10",
        "name": "HK10 – KSR 1324 bejárat",
        "zone": "KSR-1324",
        "covers": ["1323", "1324"],
        "svg_x": 248, "svg_y": 390,
        "description": "KSR sor – 1323/1324 állás köze",
    },
]

# HK ID → olvasó dict lookup
HK_BY_ID = {r["id"]: r for r in HK_READERS}

# ── HK olvasó → position leképezés ───────────────────────────────────────────
# Amikor egy kocsi átmegy egy HK olvasón, melyik pozícióba kerül?
HK_TO_POSITION = {
    "HK01": "1323",
    "HK02": "1424",
    "HK03": "RAKTÁR",
    "HK04": "1426",
    "HK05": "FOLYOSÓ",
    "HK06": "1428",
    "HK07": "KÉSZ",
    "HK08": "1327",
    "HK09": "1326",
    "HK10": "1324",
}

# ── Összes pozíció listája ────────────────────────────────────────────────────
ALL_POSITIONS = (
    ["HÁTRALÉKOS", "RAKTÁR", "FOLYOSÓ", "KÉSZ"]
    + ASSEMBLY_LINES["4270"]["positions"]
    + ASSEMBLY_LINES["4392"]["positions"]
)
