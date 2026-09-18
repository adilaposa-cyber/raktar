# 1. fázis – Szerelde pilot: 20 komissiózó kocsi követése

**Hatókör:** kizárólag a szerelde, kizárólag a komissiózó kocsik.
**Nem tartozik ide:** raklapok, göngyöleg, raktári zónák, targoncás modul,
Infor LN lejelentés. Ezek a 2. fázis tételei, ami egyelőre bizonytalan.

**Árfolyam: 1 EUR = 400 HUF (tájékoztató)**

> Az árak tájékoztató jellegűek és gyártónként erősen szórnak. A felső és az
> alsó érték is reális; a tényleges összeg ajánlatkéréstől függ.

---

## Miért UWB és nem passzív UHF ebben a fázisban

A `docs/koltseg_becsles.md` a teljes üzemre, ATR7000 passzív UHF alapon készült.
Erre a szűkebb feladatra más a helyes válasz, három okból:

1. **20 eszköznél a tag ára nem számít.** Passzív UHF hard tag 10–22 EUR
   összesen, aktív UWB tag 600–1600 EUR. Mindkettő elhanyagolható a
   beruházás mellett. A passzív UHF fő előnye – az olcsó, elemmentes tag –
   ezen a darabszámon nem előny.
2. **Hely szintű pontosság kell.** Ha látni akarjuk, melyik álláson áll a
   kocsi, a passzív UHF-nek sűrű rács kell: fémpolcos, acélvázas környezetben
   ~219 m²/olvasó. Az UWB futásidőt mér, nem visszaszórást, ezért a fém
   feleannyira rontja.
3. **Az egységár a döntő.** Az anchorszám hasonló (~18 vs ~17 db 3 000 m²-en),
   de egy UWB anchor 250–600 EUR, egy ATR7000 pedig 1 800–2 500 EUR.

Összehasonlítás 3 000 m²-re, hely szintű pontossággal:

| | darab | beruházás |
|---|---|---|
| ATR7000 passzív UHF | 17 olvasó | 41 700 – 63 300 EUR |
| **UWB** | 18 anchor | **15 100 – 38 800 EUR** |

---

## Költség a szerelde méretének függvényében

A méret az egyetlen bemenet, amit meg kell mérni. Minden sor hely szintű
pontosságra, 20 kocsira, fémpolcos/acélvázas környezetre, meglévő hálózattal
és szabad PoE port nélkül számol.

| Szerelde alapterület | Anchor | Kábel | Beruházás (EUR) | Beruházás (eFt) |
|---|---|---|---|---|
| 1 500 m² | 9 db | 417 fm | 10 500 – 29 000 | 4 200 – 11 600 |
| 2 000 m² | 12 db | 600 fm | 12 000 – 32 200 | 4 800 – 12 900 |
| 2 500 m² | 15 db | 799 fm | 13 500 – 35 500 | 5 400 – 14 200 |
| 3 000 m² | 18 db | 1 011 fm | 15 100 – 38 800 | 6 000 – 15 500 |

### A tételek bontása (3 000 m²-es példa)

| Tétel | EUR min–max | Megjegyzés |
|---|---|---|
| UWB anchor (18 db) | 4 500 – 10 800 | 250–600 EUR/db, gyártónként szór |
| Aktív UWB tag (20 db) | 600 – 1 600 | 30–80 EUR/db, elemmel |
| **Platform licenc** | **2 000 – 12 000** | **Ez a legbizonytalanabb és leginkább alkuképes tétel** |
| Hálózat: Cat6 1 011 fm + PoE switch | 2 600 – 5 200 | Meglévő strukturált hálózatot feltételez |
| Site survey, telepítés, kalibráció | 5 400 – 9 200 | 2 nap felmérés + 9 nap szerelés + 3 nap hangolás |
| **Összesen** | **15 100 – 38 800** | **6 000 – 15 500 eFt** |

---

## Amire feltétlenül rá kell kérdezni ajánlatkéréskor

1. **A platform licencdíj szerkezete.** Ekkora területen a licenc eléri vagy
   meghaladja az anchorok árát. Kérdések: egyszeri vagy éves? Tagenként vagy
   anchoronként számolják? Benne van-e a szoftverfrissítés?
2. **Hány anchor kell ténylegesen.** A 18-as szám modellbecslés. A fémpolcok
   és a szerelősorok tényleges takarása helyszíni felméréssel derül ki –
   komoly szállító ezt ajánlatadás előtt megcsinálja.
3. **Elem élettartama a tervezett frissítési gyakoriságnál.** 1 Hz-es
   pozíciófrissítésnél rövidebb, ritkábbnál hosszabb. 20 tagnál az évi
   elemcsere 40–120 EUR és néhány óra munka.
4. **Nyitott-e a kimenet.** A rendszernek REST/MQTT-n koordinátát kell tudnia
   kiadni (lásd alább). Zárt, csak saját felülettel rendelkező megoldás nem jó.

---

## Amit ez a fázis NEM igényel

**Infor LN integráció nem kell.** A komissiózó kocsi nem Handling Unit az
LN-ben – belső szállítóeszköz. A rendszer LN kapcsolat nélkül DRY-RUN módban
fut: minden mozgás naplózódik, de nem megy ki BOD. Ez pontosan megfelelő egy
pilothoz, és megspórolja a legnagyobb szoftvertételt (az ION integráció
fejlesztése 7 000 – 20 000 EUR nagyságrend).

Ha később mégis kell, a kapcsolat bekapcsolható: a lejelentés logikája kész
van, csak a környezeti változókat kell kitölteni.

**Nem kell címkenyomtató sem.** A ZT411 RFID kérdés a raklapcímkékről szólt –
azok a 2. fázisban jönnek. A 20 kocsi UWB tagje gyárilag azonosított.

---

## A szoftver oldala: nincs átírás

Az alkalmazás beolvasó végpontja koordinátát vár, és nem érdekli, mi
állította elő:

```
POST /api/rtls/ingest
Authorization: Bearer <RFID_INGEST_TOKEN>

{ "reader_id": "UWB-MOTOR", "tag_epc": "<tag azonosító>", "x": 555, "y": 150 }
```

Innen a terület alaprajza dönti el, melyik álláson van a kocsi. A
billegésvédelem (határsáv + megállapodási idő), a mozgásnapló, a kitárolt
riasztás és – ha egyszer bekapcsoljuk – az Infor LN lejelentés változatlanul
működik.

A UWB rendszert egyetlen logikai olvasóként kell felvenni (`area_readers`),
mert a pozíciót a UWB motor számolja, nem az egyes anchorok.

---

## Ha később mégis jön a 2. fázis (raklapok, RFID)

Az UWB választás nem zárja ki, és nem is drágítja:

- A raklapokra **akkor is passzív UHF kell**, mert 2 000 hordozóhoz aktív tag
  60 000 – 160 000 EUR lenne. A két technológia külön területen dolgozik.
- A szoftver ugyanaz marad: a `/teruletek` a szereldét kezeli UWB-ből, a
  raktártérkép a raklapokat UHF-ből.
- A szereldei UWB beruházás nem válik feleslegessé.

Az egyetlen többletköltség a két technológia párhuzamos üzemeltetése: külön
tartalék alkatrész és külön gyártói kapcsolat. Mivel a szerelde amúgy is
elkülönül, ez itt kisebb teher, mint általában.
