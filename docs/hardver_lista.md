# RFID RTLS Rendszer – Hardver Bevásárlólista

**Zebra ATR7000 alapú raktárkezelő rendszer**
**Magyar gyártóvállalat számára**

---

## A rendszer felépítése: mennyezeti ATR7000, nem kapus

A rendszer **nem** áthaladás-érzékelő kapukra épül. Mennyezetre lógatott Zebra
ATR7000 olvasók folyamatosan látják a tageket az alattuk lévő területen, és
irányszöget mérnek hozzájuk – ebből jön ki, melyik zónában van az eszköz.
Nem kell kapun áthaladni ahhoz, hogy a rendszer tudja, hol a kocsi.

**Fontos a beszerzéshez:** az ATR7000 beépített fázisvezérelt antennasorral
dolgozik, **nem kell hozzá külön antenna és koaxiális kábel** – ez a
FX-sorozat (FX9600/FX7500) jellemzője, amit kapus felállásnál használnának.
Ezért ebben a listában nincs külön antenna és LMR-400 tétel.

## Előfeltételek és méretezési alapelvek

- Tipikus csarnokméret: 1 000–7 000 m²
- Lefedettség: 1 ATR7000 kb. **600–900 m²** nyílt téren, **300–500 m²** sűrű
  fémpolcos / fémvázas környezetben
- Optimális felfüggesztési magasság: 4–6 m; 8 m felett romlik a zónapontosság
- Tervezéskor +20–25% redundancia, hogy egy kiesett olvasó ne vakítson meg zónát
- Referencia (anchor) tagek fix pontokon: a koordináta-kalibrációhoz kellenek,
  mennyezeti felállásnál nem opcionálisak
- Az alábbi mennyiségek egy ~3 000 m²-es csarnokra vonatkoznak; skálázható

---

## Hardver Lista

| # | Megnevezés | Modell / Specifikáció | Mennyiség | Megjegyzés |
|---|---|---|---|---|
| **RFID OLVASÓK** | | | | |
| 1 | Mennyezeti RTLS olvasó | Zebra ATR7000 UHF RFID RTLS Reader | 6–8 db | ~3 000 m²-es csarnokhoz, sűrű fémkörnyezetre méretezve. Beépített fázisvezérelt antennasor – külső antenna NEM kell. Ethernet + PoE+ (802.3at); LLRP; beépített webszerver. |
| 2 | ATR7000 mennyezeti szerelőkészlet | Zebra gyári mennyezeti/gerenda konzol | 6–8 db | Olvasónként 1 db. Beton- és acélvázhoz is; a dőlésszög állítható. |
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
| 21 | Címkenyomtató (RFID kódolós) | Zebra ZT411 **RFID** kivitel, UHF encoder | 1–2 db | A raklap- és kocsicímkék nyomtatása + EPC kódolása egy lépésben. FIGYELEM: a sima ZT411 nem tud RFID-t, csak az RFID kivitel vagy utólag beszerelt RFID kit. Ellenőrzés: konfigurációs címke nyomtatása – ha van RFID modul, megjelenik rajta a reader firmware verziója. |
| 22 | Emelőkosár / görgős állvány bérlés | 8–12 m munkamagasság | 2–4 nap | A mennyezeti olvasók felszereléséhez. Kapus felállásnál nem kellene, itt igen – tervezd be. |
| 23 | Ipari műanyag kábelvédő cső (flex) | Kopex / Anamet 20 mm flexibilis fémszálas kábelvédő | 30–50 fm | Hálózati kábelek védelmére azokon a szakaszokon, ahol mechanikai behatás érhet (villás emelő útvonal). |
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

1. **Olvasók száma**: Az ATR7000 a beépített antennasorával sugárnyalábot pásztáz maga alatt. Nyílt csarnokban 1 olvasó kb. 600–900 m²-t fed le, sűrű fémpolcos környezetben 300–500 m²-t. A rendszer zóna-pontosságú (tipikusan 1–3 m), nem centiméteres – szerelőállások megkülönböztetésére elég, raklapon belüli pozícióra nem.

2. **Felfüggesztési magasság**: Optimális 4–6 m; 8 m felett a visszaverődések és a zónapontosság romlik. Magas csarnoknál oldalsó kiegészítő olvasók is kellhetnek.

3. **Fémkörnyezet**: Fémpolcok, acélváz erősen befolyásolja az RFID terjedést. Helyszínfelmérés (site survey) elvégzése kötelező a végleges antenna-terv előtt.

4. **Ethernet kábel**: ATR7000 csak Ethernet (PoE+) kapcsolatot használ, Wi-Fi nincs benne. Minden olvasóhoz saját Ethernet futam szükséges.

5. **Címke mennyiség**: Az éves forgatmány és a raklapok átlagos száma alapján becsülhető. Ha egy raklap átlagosan 3 hónapot tölt a rendszerben, 500 aktív raklaphoz ~500 db tag kell folyamatosan.
