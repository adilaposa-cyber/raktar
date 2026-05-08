@echo off
title RFID Raktár – Indítás
echo ============================================================
echo   RFID Raktár Nyomonkövető Rendszer – Indítás
echo ============================================================

if not exist venv (
    echo Virtualis kornyezet letrehozasa...
    python -m venv venv
)

echo Fuggsegek telepitese...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo Foalkalmazas indul  : http://localhost:8000
echo Szimulator indul    : http://localhost:8001
echo.

start "RFID Foalkalmazas [:8000]" cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak > nul
start "RFID Szimulator [:8001]" cmd /k "call venv\Scripts\activate.bat && uvicorn simulator.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 2 /nobreak > nul

start http://localhost:8000/szerelde
echo Kesz! A bongeszo automatikusan megnyilt.
pause
