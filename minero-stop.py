import time
import requests
import ctypes
import winsound
import os

# Configuración
LOL_API = os.getenv("MINER_API_URL", "http://127.0.0.1:8020/summary")
CHECK_INTERVAL = 30  
START_DELAY = 120    

def show_message(title, text):
    # messageboxw para Windows
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0x1)



def beep_alert():
    winsound.Beep(1000, 1000)
    winsound.Beep(600, 500)

def get_hashrate():
    try:
        r = requests.get(LOL_API, timeout=5)
        data = r.json()
        hashrate = data["Algorithms"][0]["Total_Performance"]
        return float(hashrate)
    except Exception as e:
        print("Error leyendo API:", e)
        return 0.0

if __name__ == "__main__":
    print(f"Esperando {START_DELAY} segundos antes de comenzar el monitoreo...")
    time.sleep(START_DELAY)

    warned = False
    while True:
        hr = get_hashrate()
        print(f"Hashrate actual: {hr:.2f} Mh/s")

        if hr == 0.0:
            if not warned:
                show_message("⚠️ Minado detenido", "El minado está en 0 MH/s. Revisa lolMiner.")
                beep_alert()
                warned = True
        else:
            warned = False

        time.sleep(CHECK_INTERVAL)
