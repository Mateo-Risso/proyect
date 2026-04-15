import psutil
from pynvml import *
import os
import subprocess
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader


API_KEY_MATEO = os.getenv("MY_RIG_API_KEY", "TU_CLAVE_TEMPORAL_AQUI")

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

app = FastAPI(
    title="Remote PC Monitor API",
    description="API para monitoreo de hardware y control remoto de minería",
    version="1.0.0",
    swagger_ui_parameters={"syntaxHighlight": False},
    dependencies=[Depends(api_key_header)] 
)

@app.middleware("http")
async def validar_acceso_global(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json"]:
        return await call_next(request)
    
    token = request.headers.get("x-api-key")
    if token != API_KEY_MATEO:
        return JSONResponse(
            status_code=403, 
            content={"detail": "Acceso denegado. Se requiere x-api-key válida."}
        )
    
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# Inicializamos el acceso a la placa de video
nvmlInit()
conteo_de_dispositivos = nvmlDeviceGetCount()
gpu_data = []
nombres_vistos = {}

for i in range(conteo_de_dispositivos):
    handle = nvmlDeviceGetHandleByIndex(i)


    nombre_real = nvmlDeviceGetName(handle)

    if isinstance(nombre_real, bytes):
        nombre_real = nombre_real.decode('utf-8')
    
    if nombre_real not in nombres_vistos:
        nombres_vistos[nombre_real] = 1
        nombre_final = nombre_real
    else:
        nombres_vistos[nombre_real] += 1 
        nombre_final = f"{nombre_real} #{nombres_vistos[nombre_real]}"
    
    gpu_data.append({
        "handle" : handle,
        "nombre_app" : nombre_final
    })
records_gpu = {}
for gpu in gpu_data:
    records_gpu[gpu["nombre_app"]] = {
        "max_hotspot": 0,          # Empezamos en 0 para que cualquier temp la supere
        "min_hotspot": 100,        # Empezamos alto para que la primera lectura la baje
        "max_core": 0,
        "min_core" : 100
    }
cpu_records = {"max" : 0, "min" : 100}








@app.get("/status")
def get_rig_status():
   resultados_gpu = []
   cpu_actual = psutil.cpu_percent(interval=None)
   freq = psutil.cpu_freq()

   for gpu in gpu_data:
    a = gpu["handle"]
    nombre = gpu["nombre_app"]
    temp = nvmlDeviceGetTemperature(a, NVML_TEMPERATURE_GPU)
    fan = nvmlDeviceGetFanSpeed(a)

    if temp > records_gpu[nombre]["max_core"]:
                records_gpu[nombre]["max_core"] = temp
                
    if temp < records_gpu[nombre]["min_core"] and temp > 0:
                records_gpu[nombre]["min_core"] = temp

    try: 
        temp_hotspot = nvmlDeviceGetTemperature(a,1)
        if temp_hotspot > records_gpu[nombre]["max_hotspot"]:
                records_gpu[nombre]["max_hotspot"] = temp_hotspot
                
        if temp_hotspot < records_gpu[nombre]["min_hotspot"] and temp_hotspot > 0:
                records_gpu[nombre]["min_hotspot"] = temp_hotspot
        
        temp_hotspot_str = f"{temp_hotspot}°C"
        max_hotspot_str = f"{records_gpu[nombre]['max_hotspot']}°C"
        min_hotspot_str = f"{records_gpu[nombre]['min_hotspot']}°C"

        limit_shutdown = nvmlDeviceGetTemperatureThreshold(a, NVML_TEMPERATURE_THRESHOLD_SHUTDOWN)
        limit_throttling = nvmlDeviceGetTemperatureThreshold(a, NVML_TEMPERATURE_THRESHOLD_SLOWDOWN)
        limit_shutdown_str = f"{limit_shutdown}°C"
        limit_throttling_str = f"{limit_throttling}°C"
    except:
        temp_hotspot_str = "n/a"
        max_hotspot_str = "n/a"
        min_hotspot_str = "n/a"
        limit_shutdown_str = "n/a"
        limit_throttling_str = "n/a"

    power = nvmlDeviceGetPowerUsage(a) /1000
    resultados_gpu.append({
       "dispositivo" : gpu["nombre_app"],
       "core" : {
        "actual" : f"{temp}°C",
        "max" : f"{records_gpu[nombre]['max_core']}°C",
        "min" : f"{records_gpu[nombre]['min_core']}°C"
                                },
        "hotspot" : {
        "min" :  min_hotspot_str,
        "actual" : temp_hotspot_str ,
        "max" : max_hotspot_str,
        "limit_shutdown" : limit_shutdown_str,
        "limit_throttling" : limit_throttling_str
        },
       "fan speed" : f"{fan}%",
       "power": f"{power:.1f}W"
    })
    mem = psutil.virtual_memory() 
   return {
       "gpus" : resultados_gpu,
       "system" : {
        "cpu_usage" : f"{cpu_actual}%",
        "cpu_speed" : f"{freq.current:.0f} MHz",
        "ram_used" : f"{mem.percent}%",
        "total ram" : f"{mem.total/ (1024**3):.2f}GB"    
       },
       
       "status": "Online"
   }





@app.post("/reset-records")
def reset_records():
    for gpu in records_gpu:
        records_gpu[gpu] = {
            "max_hotspot": 0,
            "min_hotspot": 100,
            "max_core": 0,
            "min_core": 100
        }
    return {"status": "success", "message": "Récords reseteados correctamente."}




@app.post("/stop-process")
def stop_custom_process(process_name: str):
    try:
        # taskkill /F (fuerza) /T (árbol de procesos completo) /IM (nombre de imagen)
        # Esto cerrará el .exe y la ventana de consola que lo contiene
        resultado = subprocess.run(
            ["taskkill", "/F", "/T", "/IM", process_name], 
            capture_output=True, 
            text=True
        )
        
        if resultado.returncode == 0:
            return {"status": "success", "message": f"Proceso {process_name} y sus ventanas cerrados."}
        else:
            return {"status": "error", "message": "Proceso no encontrado."}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}




@app.post("/power/{action}")
def power_control(action: str):
    if action == "shutdown":
        # /s es apagar, /t 0 es tiempo inmediato
        os.system("shutdown /s /t 0")
        return {"message": "Apagando equipo..."}
    
    elif action == "suspend":
        # Comando para suspender en Windows
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return {"message": "Suspendiendo equipo..."}
    
    return {"error": "Acción no válida"}


@app.post("/fan-control")
def fan_control(mode: str, speed: int = 0):
    """
    mode: 'auto' o 'manual'
    speed: 0-100 (solo se usa si el modo es manual)
    """
    try:
        for gpu in gpu_data:
            handle = gpu["handle"]
            
            if mode.lower() == "auto":
                # Intentamos resetear al comportamiento por defecto del driver
                nvmlDeviceSetDefaultFanSpeed_v2(handle, 0) # 0 es el índice del ventilador
                return {"status": "success", "message": "Ventiladores vuelven a modo Automático."}
            
            elif mode.lower() == "manual":
                if not (0 <= speed <= 100):
                    raise HTTPException(status_code=400, detail="Velocidad manual debe ser entre 0 y 100")
                
                # Seteamos la velocidad fija
                nvmlDeviceSetFanSpeed_v2(handle, 1, speed)
                return {"status": "success", "message": f"Modo Manual: Ventiladores al {speed}%"}
            
            else:
                return {"status": "error", "message": "Modo no válido. Usar 'auto' o 'manual'."}
                
    except NVMLError as e:
        return {"status": "error", "message": f"Error de hardware (NVIDIA): {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
