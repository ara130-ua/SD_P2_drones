import socket
import threading
import sys
import sqlite3
import datetime

import numpy as np
import matplotlib.pyplot as plt

#def consulta_Clima():
    
HEADER = 64
FORMAT = 'utf-8'

# Manejo de ficheros
def file_manipulation(name, mode):
  try:
    file = open(name, mode)
    return file
  except OSError as err:
    print("Error: {0}".format(err))
  return

def manejoFichero(maxDrones):
   
    fileWrite = 'figura.txt'
    datos_drones = []

   # Una manera de sacar el contenido en una string
   #f = file_manipulation(fileWrite, 'r')
   #contenido = f.read()
   
   # sacamos la información en lineas de los drones
    with open(fileWrite, 'r') as archivo:
        lineas = archivo.readlines()

    for linea in lineas:
      #Eliminamos espacios en blanco
        linea = linea.strip()
        if linea:
            elementos = linea.split('-')

            if len(elementos) == 3:
                datos_drones.append((int(elementos[0]), (int(elementos[1]), int(elementos[2]))))            

   # cerramos el fichero
    print(datos_drones)
    return(datos_drones)

def manejoMapa(mapaBytes):
    strMapa = ""

    for fila in mapaBytes:
      strMapa = strMapa + "| "
      for elemento in fila:
         strMapa = strMapa + "[" + "E," + str(elemento) + "] "
      strMapa = strMapa + "|\n"
   
    print(strMapa)

    return(strMapa)


####main#####
print ("Bienvenido al AD_Engine")


#usaremos 6 argumentos, la BBDD no necesita de conexion
# Puerto de escucha del engine
# número máximo de drones
# IP y puerto del Broker
# IP y puerto del AD_Wheather
if  (len(sys.argv) == 7):
    PORT = int(sys.argv[1])
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER,PORT)

    manejoFichero(int(sys.argv[2]))

    mapaBytes = [[0 for _ in range(20)] for _ in range(20)]

    strMapa = manejoMapa(mapaBytes)

    IP_BROKER = sys.argv[3]
    PORT_BROKER = int(sys.argv[4])

    ADDR_BROKER = (IP_BROKER, PORT_BROKER)

    IP_WEATHER= sys.argv[5]
    PORT_WEATHER= int(sys.argv[6])
    
    ADDR_WEATHER = (IP_WEATHER, PORT_WEATHER)
    
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto> <Max_Drones> <IP_Broker> <Puerto_Broker> <IP_Weather> <Puerto_Weather>")
