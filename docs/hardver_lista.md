# RFID RTLS Rendszer – Hardver Bevásárlólista

**Zebra ATR7000 alapú raktárkezelő rendszer**
**Magyar gyártóvállalat számára**

---

## Előfeltételek és méretezési alapelvek

- Tipikus raktárméret: 2 000–5 000 m²
- Olvasók elhelyezése: 1 ATR7000 olvasó kb. 600–900 m² lefedettséghez (4 antenna, nyílt tér)
- Villasállás-/szállítóeszköz-követéshez: bejáratok, folyosók, kapuk mellé is szükséges olvasó
- Az alábbi mennyiségek egy ~3 000 m²-es, közepes raktárra vonatkoznak; skálázható

---

## Hardver Lista

| # | Megnevezés | Modell / Specifikáció | Mennyiség | Megjegyzés |
|---|---|---|---|---|
| **RFID OLVASÓK** | | | | |
| 1 | Fix RFID olvasó (RTLS) | Zebra ATR7000 UHF RFID Reader | 4–6 db | ~3 000 m²-es raktárhoz; minden olvasóhoz 4 antenna csatlakoztatható. Ethernet + PoE; LLRP protokoll; beépített webszerver. |
| 2 | Kapu/zóna RFID olvasó (opcionális) | Zebra FX9600 UHF RFID Reader | 2–4 db | Betárolási/kitárolási kapu ellenőrzéshez; 8 antenna port/egység. Használható a ATR7000 mellett a kapuknál. |
| **ANTENNÁK** | | | | |
| 3 | Beltéri UHF RFID antenna (cirkulárisan polarizált) | Zebra AN480 vagy Laird S9028PCL (9 dBic, RHCP, N-csatlakozó) | 16–24 db | 4 db/olvasó; nyílt raktárnál elegendő. Falra/mennyezetre szerelhető. IP65 minősítés ajánlott. |
| 4 | Antenna-kábel (antenna ↔ olvasó) | LMR-400 koaxiális kábel, N-Male mindkét végén | 16–24 db (à 5–10 m) | Max. 10 m/kábel ATR7000-hez; hosszabb távolságnál jelerősítő szükséges. Megrendelhető kész szerelt hosszban. |
| **UHF RFID CÍMKÉK** | | | | |
| 5 | Raklap (pallet) RFID címke | Zebra ZT610 nyomtatóval kompatibilis UHF RFID inlay; vagy kész: Avery Dennison AD-221r6 (Monza R6 chip) | 2 000–5 000 db/év | EPC Gen2, ISO 18000-63; 915 MHz EU band (865–868 MHz). Olvasási távolság: 3–6 m tipikusan. |
| 6 | Targonca/ipari jármű RFID tag | Zebra RFID Hard Tag; vagy Confidex Steelwave Micro II (fémfelületre) | 15–25 db | Fémfelületre ragasztható/csavarozható, IP68, -25°C–+70°C; olvasható közelről és kapukon áthaladva. |
| 7 | Gurulóállvány / mozgóeszköz RFID tag | Confidex Ironside Compact UHF | 30–80 db | Kemény műanyag/fém burkolatban; csavarozható; fémre is alkalmas. |
| 8 | Helymegjelölő (referencia/anchor) RFID tag | Zebra RFID Reference Tag; vagy Identix RFIDTag-WALL | 20–40 db | Fix pontokra ragasztva; RTLS koordináta-kalibráláshoz. |
| **HÁLÓZATI INFRASTRUKTÚRA** | | | | |
| 9 | PoE+ menedzselt switch | Cisco SB SG350-28P vagy HP/Aruba 1930 24G PoE+ 24 port, 370 W | 2–3 db | ATR7000: PoE+ (802.3at, max. 25 W/port) szükséges. Minden olvasóhoz 1 PoE+ port kell. VLAN, SNMP támogatás. |
| 10 | Rack szekrény (19") | 12U fali rack szekrény, 600×600 mm | 1–2 db | Szerver + switchek + UPS elhelyezésére; zárt, porálló kivitel. |
| 11 | Patch panel (Cat6A) | 24 portos Cat6A patch panel, 19" | 1–2 db | Strukturált kábelezéshez. |
| 12 | Hálózati kábel olvasóhoz | Cat6A S/FTP árnyékolt fali kábel, raktárhoz méreten vágva | ~200 fm | Minden ATR7000 olvasóhoz 1 Ethernet kábel (PoE+); raktár méretétől függő hossz. Max. 90 m/futam. |
| 13 | Gyári patch kábel (olvasó ↔ patch panel) | Cat6A patch kábel, 2 m | 10–15 db | Rack belsejébe. |
| 14 | Kábelcsatorna / kábeltálca | Fémkábel-tálca 60×40 mm (mennyezeti futtatáshoz) | 50–100 fm | Hálózati és antenna-kábelek biztonságos führéséhez; tűzálló kivitel ajánlott. |
| **SZERVER / SZÁMÍTÁSTECHNIKA** | | | | |
| 15 | Szerver (alkalmazásszerver) | Dell PowerEdge T150 vagy HP ProLiant ML110 Gen11; min.: Intel Xeon E-2300 series, 32 GB ECC RAM, 2× 1 TB SSD RAID-1, 2× GbE NIC | 1 db | RFID middleware + webalkalmazás futtatásához. Dockerizált környezet. Linux (Ubuntu 22.04 LTS) ajánlott. |
| 16 | Kliens PC / operátor munkaállomás | Dell OptiPlex 7010 SFF vagy egyenértékű; i5/i7, 16 GB RAM, 512 GB SSD, 24" monitor | 1–3 db | Raktáros operátoroknak; böngésző alapú UI elegendő. |
| 17 | Vonalkód/RFID kézi olvasó (opcionális) | Zebra MC3300ax UHF RFID + vonalkód | 2–4 db | Manuális leltározáshoz, bevételezési ellenőrzéshez. Wi-Fi (802.11ax). |
| **TÁPELLÁTÁS / UPS** | | | | |
| 18 | Szünetmentes tápegység (UPS) – szerver | APC Smart-UPS 1500VA LCD RM 2U (SMT1500RMI2U) | 1 db | Szerver + switch védelméhez; min. 15–20 perces áramszünet-védelemre. |
| 19 | UPS – hálózati rack | APC Back-UPS Pro 1200VA (BR1200GI) | 1 db | Rack switchek védelméhez, ha külön helyen van. |
| 20 | Túlfeszültségvédő elosztó (rack) | APC Rack PDU, 1U, 230V, 16A, 8× C13 | 2 db | Rack belső tápellátáshoz. |
| **SZERELÉSI KELLÉKEK** | | | | |
| 21 | Falra/mennyezetre szerelhető antenna tartókonzol | Acme/Anixter univerzális RFID antenna konzol (állítható szög, VESA kompatibilis) | 16–24 db | Minden antennához 1 db; beton/fém gerenda rögzítéshez alkalmas. |
| 22 | ATR7000 olvasó rögzítőkészlet | Zebra gyári szerelőkészlet ATR7000-hez (DIN sín vagy fali rögzítés) | 4–6 db | Gyárból rendelhető tartozék; tartalmazza csavarokat, tömítéseket. |
| 23 | Ipari műanyag kábelvédő cső (flex) | Kopex / Anamet 20 mm flexibilis fémszálas kábelvédő | 30–50 fm | Antenna-kábelek védelmére azokon a szakaszokon, ahol mechanikai behatás érhet (villás emelő útvonal). |
| 24 | Kábeles kábelkötegelő | UV-álló nylon kábelkötegelő, 300 mm és 450 mm vegyesen | 200 db | Rendezett kábelvezetéshez. |
| 25 | Csavar, dübel, rögzítő készlet | M6 rozsdamentes csavar + fém dübel betonhoz; M8 egyéb | 1 készlet (~200 db) | Mennyezeti antenna és olvasó rögzítéséhez; beton + acélváz elemekhez. |
| 26 | Ipari jelölőtábla / táblarendszer | Laminált tábla RFID zónákhoz (A4, 2 mm PVC) | 10–20 db | Zónahatárok, olvasó-helyszínek megjelölésére a raktárban. |
| **SZERSZÁMOK** | | | | |
| 27 | Hálózati teszter (Cat6A) | Fluke Networks DSX2-8000 CableAnalyzer vagy kölcsönözve | 1 db | Cat6A kábel certifikáláshoz telepítés után; kölcsönözhető is. |
| 28 | Koax kábelvégző szerszámkészlet | Amphenol/PPC N-csatlakozó préselő készlet LMR-400-hoz | 1 készlet | Antenna-kábelek helyszíni végzéséhez, ha nem előre szerelt hosszokat rendelünk. |
| 29 | Ütvecsavarozó / akkumulátoros fúró | Dewalt DCD996 vagy egyenértékű | 1–2 db | Konzolok, rackek felszerelésére. |
| 30 | Létra / állványzat | 6 m-es alumínium létra vagy görgős állvány | 1–2 db | Mennyezeti antennák szereléséhez (tipikus raktármagasság 6–9 m esetén állvány szükséges). |
| 31 | Hőlégfúvó / szigetelőszalag készlet | Általános elektromos szerelési kiegészítők | 1 készlet | Kábel lezárásokhoz, jelölésekhez. |
| 32 | Laptop (helyszíni konfiguráció) | Windows 10/11 laptop, Ethernet port vagy USB-C adapter | 1 db | ATR7000 webes felületének konfigurálásához telepítés közben; hálózati sniffer (Wireshark) futtatásához. |

---

## Opcionális / Jövőbeli Bővítés

| # | Megnevezés | Modell / Specifikáció | Megjegyzés |
|---|---|---|---|
| O1 | Zebra FMC3000 RFID kézi olvasó | Zebra FMC3000 (rugged, UHF) | Teljes leltározás kézből; nagyobb raktárhoz |
| O2 | Aktív RFID tag (valós idejű helymeghatározás) | Zebra MotionWorks tag vagy Ubisense | Ha cm-pontosságú RTLS szükséges (ATR7000 zónaszintű, nem cm-pontosságú) |
| O3 | IP kamera (zónafigyelés) | Axis P3245-V + NVR | Vizuális megerősítéshez az RFID riasztások mellé |
| O4 | Digitális kijelző (zóna-státusz) | 43" ipari monitor, Android-os keret | Raktári dashboardhoz |

---

## Megjegyzések a Méretezéshez

1. **Olvasók száma**: Az ATR7000 4 antennája 4 szektort fed. Nyílt raktárban mennyezetre szerelt antennákkal 1 olvasó kb. 600–900 m²-t fed le (antenna dőlésszögtől és polcelhelyezéstől függően). Állványos, sűrű raktárban ez 300–500 m²-re csökkenthet.

2. **Antenna magasság**: Optimális 4–6 m mennyezeti magasságban; 8 m felett a visszaverődések és a zóna-pontosság romlik. Magas raktárnál (+8 m) oldalsó antenna-elhelyezés is szükséges lehet.

3. **Fémkörnyezet**: Fémpolcok, acélváz erősen befolyásolja az RFID terjedést. Helyszínfelmérés (site survey) elvégzése kötelező a végleges antenna-terv előtt.

4. **Ethernet kábel**: ATR7000 csak Ethernet (PoE+) kapcsolatot használ, Wi-Fi nincs benne. Minden olvasóhoz saját Ethernet futam szükséges.

5. **Címke mennyiség**: Az éves forgatmány és a raklapok átlagos száma alapján becsülhető. Ha egy raklap átlagosan 3 hónapot tölt a rendszerben, 500 aktív raklaphoz ~500 db tag kell folyamatosan.
