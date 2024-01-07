import subprocess
import time

#ejecutar en terminal del sistema


bbdd = "gnome-terminal -- bash -c 'rm bd1.db && python BBDD.py && exit; exec bash '"
kafka = "gnome-terminal -- bash -c 'python launcher_kafka.py; exec bash '"
API_inEngine = "gnome-terminal -- bash -c 'uvicorn AD_Engine:app --reload --host 127.0.0.1 --port 8001 --ssl-keyfile clave-privada.key --ssl-certfile certificado-firmado.crt; exec bash '"
API_Engine = "gnome-terminal -- bash -c 'uvicorn AD_Engine:app --reload --host 127.0.0.1 --port 8002 '"
API_Registry = "gnome-terminal -- bash -c 'uvicorn AD_Registry:app --reload --host 127.0.0.1 --port 8000 --ssl-keyfile private-key2.pem --ssl-certfile certificate2.crt; exec bash '"
engine = "gnome-terminal -- bash -c 'python AD_Engine.py 8050 4 localhost 9092 localhost 7050 ; exec bash '"
registry = "gnome-terminal -- bash -c 'python AD_Registry.py 6050; exec bash '"
weather = "gnome-terminal -- bash -c 'python AD_Wheather.py 7050; exec bash '"

# Lanzamos dron
drones = "gnome-terminal -- bash -c 'python launcher_drones.py; exec bash '"


# Ejecutar los comandos en terminales separadas
subprocess.run(bbdd, shell=True)
time.sleep(2)
subprocess.run(kafka, shell=True)
time.sleep(2)
subprocess.run(API_inEngine, shell=True)
subprocess.run(API_Registry, shell=True)
subprocess.run(API_Engine, shell=True)
subprocess.run(engine, shell=True)
time.sleep(2)
subprocess.run(registry, shell=True)
time.sleep(2)


print("Pulse enter para lanzar los drones")
input()

subprocess.run(drones, shell=True)
time.sleep(2)


