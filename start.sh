#!/bin/bash
set -e

echo "======================================================"
echo " RFID Raktár Nyomonkövető Rendszer"
echo "======================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "HIBA: Python 3 nem található!"
    exit 1
fi

# Create virtual env if not exists
if [ ! -d "venv" ]; then
    echo "[1/3] Virtuális környezet létrehozása..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "[2/3] Függőségek telepítése..."
pip install -q -r requirements.txt

# Start app
echo "[3/3] Szerver indítása..."
echo ""
echo "  Az alkalmazás elérhető: http://localhost:8000"
echo "  API dokumentáció:       http://localhost:8000/docs"
echo "  Leállítás: Ctrl+C"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
