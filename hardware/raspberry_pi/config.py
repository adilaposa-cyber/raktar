# ── Szerver beállítások ────────────────────────────────────────────────────
# A raktárkezelő szoftver IP:port a helyi hálózaton
SERVER_URL = "http://192.168.1.100:8000"

# ── Olvasó azonosítók ──────────────────────────────────────────────────────
READER_ID = "FIZIKAI-RPi-A1"   # Egyedi azonosító minden RPi-nek
ZONE      = "A-TÁROLÓ"         # Melyik raktári zónában van ez az olvasó

# ── GPIO pin számok (BCM számozás) ─────────────────────────────────────────
LED_GREEN_PIN = 17   # Zöld LED – sikeres olvasás
LED_RED_PIN   = 27   # Piros LED – hiba / nem küldött
