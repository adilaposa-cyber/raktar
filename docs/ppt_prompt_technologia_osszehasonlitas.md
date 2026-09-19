# Prompt: PPT a szerelde kocsikövetés technológiaválasztásáról

> Ezt a teljes fájlt másold be egy AI-nak (Claude, ChatGPT, Gamma, stb.), és
> kérj tőle prezentációt. A benne lévő minden szám a saját tervezőnkből és a
> `docs/1_fazis_szerelde_pilot.md` költségbecslésből származik.

---

## A FELADAT

Készíts **16–18 diás magyar nyelvű PowerPoint prezentációt**, ami bemutatja
és összehasonlítja a három szóba jöhető helymeghatározó technológiát egy
konkrét ipari feladatra, és megindokolja a javaslatot.

**Közönség:** üzemvezetés és IT döntéshozók. Nem RF-mérnökök. A fizikát
érthetően, de nem lebutítva kell elmagyarázni – azt kell megérteniük, **miért**
ad az egyik technológia jobb eredményt ugyanabban a csarnokban.

**Hangnem:** tárgyilagos, mérnöki. Ne legyen marketinges. Ahol becslés van,
mondd meg, hogy becslés. Ahol bizonytalanság van, nevezd meg.

**Fontos szerkesztési elv:** ne a technológiák általános dicséretét sorold,
hanem mindig erre a konkrét feladatra vonatkoztasd. Ugyanaz a technológia más
feladatra más eredményt adna – ezt mondd is ki.

---

## A KONKRÉT FELADAT, AMIRE A VÁLASZTÁS SZÓL

| Paraméter | Érték |
|---|---|
| Helyszín | Szerelde csarnok, 4270 John Deere és 4392 középsorozatú futómű szerelősor |
| Alapterület | kb. 3 000 m² (mérendő – ez az egyetlen bizonytalan bemenet) |
| Követett eszköz | **20 db komissiózó kocsi** – nem raklap, nem göngyöleg |
| Pontossági igény | **Hely szint**: melyik szerelőálláson áll a kocsi (15 állás + 3 folyosó + hátralékos sáv + kész zóna) |
| Környezet | Sűrű fémpolcos, acélvázas csarnok, sűrű targoncaforgalom |
| Belmagasság | 5,5 m szerelési magasság |
| Meglévő | Strukturált hálózat van, szabad PoE+ port nincs |
| Fő üzleti cél | Ha egy kocsi a folyosón áll 5 percnél tovább → riasztás. Plusz: melyik álláson mennyi kocsi van, és mióta |
| Infor LN | **Ebben a fázisban nem kell** – a komissiózó kocsi nem Handling Unit az LN-ben |

---

## A HÁROM TECHNOLÓGIA – MŰKÖDÉSI ELV

Ezt a részt érthetően, ábrával magyarázd el. Ez a prezentáció lelke: ha ezt
megértik, a következtetés magától adódik.

### 1. Passzív UHF RFID (Zebra ATR7000)

- A címkében **nincs elem**. Az olvasó rádióenergiát sugároz ki, a címke ebből
  táplálkozik, és **visszaveri** a jelet a saját azonosítójával (backscatter).
- Az ATR7000 egy **fázisvezérelt antennasorral** pásztázza maga alatt a
  területet, és a visszaérkező jel szögéből becsül irányt.
- **Erőssége:** a címke fillérekbe kerül (0,08–0,18 EUR) és örökké bírja.
- **Gyengéje:** a visszavert jel nagyon gyenge, és a fém mindent visszaver –
  ezért fémes környezetben drasztikusan romlik a lefedettség. Ebben a
  csarnokban a névleges lefedettség **55%-ra esik**.

### 2. UWB – ultraszéles sávú, futásidő alapú

- A tagban **van elem**, aktívan adó. Nagyon rövid, széles sávú impulzusokat
  küld, a horgonyok pedig azt mérik, **mennyi idő alatt** ér oda a jel.
  Idő × fénysebesség = távolság; több távolságból háromszögelés.
- A széles sáv miatt a rendszer **meg tudja különböztetni a közvetlen jelutat
  a visszaverődésektől** – ezért tűri legjobban a fémet.
- **Erőssége:** 10–30 cm pontosság akkor is, ahol minden fémből van.
- **Gyengéje:** a tag drága (30–80 EUR) és elemes; a 2D helymeghatározáshoz
  legalább **négy** horgonynak látnia kell a taget.

### 3. BLE AoA – Bluetooth, beérkezési szög alapú

- A tag olcsó BLE hirdetést sugároz. A lokátor egy antennasorral azt méri,
  **milyen szögből** érkezik a hullámfront.
- Egyetlen lokátor is ad irányt, ezért **kevesebb egység kell** – de mindegyik
  drágább.
- **Erőssége:** a legolcsóbb tag (10–30 EUR) a **leghosszabb elemélettel**
  (3–5 év). Sok száz eszköznél verhetetlen.
- **Gyengéje:** a szögmérést a fémről verődő jel elhúzza – hamis irányt ad.
  Ebben a csarnokban a várható pontosság **0,8–2,3 m**.

> **Az egymondatos lényeg, amit a diákon is ki kell emelni:**
> a passzív UHF a *címkén* spórol, az UWB a *pontosságot* veszi meg,
> a BLE AoA a *sok tag* olcsó követésére való.

---

## TELEPÍTÉSI TERV – MINDHÁROM VÁLTOZAT RÉSZLETESEN

Ezekből külön dia készüljön technológiánként. A „hol és milyen magasan"
kérdést ábrán is mutasd meg.

### A) Passzív UHF – Zebra ATR7000

| Tétel | Érték |
|---|---|
| **Olvasó** | **17 db** Zebra ATR7000 |
| Elrendezés | 13,3 m-es négyzetrács a teljes követett terület fölött |
| **Szerelési magasság** | **5,5 m**, mennyezetre függesztve (optimum 4–6 m; 8 m fölött romlik) |
| Lefedettség | 219 m² / olvasó (a névleges 400 m² esik erre a fémtől) |
| Antenna | **Nem kell külön antenna** – beépített fázisvezérelt antennasor. Koax kábel sem kell. |
| Tápellátás | PoE+ (802.3at, max 25 W/port). Sima 802.3af **nem elég**. |
| Hálózat | 19 PoE+ port, 955 fm Cat6A S/FTP, max. 90 m/futam |
| Rögzítés | Gyári mennyezeti/gerenda konzol olvasónként, állítható dőlésszöggel |
| Tag | 20 db on-metal hard tag (Confidex Ironside vagy hasonló), fémre csavarozható |
| Referencia tag | 20–30 db fix ponton, koordináta-kalibrációhoz |
| Telepítés | Emelőkosár 6 nap, hangolás 4 nap, site survey 2 nap |
| Pontosság | 1–3 m (zóna szint) |

### B) UWB

| Tétel | Érték |
|---|---|
| **Horgony (anchor)** | **18 db** |
| Elrendezés | **3 sor × 4 horgony**, a csarnok pereme közelében: felső él, középvonal, alsó él. Rácstávolság 12,9 m. |
| **Miért így** | A 2D helymeghatározáshoz legalább 4 horgonynak látnia kell a taget, és **nem eshetnek egy vonalba** – ezért kell a három sor, nem elég egy sorfal. |
| **Szerelési magasság** | **5,5 m**, mennyezetre függesztve, lehetőleg szabad rálátással |
| Lefedettség | 226 m² / horgony |
| Tápellátás | PoE, 20 port |
| Hálózat | 1 011 fm Cat6 |
| Tag | 20 db aktív UWB tag, elemmel; kocsira csavarozva |
| Pozíciószámítás | Központi UWB motor (szerver vagy beágyazott egység) – ez számol, nem a horgonyok |
| Telepítés | Site survey 2 nap, szerelés 6 nap, kalibráció 3 nap |
| Pontosság | **0,1–0,3 m** |
| Karbantartás | Elemcsere 1–3 évente, 20 tagnál évi 40–120 EUR |

### C) BLE AoA

| Tétel | Érték |
|---|---|
| **Lokátor** | **18 db** |
| Elrendezés | Hasonló rács, 12,9 m; egy lokátor magában is ad irányt, de a takarás miatt átfedés kell |
| **Szerelési magasság** | **5,5 m**, mennyezetre, az antennasor síkja vízszintesen, lefelé néz |
| Lefedettség | 207 m² / lokátor |
| Tápellátás | PoE, 20 port |
| Hálózat | 1 011 fm Cat6 |
| Tag | 20 db BLE tag, 3–5 év elemélet |
| Telepítés | Site survey 2 nap, szerelés 6 nap, **szögkalibráció 4 nap** (hosszabb, mint a futásidős rendszereké) |
| Pontosság | **0,8–2,3 m** ebben a fémes környezetben |
| Karbantartás | Elemcsere 3–5 évente, évi 15–40 EUR |

---

## KÖLTSÉG-ÖSSZEHASONLÍTÁS

Ez legyen a prezentáció fő táblázata. Mindenhol min–max sáv, mert a
gyártónkénti szórás nagy.

| Tétel | Passzív UHF | UWB | BLE AoA |
|---|---|---|---|
| Egység | 17 olvasó | 18 horgony | 18 lokátor |
| Egység ára | 30 600 – 42 500 | 4 500 – 10 800 | 7 200 – 27 000 |
| Tag (20 db) | 10 – 22 | 600 – 1 600 | 200 – 600 |
| Platform licenc | – | 2 000 – 12 000 | 3 000 – 15 000 |
| Hálózat | 2 510 – 5 020 | 2 622 – 5 244 | 2 622 – 5 244 |
| Telepítés, kalibráció | 7 200 – 12 300 | 5 400 – 9 200 | 6 400 – 11 000 |
| Konzol, emelőkosár | 1 330 – 3 450 | benne | benne |
| **BERUHÁZÁS ÖSSZESEN** | **41 650 – 63 292** | **15 122 – 38 844** | **19 422 – 58 844** |
| Éves költség (elem) | 0 | 40 – 120 | 15 – 40 |
| Pontosság | 1–3 m | **0,1–0,3 m** | 0,8–2,3 m |

*Minden érték EUR. 400 HUF/EUR árfolyamon az UWB 6,0–15,5 MFt.*

---

## A JAVASLAT ÉS AZ INDOKLÁS

**Javaslat: UWB.** Három érv, ebben a sorrendben:

1. **A pontosság dönt, nem az ár.** Hely szintű követés kell: meg kell tudni
   mondani, melyik szerelőálláson áll a kocsi. Ha az állások 5–8 m szélesek,
   a BLE AoA fémes környezetben várható 2,3 m-es hibája már összemoshat két
   szomszédos állást. Az UWB 0,1–0,3 m-e ezt kizárja.
2. **Ráadásul ez a legolcsóbb is.** 15 122 – 38 844 EUR, szemben a passzív UHF
   41 650 – 63 292 EUR-jával. A passzív UHF-nél nem a technológia rossz, hanem
   az olvasó egységára (1 800–2 500 EUR) és a fémtől megkövetelt sűrű rács
   szorzata.
3. **20 eszköznél a tag ára nem számít.** Ez fontos, mert ez borítja fel a
   szokásos érvelést: a passzív UHF fő előnye – az olcsó, elemmentes címke –
   ezen a darabszámon (10–22 EUR összesen) semmit nem nyom a latban.

### Mikor lenne más a válasz – ezt is tedd diára

| Ha a feladat… | Akkor… | Mert… |
|---|---|---|
| 2 000 raklap, elég a zóna szint | **Passzív UHF** | A 0,08–0,18 EUR-os címkét semmi nem veri; 2 000 aktív tag 60–160 ezer EUR lenne |
| 2 000 eszköz, de hely szint kell | **BLE AoA** | A passzív UHF nem ad pozíciót, csak zónaátlépést; az UWB tag ennyinél megfizethetetlen |
| 20 eszköz, hely szint, fémes | **UWB** ← *a mi esetünk* | A fém a szöget és a visszaszórást rontja, a futásidőt nem |
| Tiszta tér, kevés eszköz, zóna szint | Passzív UHF | Ott a névleges 750 m²/olvasó érvényesül, kevés olvasó elég |

---

## KOCKÁZATOK ÉS NYITOTT KÉRDÉSEK – KÜLÖN DIA

Ezt ne hagyd ki. A hitelességet ez adja.

1. **A szerelde alapterülete mérendő.** A 3 000 m² becslés. 1 500 m²-nél az
   UWB 9 horgony és 10 500–29 000 EUR; 3 000 m²-nél 18 horgony és
   15 100–38 800 EUR. Ez az egyetlen bemenet, ami érdemben mozgatja az árat.
2. **A platform licencdíj a legbizonytalanabb tétel.** Ekkora területen eléri
   vagy meghaladja a horgonyok árát. Kérdezd meg: egyszeri vagy éves?
   Tagenként vagy horgonyonként? Benne van a frissítés?
3. **Az anchorszám modellbecslés.** A fémpolcok tényleges takarását helyszíni
   felmérés dönti el. Komoly szállító ezt ajánlatadás előtt megcsinálja.
4. **Kérj referenciát fémes gyártócsarnokból, mért pontossággal** – ne
   katalógusadatot. A gyártók jellemzően tiszta térben mért számokat közölnek.
5. **Elem élettartama a tervezett frissítési gyakoriságnál.** 1 Hz-es
   frissítésnél rövidebb, ritkábbnál hosszabb.

---

## AMI MÁR KÉSZ – KÜLÖN DIA A MELLÉKELT KÉPPEL

A szoftver oldala nem korlátoz és nem függ a technológiaválasztástól:

- A követő rendszer **már működik**: a mellékelt képernyőkép a szerelde élő
  alaprajzát mutatja, 20 kocsival, 12 horgonnyal, a 4270-es és 4392-es sorral,
  a három folyosóval, a hátralékos sávval és a kész hidak területtel.
- A beolvasó végpont **koordinátát vár**, és nem érdekli, mi állította elő –
  `{ reader_id, tag_epc, x, y }`. Bármelyik technológia ezt tudja küldeni.
- Ami a szoftverben megvan: billegésvédelem a zónahatáron (határsáv +
  megállapodási idő), kitárolt riasztás, mozgásnapló, és – ha egyszer kell –
  Infor LN lejelentés.
- **Ez azt jelenti, hogy a technológiaválasztás tisztán hardverdöntés.**

---

## JAVASOLT DIASZERKEZET

1. Címdia – „Kocsikövetés a szereldében: technológiaválasztás"
2. A feladat – mit akarunk elérni, üzleti célok
3. A követendő eszköz – 20 komissiózó kocsi, 15 állás, 3 folyosó
4. **A mellékelt szerelde térkép** – ez már működik
5. Mitől függ a választás – darabszám, pontosság, környezet
6. Passzív UHF RFID – hogyan működik
7. UWB – hogyan működik
8. BLE AoA – hogyan működik
9. A fizika lényege – miért rontja a fém máshogy mindhármat
10. Telepítési terv: passzív UHF (17 olvasó, 5,5 m, 13,3 m rács)
11. Telepítési terv: UWB (18 horgony, 3 sor, 5,5 m)
12. Telepítési terv: BLE AoA (18 lokátor, 5,5 m)
13. **Költség-összehasonlítás** – a fő táblázat
14. Pontosság-összehasonlítás – ábrával, az állásszélességhez viszonyítva
15. **A javaslat és a három érv**
16. Mikor lenne más a válasz – a döntési mátrix
17. Kockázatok és nyitott kérdések
18. Következő lépések – felmérés, ajánlatkérés, pilot

---

## VIZUÁLIS ELVÁRÁSOK

- Világos háttér, sötétkék kiemelés. Ipari, nem játékos.
- Technológiánként **egy-egy szín végig** a prezentációban:
  passzív UHF = kék, UWB = ciánkék, BLE AoA = lila.
- A költségtáblázatban a sávot **vízszintes sávdiagrammal** is mutasd, ne csak
  számmal – a min–max szórás így látszik.
- A pontosság-diára rajzolj egy szerelőállást méretarányosan, és jelöld be a
  három technológia hibasávját. Ez a legmeggyőzőbb ábra.
- A mellékelt szerelde térkép teljes szélességű dián szerepeljen.
- Ne legyen stock fotó. Ha kell ábra, rajzold.
