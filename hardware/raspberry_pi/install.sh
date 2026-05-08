#!/bin/bash
# Raspberry Pi RFID olvasó telepítő script
set -e
echo "=== RFID Reader telepítése (Raspberry Pi) ==="

# I2C engedélyezése ha nincs
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
  echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
  echo "I2C engedélyezve – újraindítás szükséges!"
fi

# Python csomagok
pip3 install -r requirements.txt

# Automatikus indítás (systemd service)
sudo tee /etc/systemd/system/rfid-reader.service << 'EOF'
[Unit]
Description=RFID Reader – Raktár
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rfid
ExecStart=/usr/bin/python3 /home/pi/rfid/rfid_reader.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable rfid-reader
echo "Service telepítve: sudo systemctl start rfid-reader"
