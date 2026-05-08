# RFID RTLS Rendszer – Költségbecslés

**Zebra ATR7000 alapú raktárkezelő rendszer**
**Magyar gyártóvállalat számára**
**Árfolyam: 1 EUR = 400 HUF (tájékoztató jellegű)**

---

> **Figyelmeztetés**: Az alábbi árak tájékoztató jellegűek (2024–2025 piaci adatok alapján). A tényleges árak ajánlatkéréstől, mennyiségtől, viszonteladói árazástól és piaci körülményektől függően eltérhetnek. Minden tételnél megadjuk a reális minimum–maximum sávot.

---

## 1. Egyszeri (Beruházási) Költségek

### 1.1 Hardver Költségek

#### RFID Olvasók és Antennák

| Tétel | Mennyiség | Egységár (EUR) min–max | Összesen (EUR) min–max | Összesen (HUF ezer) min–max |
|---|---|---|---|---|
| Zebra ATR7000 RFID olvasó | 5 db | 1 800 – 2 500 EUR | 9 000 – 12 500 | 3 600 – 5 000 |
| Zebra FX9600 kapu olvasó | 2 db | 1 400 – 2 000 EUR | 2 800 – 4 000 | 1 120 – 1 600 |
| UHF RFID antenna (Laird S9028 vagy egyenértékű) | 20 db | 80 – 150 EUR | 1 600 – 3 000 | 640 – 1 200 |
| Antenna koaxiális kábel LMR-400 (kész hosszak) | 20 db | 30 – 80 EUR | 600 – 1 600 | 240 – 640 |
| **Részösszeg: Olvasók + antennák** | | | **14 000 – 21 100** | **5 600 – 8 440** |

#### RFID Címkék (Induló készlet)

| Tétel | Mennyiség | Egységár (EUR) min–max | Összesen (EUR) min–max | Összesen (HUF ezer) min–max |
|---|---|---|---|---|
| UHF RFID raklap label (Avery Dennison, Monza R6) | 2 000 db | 0,08 – 0,18 EUR | 160 – 360 | 64 – 144 |
| Hard tag targoncára (Confidex Steelwave Micro II) | 20 db | 15 – 30 EUR | 300 – 600 | 120 – 240 |
| Hard tag gurulóeszközre (Confidex Ironside) | 50 db | 8 – 18 EUR | 400 – 900 | 160 – 360 |
| Referencia/anchor tag | 30 db | 5 – 12 EUR | 150 – 360 | 60 – 144 |
| **Részösszeg: Induló tagkészlet** | | | **1 010 – 2 220** | **404 – 888** |

#### Hálózati Infrastruktúra

| Tétel | Mennyiség | Egységár (EUR) min–max | Összesen (EUR) min–max | Összesen (HUF ezer) min–max |
|---|---|---|---|---|
| PoE+ menedzselt switch (24 port, pl. Cisco SG350-28P) | 2 db | 600 – 1 200 EUR | 1 200 – 2 400 | 480 – 960 |
| Cat6A S/FTP hálózati kábel (200 fm) | 200 fm | 2 – 4 EUR/fm | 400 – 800 | 160 – 320 |
| Patch panel, rack szekrény, PDU | 1 tétel | 400 – 800 EUR | 400 – 800 | 160 – 320 |
| Kábeltálca, kábelcsatorna, szerelési anyagok | 1 tétel | 300 – 600 EUR | 300 – 600 | 120 – 240 |
| **Részösszeg: Hálózati infrastruktúra** | | | **2 300 – 4 600** | **920 – 1 840** |

#### Szerver és Számítástechnika

| Tétel | Mennyiség | Egységár (EUR) min–max | Összesen (EUR) min–max | Összesen (HUF ezer) min–max |
|---|---|---|---|---|
| Alkalmazásszerver (Dell PowerEdge T150 vagy egyenértékű) | 1 db | 1 200 – 2 500 EUR | 1 200 – 2 500 | 480 – 1 000 |
| Operátori munkaállomás + monitor | 2 db | 600 – 1 000 EUR | 1 200 – 2 000 | 480 – 800 |
| UPS (szerver + rack) | 2 db | 400 – 800 EUR | 800 – 1 600 | 320 – 640 |
| **Részösszeg: Szerver és IT** | | | **3 200 – 6 100** | **1 280 – 2 440** |

---

#### Hardver Összesítő

| Kategória | Min (EUR) | Max (EUR) | Min (HUF ezer) | Max (HUF ezer) |
|---|---|---|---|---|
| RFID olvasók + antennák | 14 000 | 21 100 | 5 600 | 8 440 |
| Induló tagkészlet | 1 010 | 2 220 | 404 | 888 |
| Hálózati infrastruktúra | 2 300 | 4 600 | 920 | 1 840 |
| Szerver és IT | 3 200 | 6 100 | 1 280 | 2 440 |
| **HARDVER ÖSSZESEN** | **20 510** | **34 020** | **8 204** | **13 608** |

---

### 1.2 Szoftver Költségek

| Tétel | Megjegyzés | Egyszeri költség (EUR) |
|---|---|---|
| RFID raktárkezelő webalkalmazás (jelen rendszer) | **Ingyenes / nyílt forráskódú** | 0 |
| Ubuntu Server 22.04 LTS | Ingyenes | 0 |
| Docker / Docker Compose | Ingyenes | 0 |
| PostgreSQL / SQLite adatbázis | Ingyenes | 0 |
| Zebra ATR7000 alap firmware és LLRP | A hardver árában benne | 0 |
| Zebra SmartEdge / RFID middleware (ha szükséges) | Csak akkor, ha natív webhook nem elegendő | 0 – 3 000 EUR/olvasó/év (licenc modell) |
| **Szoftver összesen (alapeset)** | | **0 EUR** |

> **Megjegyzés**: Ha a Zebra natív middleware (pl. SmartEdge) szükséges az integrációhoz, az licenszdíja olvasónként és évente 500–3 000 EUR lehet. Ez opcionális, és az ingyenes LLRP protokollon alapuló megközelítéssel elkerülhető.

---

### 1.3 Telepítési és Üzembe Helyezési Költségek

| Tétel | Becsült napok | Nap díj (EUR) min–max | Összesen (EUR) min–max | Összesen (HUF ezer) min–max |
|---|---|---|---|---|
| Site survey (helyszínfelmérés) | 1–2 nap | 600 – 1 000 EUR/nap | 600 – 2 000 | 240 – 800 |
| Fizikai telepítés (konzolok, kábelek, olvasók) | 3–5 nap | 400 – 700 EUR/nap | 1 200 – 3 500 | 480 – 1 400 |
| Hálózati konfiguráció (switch, IP, VLAN) | 1 nap | 600 – 900 EUR/nap | 600 – 900 | 240 – 360 |
| RFID olvasó konfiguráció és finomhangolás | 2–3 nap | 600 – 1 000 EUR/nap | 1 200 – 3 000 | 480 – 1 200 |
| Szoftver telepítés és alap konfiguráció | 1–2 nap | 500 – 800 EUR/nap | 500 – 1 600 | 200 – 640 |
| Integrációs teszt (UAT) | 2–3 nap | 500 – 800 EUR/nap | 1 000 – 2 400 | 400 – 960 |
| **Részösszeg: Alap telepítés** | **10–16 nap** | | **5 100 – 13 400** | **2 040 – 5 360** |

---

### 1.4 Infor LN Integrációs Fejlesztés

| Tétel | Becsült napok | Nap díj (EUR) | Összesen (EUR) min–max | Összesen (HUF ezer) min–max |
|---|---|---|---|---|
| Követelmény-felmérés és funkcionális specifikáció | 3–5 nap | 700 – 1 000 EUR/nap | 2 100 – 5 000 | 840 – 2 000 |
| Infor LN BOD / ION API integráció fejlesztése | 10–20 nap | 700 – 1 000 EUR/nap | 7 000 – 20 000 | 2 800 – 8 000 |
| RFID middleware ↔ Infor LN adatmapping | 3–5 nap | 700 – 1 000 EUR/nap | 2 100 – 5 000 | 840 – 2 000 |
| Tesztelés, hibajavítás, éles indítás | 5–8 nap | 700 – 1 000 EUR/nap | 3 500 – 8 000 | 1 400 – 3 200 |
| Dokumentáció | 2–3 nap | 500 – 700 EUR/nap | 1 000 – 2 100 | 400 – 840 |
| **Részösszeg: LN integráció** | **23–41 nap** | | **15 700 – 40 100** | **6 280 – 16 040** |

> **Megjegyzés**: Az Infor LN integráció összetettsége az igényektől erősen függ. Ha csak egy egyszerű raktárhely-frissítési webhook elegendő, a kisebb érték reális. Ha teljes WMS ↔ ERP szinkronizáció (raklapmovement, inventory sync, GI/GR tranzakció) szükséges, a felső érték közelíthető.

---

### 1.5 Betanítás

| Tétel | Becsült napok | Nap díj (EUR) | Összesen (EUR) min–max | Összesen (HUF ezer) min–max |
|---|---|---|---|---|
| Felhasználói tréning (raktáros operátorok, 6–10 fő) | 1–2 nap | 500 – 800 EUR/nap | 500 – 1 600 | 200 – 640 |
| IT/rendszergazda tréning | 1–2 nap | 600 – 900 EUR/nap | 600 – 1 800 | 240 – 720 |
| **Részösszeg: Tréning** | | | **1 100 – 3 400** | **440 – 1 360** |

---

### Egyszeri Költségek Összesítője

| Kategória | Min (EUR) | Max (EUR) | Min (HUF ezer) | Max (HUF ezer) |
|---|---|---|---|---|
| Hardver | 20 510 | 34 020 | 8 204 | 13 608 |
| Szoftver | 0 | 0 | 0 | 0 |
| Telepítés és üzembe helyezés | 5 100 | 13 400 | 2 040 | 5 360 |
| Infor LN integráció | 15 700 | 40 100 | 6 280 | 16 040 |
| Tréning | 1 100 | 3 400 | 440 | 1 360 |
| **EGYSZERI ÖSSZESEN** | **42 410** | **90 920** | **16 964** | **36 368** |

---

## 2. Éves Ismétlődő Költségek

| Tétel | Leírás | Min (EUR/év) | Max (EUR/év) | Min (HUF ezer/év) | Max (HUF ezer/év) |
|---|---|---|---|---|---|
| Zebra OneCare hardver szerviz (ATR7000 olvasók) | ~10–15% hardverérték/év; NBD csere | 1 400 | 3 200 | 560 | 1 280 |
| Éves raklap tag pótlás (elhasználódás, veszteség) | ~500–1 000 db/év @ 0,08–0,18 EUR/db | 40 | 180 | 16 | 72 |
| Hard tag pótlás (targoncák, kocsik) | ~5–10 db/év | 40 | 300 | 16 | 120 |
| Szerver karbantartás / OS frissítés (belső IT) | Saját IT-csapat ideje, ~5 nap/év | 0 | 2 000 | 0 | 800 |
| Szoftver karbantartás (alkalmazás) | Nyílt forráskódú; saját fejlesztői kapacitás | 0 | 3 000 | 0 | 1 200 |
| Infor LN integráció karbantartás / módosítás | Alkalmi fejlesztési napok (~5 nap/év) | 2 000 | 5 000 | 800 | 2 000 |
| Hálózati eszköz garancia meghosszabbítás | Switch firmware, support | 200 | 500 | 80 | 200 |
| **ÉVES ISMÉTLŐDŐ ÖSSZESEN** | | **3 680** | **14 180** | **1 472** | **5 672** |

---

## 3. 3 Éves TCO (Total Cost of Ownership)

| Időszak | Min (EUR) | Max (EUR) | Min (HUF ezer) | Max (HUF ezer) |
|---|---|---|---|---|
| Egyszeri beruházás (0. év) | 42 410 | 90 920 | 16 964 | 36 368 |
| 1. éves ismétlődő költség | 3 680 | 14 180 | 1 472 | 5 672 |
| 2. éves ismétlődő költség | 3 680 | 14 180 | 1 472 | 5 672 |
| 3. éves ismétlődő költség | 3 680 | 14 180 | 1 472 | 5 672 |
| **3 ÉVES TCO ÖSSZESEN** | **53 450** | **133 460** | **21 380** | **53 384** |

> **Középérték (reális becslés)**: kb. **75 000–85 000 EUR** (30–34 millió HUF) 3 évre.

---

## 4. ROI Számítás

### 4.1 Feltételezett Megtakarítások

Az RFID RTLS rendszer az alábbi területeken hoz mérhető megtakarítást:

| Megtakarítási terület | Feltételezés | Éves megtakarítás (EUR) |
|---|---|---|
| Elveszett / rossz helyre tett raklapok csökkentése | 20 db elveszett raklap/év × átlag 500 EUR értékvesztés (keresési idő + áru) | 10 000 |
| Raklapkeresési idő megtakarítás | 3 raktáros × 0,5 óra/nap × 250 munkanap × 15 EUR/óra | 5 625 |
| Leltározási munkaóra csökkentés | Negyedéves teljes leltár 3 napról 1 napra csökkentése: 5 fő × 2 nap × 4 × 20 EUR/óra × 8 h | 6 400 |
| Infor LN készletadat-pontosság (kevesebb sürgős rendelés/szállítás) | Évente 5 sürgős szállítás elmaradása × 300 EUR/alkalom | 1 500 |
| Villástargonca optimálisabb útválasztás (üzemanyag-megtakarítás) | 10% hatékonyság-javulás × 8 targonca × 5 000 EUR/év üzemköltség × 10% | 4 000 |
| **Éves megtakarítás összesen** | | **~27 525 EUR** |

> **Megjegyzés**: A fenti feltételezések egy közepes méretű gyártóraktárra vonatkoznak. A tényleges megtakarítás a konkrét körülményektől, a keresési időktől és az áruérték-vesztéstől erősen függ. Az értékek konzervatív becslések.

### 4.2 ROI Számítás

| Mutató | Érték |
|---|---|
| Beruházás (egyszeri, középérték) | ~66 000 EUR |
| Éves megtakarítás (konzervatív) | ~27 500 EUR |
| Egyszerű megtérülési idő (Payback Period) | **~2,4 év** |
| 3 éves nettó megtakarítás (megtakarítás – TCO) | ~82 500 EUR – 91 000 EUR = **–8 500 EUR** (enyhe mínusz, de a 4. évtől profitál) |
| 5 éves nettó megtakarítás | 5 × 27 500 – (66 000 + 4 × 9 000 ismétlődő) = **~101 500 EUR** |

> A rendszer **2,5–3 éven belül megtérül**, és az 5. év végére 100 000 EUR feletti nettó hasznot hozhat.

---

## 5. Összefoglaló Táblázat

| | Optimista (min) | Reális (közép) | Pesszimista (max) |
|---|---|---|---|
| Egyszeri beruházás | 42 000 EUR (16,8 M HUF) | 65 000 EUR (26,0 M HUF) | 91 000 EUR (36,4 M HUF) |
| Éves ismétlődő | 3 700 EUR (1,5 M HUF) | 8 000 EUR (3,2 M HUF) | 14 200 EUR (5,7 M HUF) |
| 3 éves TCO | 53 000 EUR (21,2 M HUF) | 89 000 EUR (35,6 M HUF) | 134 000 EUR (53,6 M HUF) |
| Éves megtakarítás | 35 000 EUR | 27 500 EUR | 18 000 EUR |
| Megtérülési idő | 1,5 év | 2,4 év | 4,5 év |

---

## 6. Fontos Megjegyzések és Kockázatok

1. **Infor LN integráció a legnagyobb bizonytalansági faktor**: Az ERP integráció fejlesztési időigénye 23–41 napra becsült. Ha az Infor LN verzió idősebb (pl. 10.x vs 12.x), vagy ha az ION integrációs réteg nincs konfigurálva, a fejlesztési idő és cost jelentősen nőhet.

2. **A szoftver ingyenes**: Jelen rendszer nyílt forráskódú, nincs licenszdíja. Ez komoly előny az üzleti RFID middleware megoldásokhoz képest (pl. Zebra Savanna, Impinj ItemSense).

3. **Tag pótlás folyamatos tétel**: A raklap labelek fogyóeszközök. A pótlás éves mennyisége a raktár forgalmától függ. 5 000+ raklapforgatmány esetén a pótlás éves tétele 400–900 EUR-ra nőhet.

4. **Site survey kötelező**: A helyszínfelmérés nélkül kialakított rendszer nagy valószínűséggel nem adja a várt lefedettséget. A site survey-t az ajánlatba be kell kérni.

5. **Phased approach ajánlott**: Ha a teljes beruházás egyszerre kockázatos, érdemes fázisosan indítani: először 2 olvasó + pilot zóna (~25 000 EUR), majd az eredmények alapján bővíteni.
