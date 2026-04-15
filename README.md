# remote-gpu-monitor

Remote Hardware Monitor and Mining Control
Este proyecto consiste en un ecosistema de monitoreo remoto diseñado para gestionar y supervisar el estado de una estacion de minado de criptomonedas (Nexa, Ergo o Kaspa) en tiempo real. Permite visualizar metricas criticas de hardware como temperaturas de nucleo y hotspot, velocidad de ventiladores y consumo energetico, ademas de ejecutar acciones remotas de control.

Vista General
El sistema se divide en dos componentes principales que se comunican de forma segura:

Backend (Python y FastAPI): Un servidor local que extrae datos directamente de los sensores de la GPU utilizando la libreria de bajo nivel de NVIDIA (pynvml).

Mobile App (Flutter): Una interfaz movil que consume la API para mostrar tableros visuales y permitir el control remoto, incluyendo funciones de apagado, suspension y reseteo de registros.

Tecnologias Utilizadas
Backend: Python 3.x, FastAPI, psutil para metricas de sistema y nvidia-ml-py (pynvml).

Mobile: Flutter, Dart y cliente HTTP.

Seguridad: Implementacion de Middleware para validacion de claves de API (x-api-key) en cada peticion.

Caracteristicas Tecnicas
Monitoreo Preciso: Lectura de temperatura de Hotspot, fundamental para la integridad de componentes de alto rendimiento como la GPU MSI Ventus RTX 5060 Ti.

Control de Energia: Funciones para realizar shutdown o suspend del equipo de forma remota mediante llamadas al sistema operativo.

Gestion de Ventiladores: Capacidad de alternar entre modo automatico y manual, ajustando la velocidad segun la necesidad termica del algoritmo de minado.

Mineria Inteligente: Incluye un script secundario (minero-stop.py) que monitorea el hashrate de la API de lolMiner y emite alertas sonoras y visuales si la potencia de minado cae a 0 MH/s.

Estructura del Repositorio
/backend: Contiene el servidor FastAPI (main.py), el script de monitoreo de hashrate (minero-stop.py) y el archivo de dependencias (requirements.txt).

/mobile_app: Contiene la logica de la interfaz en Flutter (lib/main.dart) y la configuracion de dependencias (pubspec.yaml).

Seguridad y Despliegue
Por motivos de seguridad, las direcciones IP y las llaves de API han sido omitidas o reemplazadas por valores genericos en este repositorio. Para su despliegue, se requiere configurar las variables de entorno correspondientes segun el entorno de ejecucion.

Desarrollado por Mateo Angel Risso
Estudiante de cuarto año de la Licenciatura en Ciencias de Datos en la Universidad de Buenos Aires (UBA).
