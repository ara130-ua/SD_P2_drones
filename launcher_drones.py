import subprocess
import time

IP_ENGINE = "192.168.108.182"
PUERTO_ENGINE = 8050

IP_KAFKA = "192.168.108.182"
PUERTO_KAFKA = 9092

IP_REGISTRY = "192.168.108.182"
PUERTO_REGISTRY = 6050

ALIAS_DRON = ["Alfa", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]


for dron in ALIAS_DRON:
    comando_dron = "gnome-terminal -- bash -c 'python AD_Drone.py " +IP_ENGINE+ " " +str(PUERTO_ENGINE)+ " " +IP_KAFKA+ " " +str(PUERTO_KAFKA)+ " " +IP_REGISTRY+ " " +str(PUERTO_REGISTRY)+ " " +dron + "; exec bash '"
    subprocess.run(comando_dron, shell=True)
    time.sleep(1)
