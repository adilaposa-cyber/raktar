"""
Szerelde RFID konfiguráció – a valódi gyári alaprajz alapján.

10 db RFID érzékelő pozíciója és az összes szerelőállás.
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
    {"id": "HÁTRALÉKOS",    "name": "Hátralékos kocsik",   "color": "#3b82f6"},
    {"id": "RAKTÁR",        "name": "Szereldei raktár",    "color": "#8b5cf6"},
    {"id": "KÉSZ",          "name": "Kész hidak",           "color": "#22c55e"},
    {"id": "FOLYOSÓ-BAL",   "name": "Bal folyosó",          "color": "#64748b"},
    {"id": "FOLYOSÓ-KÖZÉP", "name": "Középső folyosó",      "color": "#64748b"},
    {"id": "FOLYOSÓ-JOBB",  "name": "Jobb folyosó",         "color": "#64748b"},
]

# ── RFID érzékelők pozíciói ───────────────────────────────────────────────────
# SVG koordináták: viewBox="0 0 1100 500"
HK_READERS = [
    {
        "id": "HK01",
        "name": "RFID érzékelő 01 – KSR bal bejárat",
        "zone": "KSR-1323",
        "covers": ["HÁTRALÉKOS", "1323"],
        "svg_x": 224, "svg_y": 310,
        "description": "Komissiózó kocsik bejárata a KSR sorba (bal)",
    },
    {
        "id": "HK02",
        "name": "RFID érzékelő 02 – JD 1424 bejárat",
        "zone": "JD-1424",
        "covers": ["HÁTRALÉKOS", "1424"],
        "svg_x": 411, "svg_y": 55,
        "description": "JD sor – 1424 állás bejárata",
    },
    {
        "id": "HK03",
        "name": "RFID érzékelő 03 – Raktár kapu",
        "zone": "RAKTÁR",
        "covers": ["RAKTÁR", "HÁTRALÉKOS"],
        "svg_x": 132, "svg_y": 250,
        "description": "Raktár és szerelde közötti kapu",
    },
    {
        "id": "HK04",
        "name": "RFID érzékelő 04 – JD 1426 bejárat",
        "zone": "JD-1426",
        "covers": ["1425", "1426"],
        "svg_x": 599, "svg_y": 55,
        "description": "JD sor – 1425/1426 állás közötti RFID kapu",
    },
    {
        "id": "HK05",
        "name": "RFID érzékelő 05 – Középső folyosó",
        "zone": "FOLYOSÓ-KÖZÉP",
        "covers": ["1426", "1326", "FOLYOSÓ-KÖZÉP"],
        "svg_x": 660, "svg_y": 260,
        "description": "Középső folyosó – JD/KSR sorok között",
    },
    {
        "id": "HK06",
        "name": "RFID érzékelő 06 – JD 1428 bejárat",
        "zone": "JD-1428",
        "covers": ["1427", "1428"],
        "svg_x": 849, "svg_y": 55,
        "description": "JD sor – 1427/1428 állás közötti kapu",
    },
    {
        "id": "HK07",
        "name": "RFID érzékelő 07 – JD jobb oldal / Kész",
        "zone": "JD-1429",
        "covers": ["1429", "KÉSZ"],
        "svg_x": 1080, "svg_y": 152,
        "description": "JD sor jobb oldala – kész hidak zóna",
    },
    {
        "id": "HK08",
        "name": "RFID érzékelő 08 – KSR 1327 bejárat",
        "zone": "KSR-1327",
        "covers": ["1326", "1327"],
        "svg_x": 660, "svg_y": 276,
        "description": "KSR sor – 1326/1327 állás köze",
    },
    {
        "id": "HK09",
        "name": "RFID érzékelő 09 – KSR 1326 bejárat",
        "zone": "KSR-1326",
        "covers": ["1325", "1326"],
        "svg_x": 551, "svg_y": 276,
        "description": "KSR sor – 1325/1326 állás köze",
    },
    {
        "id": "HK10",
        "name": "RFID érzékelő 10 – KSR 1324 bejárat",
        "zone": "KSR-1324",
        "covers": ["1323", "1324"],
        "svg_x": 333, "svg_y": 276,
        "description": "KSR sor – 1323/1324 állás köze",
    },
]

# RFID érzékelő ID → olvasó dict lookup
HK_BY_ID = {r["id"]: r for r in HK_READERS}

# ── RFID érzékelő → pozíció leképezés ────────────────────────────────────────
# Amikor egy kocsi átmegy egy érzékelőn, melyik pozícióba kerül?
HK_TO_POSITION = {
    "HK01": "1323",
    "HK02": "1424",
    "HK03": "RAKTÁR",
    "HK04": "1426",
    "HK05": "FOLYOSÓ-KÖZÉP",
    "HK06": "1428",
    "HK07": "KÉSZ",
    "HK08": "1327",
    "HK09": "1326",
    "HK10": "1324",
}

# ── Összes pozíció listája ────────────────────────────────────────────────────
ALL_POSITIONS = (
    ["HÁTRALÉKOS", "RAKTÁR", "FOLYOSÓ-BAL", "FOLYOSÓ-KÖZÉP", "FOLYOSÓ-JOBB", "KÉSZ"]
    + ASSEMBLY_LINES["4270"]["positions"]
    + ASSEMBLY_LINES["4392"]["positions"]
)

# Folyosó pozíciók halmaza (5 perces timer figyeléséhez)
CORRIDOR_POSITIONS = {"FOLYOSÓ-BAL", "FOLYOSÓ-KÖZÉP", "FOLYOSÓ-JOBB"}
