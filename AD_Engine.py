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
SERVER = socket.gethostbyname(socket.gethostname())
ADDR_ENGINE = (SERVER, PORT)

#----------------------------------------------------------#

### Funciones de servidor ###

def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    print("Enviando mensaje: ", message)
    client.send(message)

def receive(client):
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        print(f"Se ha recibido del servidor: {msg}")
        return msg
    else:
        print("No se ha recibido nada del servidor")
        return None
    
### Funciones de servidor ###

#----------------------------------------------------------#

### Funciones de BBDD ###

# posible solución para la BBDD
# siempre eliminar la fila de la tabla weather
# y crear una nueva con los datos actualizados

def climaBBDD(datos_clima):
    # datos_clima es un string que contiene los datos de clima
    # revisar por si hay que convertirla en tupla
    tuplaClima = eval(datos_clima)
    nombreCiudad = tuplaClima[0]
    temperatura = tuplaClima[1]
    conexion = sqlite3.connect("bd1.db")

    #try:
        # comprobar los tipos de datos de nombre y de temperatura
    conexion.execute("insert into weather(nombre, temperatura) values ('"+nombreCiudad+"',"+str(temperatura)+")")
    conexion.commit()
    return("ciudad añadida a la BBDD")
    #except sqlite3.OperationalError:
    #    print("Error al añadir la ciudad a la BBDD")
    #    conexion.close()
    #    return "Error", "Base de datos"

### Funciones de BBDD ###

#----------------------------------------------------------#

### Funciones que manejan la conexion con el AD_Wheather ###

def conexionClima(ipClima, puertoClima):
    ADDR = (str(ipClima), int(puertoClima))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Se ha establecido conexión en [{ADDR}]")
    thread = threading.Thread(target=manejoClima, args=(client, ADDR))
    thread.start()


def manejoClima(conn, addr):
    conectado = True
    while conectado:
        send("Petición de clima", conn)
        # para compartir la información entre los hilos
        # habrá que guardar los datos en la BBDD
        datos_clima = receive(conn)
        print(f"Se ha recibido del AD_Weather {addr} los datos de clima: {datos_clima}")
        # guardar en la BBDD
        print(climaBBDD(datos_clima))

### Funciones que manejan la conexion con el AD_Wheather ###

#----------------------------------------------------------#

### Funciones que manejan el fichero de drones y el mapa ###

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


### Funciones que manejan el fichero de drones y el mapa ###

#----------------------------------------------------------#

####main#####
print ("Bienvenido al AD_Engine")


#usaremos 5 argumentos, la BBDD no necesita de conexion
# número máximo de drones
# puerto del AD_Engine
# IP y puerto del Broker
# IP y puerto del AD_Wheather
if  (len(sys.argv) == 6):
    
    # zona de argumentos

    IP_BROKER = sys.argv[3]
    PORT_BROKER = int(sys.argv[4])

    ADDR_BROKER = (IP_BROKER, PORT_BROKER)



    # zona de funciones

    manejoFichero(int(sys.argv[2]))

    mapaBytes = [[0 for _ in range(20)] for _ in range(20)]

    strMapa = manejoMapa(mapaBytes)

    IP_WEATHER = socket.gethostbyname(socket.gethostname())

    conexionClima(IP_WEATHER, sys.argv[5])

    
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Max_Drones> <IP_Broker> <Puerto_Broker> <IP_Weather> <Puerto_Weather>")
