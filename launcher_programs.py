import subprocess
import time

#ejecutar en terminal del sistema

bbddRemove = "gnome-terminal -- bash -c 'rm bd1.db; exec bash '"
bbdd = "gnome-terminal -- bash -c 'python BBDD.py; exec bash '"
kafka = "gnome-terminal -- bash -c 'python launcher_kafka.py; exec bash '"
engine = "gnome-terminal -- bash -c 'python ADs/AD_Engine.py 8050 4 localhost 9092 localhost 7050 ; exec bash '"
registry = "gnome-terminal -- bash -c 'python ADs/AD_Registry.py 6050; exec bash '"
weather = "gnome-terminal -- bash -c 'python ADs/AD_Wheather.py 7050; exec bash '"

# Lanzamos dron
drones = "gnome-terminal -- bash -c 'python launcher_drones.py; exec bash '"


# Ejecutar los comandos en terminales separadas
subprocess.run(bbddRemove, shell=True)
subprocess.run(bbdd, shell=True)
time.sleep(2)
subprocess.run(kafka, shell=True)
time.sleep(2)
subprocess.run(engine, shell=True)
time.sleep(2)
subprocess.run(registry, shell=True)
time.sleep(2)
subprocess.run(weather, shell=True)
time.sleep(2)

print("Pulse enter para lanzar los drones")
input()

subprocess.run(drones, shell=True)
time.sleep(2)


