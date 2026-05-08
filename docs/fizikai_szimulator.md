# Fizikai RFID Szimulátor – 3D nyomtatott raktármodell

## Áttekintés

Ez egy asztali méretű fizikai szimulátor, ami az igazi RFID rendszert modellezi:
- 3D nyomtatott raktárpolcok és zónák
- Kis RFID kártyák = raklapok
- ESP32 vagy Raspberry Pi RFID olvasók kapuknál
- LED-ek mutatják a zóna foglaltságát
- Az egész "üzemi méretű" szoftvert hajtja valódi HTTP eseményekkel

---

## Alkatrész lista (teljes)

### 1. Elektronika

| Alkatrész | Modell | Db | Ár (kb.) | Forrás |
|-----------|--------|----|----------|--------|
| Mikrokontroller | ESP32-WROOM-32 DevKit | 6 | 6 × ~2.500 Ft | AliExpress / Hestore |
| RFID olvasó | MFRC522 13.56 MHz modul | 6 | 6 × ~800 Ft | AliExpress |
| RFID kártyák | MIFARE Classic 1K fehér kártya | 20 | 20 × ~100 Ft | AliExpress |
| RFID kulcstartók | NTAG213 kulcstartó | 20 | 20 × ~150 Ft | AliExpress |
| LED (zöld) | 5mm zöld LED | 20 | csomag ~300 Ft | Hestore |
| LED (piros) | 5mm piros LED | 20 | csomag ~300 Ft | Hestore |
| LED (sárga) | 5mm sárga LED | 10 | csomag ~200 Ft | Hestore |
| Ellenállás | 220Ω, 470Ω válogatás | 50 | csomag ~200 Ft | Hestore |
| Breadboard | 830 pontos | 6 | 6 × ~600 Ft | Hestore |
| Jumper kábel | Dugó-dugó 20cm | 3 csomag | ~1.500 Ft | Hestore |
| USB töltő | 5V 2A micro-USB | 6 | 6 × ~1.200 Ft | AliExpress |
| USB kábel | Micro-USB 1m | 6 | 6 × ~400 Ft | – |

**Elektronika összesen: ~35.000 Ft**

---

### 2. 3D nyomtatás

| Modell | Anyag | Nyomtatási idő (kb.) | Megjegyzés |
|--------|-------|----------------------|------------|
| Raktárpolc szekció (×12) | PLA, szürke | 12 × 2 ó = 24 ó | 15×10×8 cm, 3 szint |
| Raklap modell (×20) | PLA, barna | 20 × 30 perc = 10 ó | 4×4×1.5 cm, RFID tartóval |
| Targonca modell (×2) | PLA, sárga | 2 × 3 ó = 6 ó | Dekoratív |
| Zóna tábla (×6) | PLA, fehér | 6 × 20 perc = 2 ó | Lézereszhető |
| Olvasó burkolat (×6) | PLA, fekete | 6 × 1 ó = 6 ó | MFRC522 + ESP32 doboz |
| Alaplap (1 db) | MDF vagy PLA | – | 60×40 cm alap |

**Nyomtatási anyag összesen: ~3.000 Ft PLA filament**

**Ajánlott 3D nyomtató**: Bambu Lab A1 Mini, Prusa Mini+, Ender 3 V2

---

### 3. Egyéb anyagok

| Anyag | Mennyiség | Ár |
|-------|-----------|----|
| Szalagkábel AWG 28 | 2 m | ~500 Ft |
| Kétoldalas ragasztószalag | 1 csomag | ~500 Ft |
| Forró ragasztó pisztolyhoz | 1 csomag | ~400 Ft |
| M3 csavar+anya készlet | 50 db | ~600 Ft |

---

## Összesített költség

| Kategória | Összeg |
|-----------|--------|
| Elektronika | ~35.000 Ft |
| 3D nyomtatás + anyag | ~5.000 Ft |
| Egyéb | ~2.000 Ft |
| **Összesen** | **~42.000 Ft (~105 EUR)** |

---

## Bekötési ábra – ESP32 + MFRC522

```
ESP32 DevKit                    MFRC522
┌──────────────┐               ┌──────────────┐
│  GPIO 5 ─────┼───────────────┤ SDA (SS)     │
│  GPIO 18 ────┼───────────────┤ SCK          │
│  GPIO 23 ────┼───────────────┤ MOSI         │
│  GPIO 19 ────┼───────────────┤ MISO         │
│  GPIO 27 ────┼───────────────┤ RST          │
│  3.3V ───────┼───────────────┤ 3.3V         │
│  GND ────────┼───────────────┤ GND          │
│              │               └──────────────┘
│  GPIO 2 ─┬──┤  LED ZÖLD (220Ω ellenállással)
│  GPIO 4 ─┬──┤  LED PIROS (220Ω ellenállással)
│  GPIO 15 ─┬─┤  Buzzer (opcionális)
└──────────────┘
```

---

## Raspberry Pi + PN532 bekötés (I2C)

```
Raspberry Pi            PN532
┌────────────┐         ┌──────────────┐
│ 3.3V (1)───┼─────────┤ VCC          │
│ GND  (6)───┼─────────┤ GND          │
│ SDA  (3)───┼─────────┤ SDA          │  ← I2C mód
│ SCL  (5)───┼─────────┤ SCL          │
│ GPIO24(18)─┼─────────┤ IRQ          │  opcionális
│ GPIO17(11)─┤  LED ZÖLD              │
│ GPIO27(13)─┤  LED PIROS             │
└────────────┘         └──────────────┘

FONTOS: PN532-n a SEL jumpereket I2C módba kell állítani:
  SEL1 = OFF (0)
  SEL2 = ON  (1)
```

---

## Szoftver telepítés ESP32-re

1. **Arduino IDE** letöltése: arduino.cc/en/software
2. **ESP32 board csomag** hozzáadása:
   - File → Preferences → Additional board URLs:
     `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board Manager → "esp32" telepítése
3. **Könyvtárak** (Tools → Manage Libraries):
   - `MFRC522` by GithubCommunity
   - `ArduinoJson` by Benoit Blanchon
4. **Konfiguráció** szerkesztése: `hardware/esp32/config.h`
5. **Feltöltés**: Tools → Board: ESP32 Dev Module → Port: COMx → Upload

---

## Szoftver telepítés Raspberry Pi-re

```bash
# 1. Fájlok másolása RPi-re
scp -r hardware/raspberry_pi/ pi@192.168.x.x:/home/pi/rfid/

# 2. SSH belépés
ssh pi@192.168.x.x

# 3. I2C engedélyezése
sudo raspi-config → Interfacing Options → I2C → Enable

# 4. Telepítés
cd /home/pi/rfid
chmod +x install.sh && ./install.sh

# 5. Indítás
sudo systemctl start rfid-reader
sudo systemctl status rfid-reader

# 6. Log figyelése
journalctl -u rfid-reader -f
```

---

## Factory I/O integráció

A **Factory I/O** (realsimlab.com) egy professzionális 3D gyárszimulációs szoftver
amely PLCkkel és Modbus-szal kommunikál. Az RFID rendszerünkkel az alábbi módon
integrálható:

### Amit a Factory I/O tud szimulálni:
- Futószalagok (conveyor belts)
- RFID olvasók (beépített RFID sensor)
- Kapuk, lift-ek, targoncák
- Szenzorok (fotoelektromos, ütközési)

### Integráció lépései:
1. Factory I/O-ban hozzáadd az RFID Scanner sensort a szalaghoz
2. A Factory I/O Driver SDK-val (C#/.NET) olvasd ki a RFID eseményt
3. A C# bridge HTTP POST-ot küld a mi `/api/rfid/event` végpontunkra
4. Vagy: Factory I/O → Modbus TCP → Python Modbus kliens → HTTP POST

### Factory I/O Modbus bridge (Python):
```python
# pip install pymodbus requests
from pymodbus.client import ModbusTcpClient
import requests, time

client = ModbusTcpClient('127.0.0.1', port=502)  # Factory I/O Modbus szerver
while True:
    result = client.read_holding_registers(0, 10)
    if result.registers[0] != 0:  # RFID olvasva
        tag_id = result.registers[0]
        requests.post('http://localhost:8000/api/rfid/event', json={
            "reader_id": "FACTORYIO-01",
            "tag_epc": f"FIO-{tag_id:08X}",
            "zone": "GYÁRTÁS",
            "event_type": "read"
        })
    time.sleep(0.1)
```

### Factory I/O ingyenes verzió:
- 30 napos trial teljes funkcionalitással
- Student license: ~€35/év
- Professional: ~€1.000

---

## Javasolt szimuláció sorrendek

### 1. szint – Ma, software szimulátorral (0 Ft)
```
python simulator/main.py  →  http://localhost:8001
```
Drag & drop raklapok a virtuális raktárban, demo mód, élő esemény küldés.

### 2. szint – Olcsó fizikai (1 hét, ~42.000 Ft)
3D nyomtatott modell + ESP32 + MFRC522 + RFID kártyák

### 3. szint – Factory I/O (2 hét, +~15.000 Ft)
Professzionális 3D szimuláció futószalagokkal, RFID sensorokkal

### 4. szint – Valódi ATR7000 (~3-6 hónap, több millió Ft)
Éles raktári telepítés Zebra ATR7000 olvasókkal
