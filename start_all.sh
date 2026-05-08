#!/bin/bash
set -e

echo "============================================================"
echo "  RFID Raktár Nyomonkövető Rendszer – Indítás"
echo "============================================================"

if [ ! -d "venv" ]; then
    echo "Virtuális környezet létrehozása..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo ""
echo "  Főalkalmazás → http://localhost:8000"
echo "  Szimulátor   → http://localhost:8001"
echo "  Leállítás: Ctrl+C"
echo ""

# Főalkalmazás háttérben
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
MAIN_PID=$!

sleep 2

# Szimulátor háttérben
uvicorn simulator.main:app --host 0.0.0.0 --port 8001 --reload &
SIM_PID=$!

# Böngésző megnyitása (ha elérhető)
sleep 2
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000/szerelde &
elif command -v open &> /dev/null; then
    open http://localhost:8000/szerelde &
fi

echo "Mindkét szerver fut. Ctrl+C a leállításhoz."

cleanup() {
    echo "Leállítás..."
    kill $MAIN_PID $SIM_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

wait $MAIN_PID
