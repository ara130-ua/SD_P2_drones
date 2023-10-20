import socket
import threading
import sys
import sqlite3
import datetime
import time
from kafka import KafkaProducer
from json import dumps
from kafka import KafkaConsumer


#def consulta_Clima():
    
HEADER = 64
FORMAT = 'utf-8'
PORT = 5050

def manejoClima(ipClima, puertoClima):
    # conexion con AD_Weather mediante socket
    ADDR_WEATHER = (ipClima, puertoClima)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR_WEATHER)
    server.listen()
    print(f"AD_Engine escuchando en  {ADDR_WEATHER}")



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

def mandar_mapa(mapa):
    producer = KafkaProducer(
    value_serializer=lambda m: dumps(m).encode('utf-8'),
    bootstrap_servers=['localhost:9092'])

    producer.send("drones-topic", value=mapa)


####main#####
print ("Bienvenido al AD_Engine")


#usaremos 5 argumentos, la BBDD no necesita de conexion
# número máximo de drones
# IP y puerto del Broker
# IP y puerto del AD_Wheather
if  (len(sys.argv) == 6):
    
    # zona de argumentos

    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER,PORT)

    IP_BROKER = sys.argv[3]
    PORT_BROKER = int(sys.argv[4])

    ADDR_BROKER = (IP_BROKER, PORT_BROKER)

    # zona de funciones

    manejoFichero(int(sys.argv[2]))

    mapaBytes = [[0 for _ in range(20)] for _ in range(20)]

    strMapa = manejoMapa(mapaBytes)

    # thread = threading.Thread(target=manejoClima, args=(sys.argv[5], int(sys.argv[6])))
    # thread.start()

    
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto> <Max_Drones> <IP_Broker> <Puerto_Broker> <IP_Weather> <Puerto_Weather>")
