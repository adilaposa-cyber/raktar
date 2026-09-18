# RFID raklapkövetés – rendszerleírás és összehasonlítás
## Miért jobb ez a rendszer a jelenlegi megoldásnál?

> **A hatókör:** ez nem ERP és nem WMS – az Infor LN mellé települő
> nyomonkövetés. Arra válaszol, hogy egy kocsi vagy raklap **hol van most**,
> **hogyan került oda** és **mióta áll ott**, és minden helyváltozást lejelent
> az LN felé. A cikktörzs, a készlet és a rendelés az Infor LN-é marad.

---

## Mi a jelenlegi helyzet (tipikus gyárakban)?

A legtöbb magyarországi gyárban a komissiózó kocsik és szerelési állások követése jelenleg:
- **Papíron** zajlik (kézzel kitöltött listák, táblák)
- **Excel/WhatsApp** üzeneteken alapul (nincs valós idejű adat)
- **Szóbeli egyeztetéssel** (ki éppen merre van, melyik kocsi hol áll)
- **Nincs automatikus riasztás** ha egy kocsi túl soká áll egy helyen

### Következmények:
- Ha egy kocsi 2 óra óta a folyosón áll és senki sem veszi észre → állásidő, termeléskiesés
- A műszakvezető nem látja egyszerre az összes állomás állapotát
- Hézagoló lemezek elfelejtése → megáll a szerelés → újra kellett rendelni, késés
- A targoncások nem tudják, melyik kocsi vár mozgatásra

---

## Mit tud az RFID Raktar rendszer?

### 1. Élő szerelde térkép
- Az összes komissiózó kocsi pozíciója **valós időben** látható a képernyőn
- Automatikusan frissül 15 másodpercenként, RFID érzékelőkkel azonnali frissítés
- Az állások **kattinthatók**: rögtön látni, ki mit csinál ott és mennyi kocsi áll ott

### 2. Automatikus "kitárolt" riasztás (5 perces timer)
- Ha egy kocsi a folyosón áll **5 percnél tovább**, a rendszer piros riasztást jelez
- A műszakvezető azonnal látja: ez a kocsi **üres, mozgatásra vár**
- Nincs többé "nem tudtam, hogy ott áll" – a riasztás ott van a képernyőn

### 3. Napi gyártási terv
- Minden reggel be lehet állítani, **melyik állomáson mit gyártanak aznap**
- Az információ azonnal látható a szerelde térképen és a napi terv nézeten
- A "Nap lezárása" gombbal egyszerre törölhető az összes bejegyzés
- A hézagoló lemez igény is nyilvántartott állomásonként

### 4. Targoncás bejelentkezés RFID-del
- A targoncások a **belépő kártyájukkal vagy PIN kóddal** jelentkeznek be a rendszerbe
- Látható, ki éppen melyik targoncán dolgozik és mióta
- Teljes szekció-napló: ki mikor volt ott, mennyi ideig

### 5. Infor LN integráció (ION BOD, kétirányú)
- **LN → rendszer**: a Handling Unit és a cikktörzs tükrözve érkezik
  (`SyncHandlingUnit`, `SyncItemMaster`), így nem kell kézzel beírni semmit
- **Rendszer → LN**: minden fizikai helyváltozás automatikusan lejelentődik
  `SyncWarehouseTransfer` BOD-ként – ez a rendszer legfontosabb kimenete
- Amíg nincs élő ION kapcsolat, a lejelentés DRY-RUN módban naplózódik, és az
  LN HU-listája Excel/CSV fájlból tölthető be
- A rendszer **soha nem ír törzsadatot** az LN-be

### 6. Üzem struktúra
- Az egész gyár hierarchia tárolható: Üzem → Csarnok → Munkaállomás
- Minden állomáshoz egyedi térkép szerkeszthető (drag-and-drop)
- Más csarnokok is hozzáadhatók ugyanabba a rendszerbe

---

## Összehasonlítás táblázat

| Szempont | Régi megoldás (papír/Excel) | RFID Raktar rendszer |
|---|---|---|
| Kocsi pozíció láthatósága | Nem látható / szóbeli | Valós idő, élő térkép |
| Kitárolt kocsi riasztás | Nincs | Automatikus 5 perc után |
| Targoncás nyilvántartás | Papír / szóbeli | RFID bejelentkezés, napló |
| Hézagoló lemez igény | Post-it / fejből | Állomásonként rögzítve |
| Infor LN lejelentés | Kézi könyvelés utólag | Automatikus BOD minden mozgásnál |
| Frissítési sebesség | Kézzel, műszakonként | Valós idő (másodpercek) |
| Térbeli áttekintés | Nincs | SVG alaprajz, vizuális |
| Mobilos elérés | Nincs | Targoncás felület telefonon |
| Riasztások | Nincs | Piros jelzők, hangjelzés |
| Keresés / szűrés | Kézi lapozás | Azonnali szűrő |
| Auditnyom | Nincs | Minden mozgás naplózva |

---

## Megtakarított idő (becsült értékek)

| Tevékenység | Jelenlegi idő | RFID rendszerrel | Megtakarítás |
|---|---|---|---|
| "Hol van az X kocsi?" kérdés | 3-10 perc | 5 másodperc | **~95%** |
| Kitárolt kocsi észrevétele | 15-60 perc | Automatikus (5 perc) | **~80%** |
| Mozgás lekönyvelése LN-ben | 15-30 mp / mozgás | Automatikus | **~100%** |
| Hézagoló lemez lista | 5-15 perc | Azonnali, 1 kattintás | **~90%** |
| Targoncás bejelentkezés napló | 5-10 perc/nap | Automatikus | **~100%** |

---

## Technikai háttér

- **Backend**: FastAPI (Python) – gyors, modern, skálázható
- **Adatbázis**: SQLite (fejlesztés) → PostgreSQL (éles) – könnyen migrálható
- **RFID hardver**: Zebra ATR7000 RTLS olvasók a **mennyezetre függesztve**
  (beépített fázisvezérelt antennasor, külső antenna nem kell, PoE+ táplálás).
  A rendszer nem kapus: az olvasók folyamatosan látják a tageket alattuk és
  koordinátát adnak, amiből az alaprajz dönti el a helyet.
- **Kommunikáció**: WebSocket alapú valós idejű frissítés
- **Frontend**: Bootstrap 5, SVG alaprajz – böngészőből elérhető, nincs telepítés
- **Szimulátor**: Szoftveres RFID szimulátor – hardware nélkül is tesztelhető

---

## Bevezetési lépések

1. **Konfiguráció** (1-2 nap): Üzem, csarnokok, munkaállomások rögzítése
2. **ATR7000 olvasók telepítése** (2-3 nap): mennyezeti függesztés 4–6 m
   magasan emelőkosárral, PoE+ hálózat kiépítése, majd 3–4 nap behangolás
3. **Kocsi RFID tagek** (1 nap): Minden kocsihoz tag rögzítése + EPC regisztrálás
4. **Oktatás** (fél nap): Műszakvezető, targoncások, adminisztrátor
5. **Éles indítás**: Fokozatos bevezetés, szimulátorral párhuzamosan tesztelhető

---

*Rendszer verziója: 1.0.0 | Fejlesztő: RFID Raktar projekt*
*Dokumentum utolsó frissítése: 2026-05-09*
