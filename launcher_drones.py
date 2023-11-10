import subprocess
import time

IP_ENGINE = "172.20.10.9"
PUERTO_ENGINE = 8050

IP_KAFKA = "172.20.10.2"
PUERTO_KAFKA = 9092

IP_REGISTRY = "172.20.10.9"
PUERTO_REGISTRY = 6050

PUERTO_DRON = 5050

ALIAS_DRON = ["Alfa", "Bravo", "Charlie", "Delta"]


for dron in ALIAS_DRON:
    comando_dron = "gnome-terminal -- bash -c 'python3 AD_Drone.py " +IP_ENGINE+ " " +str(PUERTO_ENGINE)+ " " +IP_KAFKA+ " " +str(PUERTO_KAFKA)+ " " +IP_REGISTRY+ " " +str(PUERTO_REGISTRY)+ " " +str(PUERTO_DRON)+ " " +dron + "; exec bash '"
    subprocess.run(comando_dron, shell=True)
    time.sleep(1)
