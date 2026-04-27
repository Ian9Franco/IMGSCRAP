import webview
import time
import urllib.request
import subprocess
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

processes = []

# En Windows, oculto las molestas ventanas negras de la consola para que no me molesten.
CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

def start_servers():
    print("Iniciando backend (FastAPI)...")
    p_backend = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=BACKEND_DIR,
        creationflags=CREATION_FLAGS
    )
    processes.append(p_backend)

    print("Iniciando frontend (Next.js)...")
    p_frontend = subprocess.Popen(
        "npm run dev",
        cwd=FRONTEND_DIR,
        shell=True,
        creationflags=CREATION_FLAGS
    )
    processes.append(p_frontend)

def kill_servers():
    print("\nCerrando Scrap.io...")
    for p in processes:
        try:
            subprocess.run(
                f"taskkill /F /T /PID {p.pid}",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"Error cerrando proceso {p.pid}: {e}")

def check_server(timeout=180):
    print(f"Esperando Next.js en puerto 3000...")
    for _ in range(timeout):
        try:
            urllib.request.urlopen("http://localhost:3000", timeout=2)
            print("¡Scrap.io esta lista!")
            return True
        except:
            time.sleep(1)
    return False

if __name__ == '__main__':
    try:
        start_servers()
        if check_server():
            window = webview.create_window(
                title='Scrap.io',
                url='http://localhost:3000',
                width=1280,
                height=820,
                min_size=(960, 600),
                background_color='#0f172a'
            )
            window.events.closed += kill_servers
            webview.start()
        else:
            print("Error: Next.js no respondió a tiempo.")
            kill_servers()
    except KeyboardInterrupt:
        kill_servers()
