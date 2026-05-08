/**
 * RFID Reader – ESP32 + MFRC522
 * --------------------------------
 * Hardware: ESP32-WROOM-32 + MFRC522 RFID olvasó
 *
 * Bekötés:
 *   MFRC522   →  ESP32
 *   SDA       →  GPIO 5  (SS)
 *   SCK       →  GPIO 18
 *   MOSI      →  GPIO 23
 *   MISO      →  GPIO 19
 *   RST       →  GPIO 27
 *   3.3V      →  3.3V
 *   GND       →  GND
 *
 * Függőségek (Arduino Library Manager):
 *   - MFRC522 by GithubCommunity
 *   - ArduinoJson by Benoit Blanchon
 *   - HTTPClient (beépített ESP32)
 *
 * Konfiguráció: config.h fájlban
 */

#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

// RFID pins
#define SS_PIN   5
#define RST_PIN  27

MFRC522 rfid(SS_PIN, RST_PIN);

// LED státusz indikátorok
#define LED_WIFI   2   // Kék LED – WiFi kapcsolat
#define LED_READ  15   // Zöld LED – sikeres olvasás
#define LED_ERR   4    // Piros LED – hiba

// Debounce – ugyanaz a tag ne legyen beküldve X ms-on belül újra
#define DEBOUNCE_MS 3000
String lastEPC = "";
unsigned long lastReadMs = 0;

// ── Setup ──────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println("\n=== RFID Reader induló ===");

  pinMode(LED_WIFI, OUTPUT);
  pinMode(LED_READ, OUTPUT);
  pinMode(LED_ERR, OUTPUT);

  // SPI és RFID init
  SPI.begin();
  rfid.PCD_Init();
  rfid.PCD_DumpVersionToSerial();
  Serial.println("MFRC522 inicializálva");

  // WiFi csatlakozás
  connectWiFi();
}

// ── Loop ───────────────────────────────────────────────────────────────────
void loop() {
  // WiFi reconnect ha szükséges
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_WIFI, LOW);
    connectWiFi();
  }

  // RFID olvasás
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  String epc = getEPC();
  unsigned long now = millis();

  // Debounce – ne küldjük ugyanazt a tagot túl sűrűn
  if (epc == lastEPC && (now - lastReadMs) < DEBOUNCE_MS) {
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    return;
  }
  lastEPC = epc;
  lastReadMs = now;

  Serial.printf("Tag olvasva: %s\n", epc.c_str());

  // HTTP POST küldés
  bool ok = sendRFIDEvent(epc);

  // LED visszajelzés
  if (ok) {
    digitalWrite(LED_READ, HIGH);
    delay(200);
    digitalWrite(LED_READ, LOW);
  } else {
    // Hibajelzés – 3x villog
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_ERR, HIGH); delay(100);
      digitalWrite(LED_ERR, LOW);  delay(100);
    }
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

// ── EPC olvasás (hex string) ───────────────────────────────────────────────
String getEPC() {
  String result = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) result += "0";
    result += String(rfid.uid.uidByte[i], HEX);
  }
  result.toUpperCase();
  return result;
}

// ── HTTP POST RFID esemény ─────────────────────────────────────────────────
bool sendRFIDEvent(String epc) {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  String url = String(SERVER_URL) + "/api/rfid/event";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(3000);

  // JSON payload összeállítása
  StaticJsonDocument<256> doc;
  doc["reader_id"]  = READER_ID;
  doc["tag_epc"]    = epc;
  doc["rssi"]       = -65.0;  // MFRC522 nem tud RSSI-t, fix értéket küldünk
  doc["zone"]       = ZONE;
  doc["event_type"] = "read";

  String payload;
  serializeJson(doc, payload);

  Serial.printf("POST %s: %s\n", url.c_str(), payload.c_str());

  int code = http.POST(payload);
  bool ok = (code == 200);
  Serial.printf("Válasz: %d\n", code);
  http.end();
  return ok;
}

// ── WiFi csatlakozás ───────────────────────────────────────────────────────
void connectWiFi() {
  Serial.printf("WiFi csatlakozás: %s\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 20) {
    delay(500);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(LED_WIFI, HIGH);
    Serial.printf("\nWiFi OK – IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\nWiFi HIBA – újrapróbálkozás 10 mp-ben");
    delay(10000);
  }
}
