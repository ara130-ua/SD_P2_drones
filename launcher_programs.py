import subprocess
import time

#ejecutar en terminal del sistema

# Creamos la BBDD
bbdd = "gnome-terminal -- bash -c 'python /home/joanclq/Documents/SD/SD_P2_drones/BBDD.py; exec bash '"

# Lanzamos el registry
registry = "gnome-terminal -- bash -c 'python /home/joanclq/Documents/SD/SD_P2_drones/AD_Registry.py; exec bash '"

# Lanzamos dron
drones = "gnome-terminal -- bash -c 'python /home/joanclq/Documents/SD/SD_P2_drones/AD_Drone.py; exec bash '"


subprocess.Popen(bbdd, shell=True)
time.sleep(2)
subprocess.Popen(registry, shell=True)
time.sleep(2)
subprocess.Popen(drones, shell=True)
