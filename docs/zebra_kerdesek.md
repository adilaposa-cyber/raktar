# Zebra Viszonteladónak Felteendő Kérdések

**Zebra ATR7000 alapú RFID RTLS rendszer – Értékesítési és Műszaki Megbeszélés**
**Magyar gyártóvállalat számára**

---

## Bevezető

Az alábbi kérdéslistát a Zebra Technologies magyarországi viszonteladójával / disztribútorával tartandó megbeszélésre készítettük. A cél egy Zebra ATR7000 alapú, valós idejű helymeghatározáson (RTLS) alapuló raktárkezelő rendszer telepítése. Kérjük, minden kérdésre konkrét választ, dokumentációt vagy referenciát kérjen.

---

## 1. Lefedettség és Telepítési Tervezés

1.1. Egy ATR7000 olvasó (4 antennával) mekkora raktárterületet képes megbízhatóan lefedni?
- Nyílt, polcmentes területen?
- Sűrű állványzattal, fémpolcokkal?
- Mennyezeti magasságtól (4 m / 6 m / 9 m) hogyan függ ez?

1.2. Ajánlott-e a site survey (helyszíni felmérés) a telepítés előtt, és ez bele van-e a viszonteladói ajánlatba? Ki végzi el, és mennyi idő alatt?

1.3. Mekkora az antennák optimális dőlésszöge és iránya mennyezeti elhelyezésnél? Van-e ajánlott antenna-terv sablon raktárakhoz?

1.4. Milyen hatása van az alábbi akadályoknak az olvasási megbízhatóságra?
- Fémpolcok / acélszerkezet
- Fóliacsomagolású raklapok
- Nedves/fagyasztott áru
- Mozgó villástargoncák

1.5. Hogyan kezeli a rendszer az átmeneti „dead zone"-okat (lefedetlen területeket)? Van-e automatikus riasztás, ha egy tag kikerül minden olvasó látóteréből?

1.6. Hány olvasó és antenna szükséges az alábbi kapukhoz?
- Árubeérkezési kapu (8 m széles)
- Expedíciós kapu (8 m széles)
- Belső zónahatár átjáró

---

## 2. Tag Olvasási Távolság és Pontosság

2.1. Mi az ATR7000 maximális megbízható olvasási távolsága:
- Standard UHF passzív raklap-taggel?
- Fémre szerelt hard taggel (targonca)?
- Mozgás közben (pl. 10 km/h sebességű targonca)?

2.2. Milyen chip-típust ajánl (Impinj Monza R6, NXP UCODE 8, Alien Higgs-4 stb.) az alábbi alkalmazásokhoz?
- Raklap-azonosítás (kartonra ragasztott label)
- Targonca-azonosítás (fémre csavarozva)
- Gurulóeszköz (fémvázas kocsi)

2.3. Milyen olvasási megbízhatóság (read rate) érhető el tipikus raktárban?
- Statikus raklaptárolónál?
- Kapun áthaladó villástargoncánál?
- Célként legalább 95–98%-os read rate elvárható?

2.4. Az ATR7000 képes-e RSSI (jelszint) alapú helymeghatározásra, azaz meg tudja-e becsülni egy tag pozícióját az antennák közötti jelszint-különbségből? Milyen pontossággal (méterben)?

2.5. Tud-e a rendszer különbséget tenni szomszédos zónák között, ha azok között nincs fizikai határ (pl. 2 szomszédos raklap-pozíció a folyosón)?

2.6. Mennyi idő alatt kerül be egy újonnan belépő tag az olvasó látóterébe az első olvasásig (latency)?

---

## 3. Protokoll és Integráció

3.1. Az ATR7000 milyen protokollokon kommunikál?
- Támogatja-e az LLRP (Low Level Reader Protocol, ISO 15961) szabványt?
- Elérhető-e REST API vagy SOAP webszolgáltatás az olvasott adatokhoz?
- **Tud-e HTTP/HTTPS webhook push-t küldeni esemény alapon?** (pl. minden tag olvasáskor, vagy csak meghatározott tag látásakor)

3.2. Ha a webhook nem natív funkció: van-e Zebra szoftveres middleware (pl. Zebra SmartEdge, Zebra RFID Software Suite, Zebra DNA), amely az ATR7000 adatait HTTP-re konvertálja? Milyen licenszdíj vonatkozik erre?

3.3. Hogyan néz ki az adatfolyam részletesen?
- Milyen formátumban érkezik az adat (XML, JSON, binary)?
- Tartalmaz-e időbélyeget (UTC) és antenna-azonosítót?
- Elérhető-e az EPC kód mellett az RSSI érték és az olvasó ID is?

3.4. Elérhető-e szimulátoros / tesztkörnyezet (pl. Zebra 4X01 emulator vagy demo egység), amellyel az integráció fejlesztése elvégezhető a fizikai hardver telepítése előtt?

3.5. Milyen portokat kell megnyitni a tűzfalon az ATR7000 kommunikációjához?
- Webes konfiguráció portja?
- LLRP kommunikáció portja (alapértelmezett: 5084/TCP)?
- NTP időszinkron?
- Firmware-frissítés?

3.6. Hogyan konfigurálható a szűrés / filterezés az olvasóban?
- Be lehet-e állítani EPC prefix szerinti szűrést (csak saját tagek olvasása)?
- Configurable event filtering (pl. csak akkor küld eseményt, ha a tag 3 egymást követő olvasásban megjelent)?

3.7. Van-e Zebra által biztosított SDK (C#, Java, Python) az LLRP kommunikációhoz? Hol érhető el a dokumentáció?

3.8. **Infor LN integrációhoz**: Van-e ismert, kész connector vagy korábbi referencia projekt, ahol ATR7000-t integráltak ERP rendszerbe (SAP, Oracle, Infor)?

---

## 4. Garancia és Szerviz

4.1. Mi az ATR7000 olvasó gyártói garanciaideje (Zebra), és ez milyen feltételekkel érvényes?
- On-site csere vagy depot repair modell?
- Mi a garantált válaszidő (NBD – Next Business Day, 4 óra stb.)?

4.2. Van-e Zebra OneCare szervizcsomag az ATR7000-hez? Mik a csomagok (Essential, Select, Premier) és mi a különbség köztük?

4.3. Mi a csereegység (swap unit) eljárás meghibásodás esetén?
- Mennyi idő alatt szállítanak csereolvasót Magyarországra?
- Van-e helyi (magyarországi / közép-európai) raktár a Zebra szervizpartnernek?

4.4. Mi a garantált firmware-támogatási időszak az ATR7000-re? Meddig várható biztonsági javítás és funkcionális frissítés?

4.5. Mi a helyszíni szerviz lehetősége? Van-e helyi Zebra-tanúsított szerviztechnikus Magyarországon?

4.6. Mi a berendezés átlagos élettartama (MTBF) az ATR7000-re? Rendelkezésre áll-e az MTBF adatlap?

---

## 5. Árazás és Licencek

5.1. Mi az ATR7000 listaára (EUR), és milyen kedvezményi szintek érhetők el mennyiségtől függően (pl. 4, 8, 16 db esetén)?

5.2. Az ATR7000 szoftver-licenszt igényel-e a basic LLRP / REST API használathoz? Ha igen, mi az éves díj?

5.3. Mi az ajánlott UHF RFID tag-ek (raklap label, hard tag targoncára) egységára kis (1 000 db) és közepes (10 000 db) mennyiségnél?

5.4. Mi a Zebra SmartEdge / RFID middleware licenszdíja, ha szükséges? Felhasználószám vagy olvasószám alapú az árazás?

5.5. Tartalmaz-e az ajánlat site survey-t, és ha igen, ennek külön díja van-e, vagy az ajánlatba számítódik?

5.6. Mi a tipikus telepítési / üzembe helyezési díj 4–6 ATR7000 olvasóból álló rendszernél (Magyarországon)?

5.7. Van-e éves karbantartási díj (maintenance fee) a hardverre és/vagy a szoftverre, és ez mit tartalmaz?

5.8. Nyújtható-e operatív lízing lehetőség (hardware-as-a-service) az ATR7000 olvasókra?

---

## 6. ATR7000 Specifikus Technikai Kérdések

6.1. Az ATR7000 beépített webszervere milyen konfigurációs lehetőségeket kínál?
- IP-cím beállítás (DHCP / statikus)?
- Antenna power szint (dBm) hangolása antennánként?
- Read mode: single, inventory, vagy event-based üzemmód?

6.2. **HTTP Webhook**: Az ATR7000 natívan tud-e HTTP POST kérést küldeni egy megadott URL-re minden tag-olvasási eseménynél? Ha igen:
- Milyen JSON/XML struktúrában?
- Konfigurálható-e az URL és a küldési feltétel (minden olvasás, vagy csak belépés/kilépés esemény)?
- Elérhető-e TLS/HTTPS webhook?

6.3. Az ATR7000 képes-e egyszerre több olvasási munkamenetet kezelni (több LLRP kliens párhuzamosan)?

6.4. Milyen antenna csatlakozót használ az ATR7000 (RP-TNC, N-type, TNC)? Mi a maximális antenna port szám?

6.5. Mi a maximális RF kimeneti teljesítmény (dBm / mW) antennánként EU-ban (865–868 MHz sáv)?

6.6. Az ATR7000 rendelkezik-e beépített Impinj-féle „TagFocus" vagy hasonló anti-collision funkcióval? Hogyan kezeli a dense reader environment-et?

6.7. Milyen a fizikai burkolat védettsége (IP minősítés)? Beltéri, por/páramentes, ipari raktárban működik-e csomagolás nélkül?

6.8. Az ATR7000 firmware frissíthető-e távolról (over-the-air / OTA), és ez mennyi leállással jár?

---

## 7. Helyszínfelmérés (Site Survey)

7.1. Milyen adatokat kell előzetesen megadnunk a site survey-hez?
- Alaprajz (DXF / PDF formátum elegendő-e)?
- Polcrendszer elrendezése (magasság, anyag, sűrűség)?
- Forgalmi utak, kapuhelyek?
- Meglévő hálózati infrastruktúra helyszíne?

7.2. A site survey magában foglalja-e az alábbiak elvégzését?
- RF spektrumelemzés (rádiózaj mérése)?
- Próbaolvasási teszt demo hardverrel?
- Antenna-terv és olvasó-elhelyezési terv dokumentálása?
- Javasolt kábelfutás terv?

7.3. Mennyi ideig tart a site survey helyszínen, és szükséges-e a raktár részleges leállítása?

7.4. A site survey után kapunk-e írott jelentést, amely tartalmaz:
- Antenna elhelyezési alaprajzot?
- Várható lefedettségi térképet?
- Interferencia-kockázatok listáját?

7.5. Elvégezhető-e a site survey egy munkanap alatt, vagy több napos mérés szükséges?

---

## 8. Betanítás és Üzembe Helyezés

8.1. Milyen betanítási lehetőségeket kínálnak a rendszer üzemeltetéséhez?
- Helyszíni képzés (on-site training)?
- Zebra online tanfolyam (eLearning)?
- Zebra-tanúsítvány elérhető-e a technikusaink számára?

8.2. Az üzembe helyezési (commissioning) folyamat mennyi napot vesz igénybe tipikusan 4–6 olvasós rendszernél?

8.3. Tartalmaz-e az üzembe helyezés az alábbi lépéseket?
- Fizikai telepítés és kábelezés?
- Olvasók hálózati konfigurációja?
- Antenna finomhangolás (read power, tilt)?
- Integrációs teszt (LLRP / API szinten)?
- Felhasználói elfogadási teszt (UAT) levezetése?

8.4. Biztosítanak-e telefonos / remote támogatást az első 3 hónapban az üzembe helyezés után?

8.5. Van-e dokumentáció (angol vagy magyar) az ATR7000 konfigurálásához és hibaelhárításához, amely átadható a saját IT-csapatunknak?

8.6. Hogyan kezeljük a rendszer bővítését (új olvasók hozzáadása)? Ehhez szükséges-e a viszonteladó bevonása, vagy saját technikusaink elvégezhetik?

---

## 9. Referenciák és Tapasztalat

9.1. Van-e Magyarországon (vagy Közép-Kelet-Európában) élő referencia, ahol Zebra ATR7000 alapú RTLS rendszert üzemelnek termelési raktárban?
- Felkereshető-e a referencia helyszín?
- Milyen iparágban (autóipar, élelmiszer, gyógyszer stb.)?

9.2. Hány Zebra ATR7000 telepítés van a portfóliójukban? Mekkora volt a legnagyobb projekt (olvasók száma, négyzetméter)?

9.3. Van-e tapasztalatuk ERP-integrációval (SAP WM/EWM, Infor LN, Oracle WMS)? Milyen integrációs réteget alkalmaztak?

9.4. Mi volt a leggyakoribb probléma a telepítések során, és hogyan oldották meg?

---

## 10. Egyéb

10.1. Milyen szállítási határidővel számolhatunk az ATR7000 olvasókra Magyarországra?
- Raktárkészletről azonnal?
- Rendelésre: hány hét?

10.2. Lehetséges-e demo / pilot egységet kölcsönözni (1–2 ATR7000 + antennák) a PoC (Proof of Concept) fázishoz, mielőtt a teljes rendszert megrendeljük?

10.3. Mi a minimálisan megrendelhető mennyiség (MOQ) az ATR7000-re és a tagekre?

10.4. Milyen fizetési feltételeket kínálnak (előre / szállításra / 30-60-90 nap)?

10.5. Rendelkezésre áll-e CE-jelölési dokumentáció az ATR7000-hez, amely szükséges a magyarországi üzemeltetéshez?
