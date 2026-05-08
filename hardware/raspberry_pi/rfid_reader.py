#!/usr/bin/env python3
"""
RFID Reader – Raspberry Pi + PN532 (I2C)
-----------------------------------------
Hardware: Raspberry Pi Zero 2W / RPi 3/4 + PN532 NFC/RFID modul

Bekötés (I2C mód):
  PN532 VCC  → 3.3V (Pin 1)
  PN532 GND  → GND  (Pin 6)
  PN532 SDA  → GPIO 2 (Pin 3)
  PN532 SCL  → GPIO 3 (Pin 5)
  PN532 IRQ  → GPIO 24 (Pin 18)  [opcionális]

Telepítés:
  pip install adafruit-circuitpython-pn532 requests RPi.GPIO

Konfiguráció: config.py fájlban
"""
import time
import logging
import requests
from datetime import datetime
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

# Debounce beállítás
DEBOUNCE_SECONDS = 3
last_uid: bytes = None
last_read_time: float = 0

# LED GPIO (opcionális – RPi GPIO pin)
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.LED_GREEN_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(config.LED_RED_PIN, GPIO.OUT, initial=GPIO.LOW)
    HAS_GPIO = True
except Exception:
    HAS_GPIO = False
    log.warning("GPIO nem elérhető – LED visszajelzés kikapcsolva")


def uid_to_epc(uid: bytes) -> str:
    """Byte array → HEX string EPC formátumba."""
    return uid.hex().upper()


def send_rfid_event(epc: str) -> bool:
    """HTTP POST az RFID eseményt a raktárkezelő szervernek."""
    payload = {
        "reader_id": config.READER_ID,
        "tag_epc": epc,
        "rssi": -65.0,
        "zone": config.ZONE,
        "event_type": "read",
    }
    url = f"{config.SERVER_URL}/api/rfid/event"
    try:
        resp = requests.post(url, json=payload, timeout=3)
        ok = resp.status_code == 200
        log.info(f"POST {url} → {resp.status_code} ({'OK' if ok else 'HIBA'})")
        return ok
    except requests.exceptions.ConnectionError:
        log.error(f"Szerver nem elérhető: {url}")
        return False
    except Exception as e:
        log.error(f"HTTP hiba: {e}")
        return False


def led_feedback(success: bool):
    if not HAS_GPIO:
        return
    if success:
        GPIO.output(config.LED_GREEN_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(config.LED_GREEN_PIN, GPIO.LOW)
    else:
        for _ in range(3):
            GPIO.output(config.LED_RED_PIN, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(config.LED_RED_PIN, GPIO.LOW)
            time.sleep(0.1)


def main():
    global last_uid, last_read_time

    log.info("=== RFID Reader induló ===")
    log.info(f"Olvasó ID: {config.READER_ID} | Zóna: {config.ZONE}")
    log.info(f"Szerver: {config.SERVER_URL}")

    # PN532 inicializálás
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)

    ic, ver, rev, support = pn532.firmware_version
    log.info(f"PN532 firmware: {ver}.{rev}")
    pn532.SAM_configuration()

    log.info("Várakozás RFID tagre...")

    while True:
        try:
            uid = pn532.read_passive_target(timeout=0.5)
            if uid is None:
                continue

            now = time.time()
            epc = uid_to_epc(uid)

            # Debounce – ugyanazt a tagot ne küldjük túl sűrűn
            if uid == last_uid and (now - last_read_time) < DEBOUNCE_SECONDS:
                continue

            last_uid = uid
            last_read_time = now

            log.info(f"Tag olvasva: {epc}")
            ok = send_rfid_event(epc)
            led_feedback(ok)

        except KeyboardInterrupt:
            log.info("Leállítás...")
            break
        except Exception as e:
            log.error(f"Olvasási hiba: {e}")
            time.sleep(1)

    if HAS_GPIO:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
