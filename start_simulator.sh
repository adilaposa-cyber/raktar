#!/bin/bash
set -e
echo "======================================================"
echo " RFID Szimulátor (ATR7000 szoftver helyettesítő)"
echo "======================================================"

# Check Python
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo ""
echo "  Szimulátor UI:   http://localhost:8001"
echo "  Főalkalmazás:    http://localhost:8000"
echo ""
echo "  FONTOS: A főalkalmazás is fusson párhuzamosan!"
echo "  Nyiss egy másik terminált és futtasd: ./start.sh"
echo ""

uvicorn simulator.main:app --host 0.0.0.0 --port 8001 --reload
