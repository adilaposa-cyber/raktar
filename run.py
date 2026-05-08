"""
Egy gombos indító – elindítja a főalkalmazást ÉS a szimulátort.
Használat: python run.py
"""
import subprocess
import sys
import os
import time
import signal
import threading

BASE = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE, "venv", "Scripts" if sys.platform == "win32" else "bin", "python")
PYTHON = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable

procs = []

def stream(proc, prefix, color):
    code = {"red": "\033[91m", "cyan": "\033[96m", "reset": "\033[0m"}
    c, r = code.get(color, ""), code["reset"]
    for line in iter(proc.stdout.readline, b""):
        print(f"{c}[{prefix}]{r} {line.decode('utf-8', errors='replace').rstrip()}")

def stop_all(sig=None, frame=None):
    print("\n\033[93mLeállítás...\033[0m")
    for p in procs:
        try:
            p.terminate()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, stop_all)
signal.signal(signal.SIGTERM, stop_all)

def install_deps():
    req = os.path.join(BASE, "requirements.txt")
    if os.path.exists(req):
        subprocess.run([PYTHON, "-m", "pip", "install", "-q", "-r", req], check=True)

print("\033[96m" + "=" * 60)
print("   RFID Raktár Nyomonkövető – Indítás")
print("=" * 60 + "\033[0m")
print("Függőségek ellenőrzése...")
install_deps()

print("\n\033[92mFőalkalmazás indul  → http://localhost:8000\033[0m")
print("\033[96mSzimulátor indul    → http://localhost:8001\033[0m")
print("\033[93mLeállítás: Ctrl+C\033[0m\n")

main_proc = subprocess.Popen(
    [PYTHON, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=BASE,
)
procs.append(main_proc)
time.sleep(2)

sim_proc = subprocess.Popen(
    [PYTHON, "-m", "uvicorn", "simulator.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=BASE,
)
procs.append(sim_proc)

t1 = threading.Thread(target=stream, args=(main_proc, "RAKTAR  ", "cyan"),  daemon=True)
t2 = threading.Thread(target=stream, args=(sim_proc,  "SZIMULÁTOR", "red"), daemon=True)
t1.start()
t2.start()

main_proc.wait()
stop_all()
