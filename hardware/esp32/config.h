#pragma once

// ── WiFi beállítások ───────────────────────────────────────────────────────
#define WIFI_SSID   "RAKTAR-WIFI"        // WiFi hálózat neve
#define WIFI_PASS   "jelszo123"          // WiFi jelszó

// ── Szerver beállítások ───────────────────────────────────────────────────
// A raktárkezelő szoftver IP címe a helyi hálózaton
#define SERVER_URL  "http://192.168.1.100:8000"

// ── Olvasó azonosítók ─────────────────────────────────────────────────────
// Minden ESP32-nek egyedi Reader ID kell!
// Például: "FIZIKAI-A1", "FIZIKAI-BEVET", "FIZIKAI-KISZALL"
#define READER_ID   "FIZIKAI-A1"

// Az a raktári zóna ahol ez az olvasó fizikailag van
// Lehetséges értékek: BEVÉTELEZŐ, A-TÁROLÓ, B-TÁROLÓ, GYÁRTÁS, KOMISSIÓZÓ, KISZÁLLÍTÁS
#define ZONE        "A-TÁROLÓ"
