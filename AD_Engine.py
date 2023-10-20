import socket
import threading
import sys
import sqlite3
import datetime

#def consulta_Clima():
    
HEADER = 64
FORMAT = 'utf-8'
PORT = 5050

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
            elementos = linea.split()

            if len(elementos) == 3:
                datos_drones.append((int(elementos[0]), float(elementos[1]), float(elementos[2])))            

   # cerramos el fichero
    return(datos_drones)


####main#####
print ("Bienvenido al AD_Engine")


#usaremos 6 argumentos, la BBDD no necesita de conexion
# Puerto de escucha del engine
# número máximo de drones
# IP y puerto del Broker
# IP y puerto del AD_Wheather
if  (len(sys.argv) == 7):
    PORT = int(sys.argv[1])
    SERVER = socket.gethostbyname(socket.gethostbyname())
    ADDR = (SERVER,PORT)

    manejoFichero(MAX_DRONES = int(sys.argv[2]))

    IP_BROKER = sys.argv[3]
    PORT_BROKER = int(sys.argv[4])

    ADDR_BROKER = (IP_BROKER, PORT_BROKER)

    IP_WEATHER= sys.argv[5]
    PORT_WEATHER= int(sys.argv[6])
    
    ADDR_WEATHER = (IP_WEATHER, PORT_WEATHER)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print (f"Establecida conexión en [{ADDR}]")

    msg=sys.argv[3]
    while msg != FIN :
        print("Envio al servidor: ", msg)
        send(msg)
        print("Recibo del Servidor: ", client.recv(2048).decode(FORMAT))
        msg=input()

    print ("SE ACABO LO QUE SE DABA")
    print("Envio al servidor: ", FIN)
    send(FIN)
    client.close()
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto> <Max_Drones> <IP_Broker> <Puerto_Broker> <IP_Weather> <Puerto_Weather>")
