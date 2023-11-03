import socket
import threading
import sys
import sqlite3
import datetime
import time
import json
import os
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

    try:
        # comprobar los tipos de datos de nombre y de temperatura
        conexion.execute("insert into weather (nombre, temperatura) values ('"+nombreCiudad+"',"+str(temperatura)+")")
        conexion.commit()
        conexion.close()
        return("ciudad añadida a la BBDD")
    except sqlite3.OperationalError:
        print("Error al añadir la ciudad a la BBDD")
        conexion.close()
        return "Error", "Base de datos"
    

def leerUltFilaClima():
    # nos conectamos a la BBDD y leemos la última fila
    conexion = sqlite3.connect("bd1.db")
    cursor = conexion.cursor()
    cursor.execute("select * from weather order by id desc limit 1")
    ultimaFila = cursor.fetchone()
    conexion.close()
    # convertimos los datos a una tupla y la devolvemos
    datosClimaActual = ultimaFila[1], ultimaFila[2]
    return datosClimaActual

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

def manejoFichero():
   
    with open('AwD_figuras.json', 'r') as archivo:
        # cargamos el archivo json
        json_data = json.load(archivo)

        figuras = json_data["figuras"]
        lista_inicial = []
        # Iteramos sobre figuras
        for figura in figuras:

            info_dron = []
            lista_figura = []

            lista_figura.append(figura["Nombre"])
            drones = figura["Drones"]
            bucleFigura = True
            # Utilizamos el booleano para que no se hagan duplicados
            for dron in drones:
                if(bucleFigura):
                    dron_id = dron["ID"]
                    pos_x, pos_y = map(int, dron["POS"].split(","))
                    if dron_id == 1 and len(info_dron) > 1:
                        bucleFigura = False
                    else:
                        info_dron.append((dron_id, (pos_x, pos_y)))

            lista_figura.append(info_dron)
            lista_inicial.append(lista_figura)
            
    return(lista_inicial)

# dronMov = [E,ID,(X,Y)]
def manejoMapa(isMoved = False, dronMov = []):
    mapaBytes = [[0 for _ in range(20)] for _ in range(20)]
    listaMapa = []
  
    for coordX in mapaBytes:
        listaCoordX = []
        for coordY in coordX:
            listaCoordX.append(('E', 0))
        listaMapa.append(listaCoordX)

    if isMoved:
        estado = dronMov[0]
        Id = dronMov[1]
        movimiento = (dronMov[2][0]-1, dronMov[2][1]-1)
        
        listaMapa[movimiento[0]][movimiento[1]] = (estado, Id)


    return(listaMapa)

def stringMapa(listaMapa):
    strMapa = ""
    for fila in listaMapa:
        strMapa = strMapa + "| "
        for elemento in fila:
            strMapa = strMapa + "[" + elemento[0] + "," + str(elemento[1]) + "] "
        strMapa = strMapa + "|\n"

    return strMapa

def mandar_mapa(mapa):
    producer = KafkaProducer(
    value_serializer=lambda m: dumps(m).encode('utf-8'),
    bootstrap_servers=['localhost:9092'])

    producer.send("drones-topic", value=mapa)


### Funciones que manejan el fichero de drones y el mapa ###

#----------------------------------------------------------#

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

    print("Bienvenido al AD_Engine")
    programaActiveBool = True
    figuras = manejoFichero()
    # Bucle de menú principal
    while(programaActiveBool):
        print("Elige una opción:")
        print("1. Ver figuras disponibles")
        print("2. Salir")
        opcion = input()

        if(opcion == "1"):
            os.system("clear")
            # bucle de figuras
            programaFigurasBool = True
            while(programaFigurasBool):
                iterador = 1
                print("Selecciona una figura: ")
                for figura in figuras:
                    print(str(iterador) + ". " + figura[0])
                    iterador = iterador + 1
                print(str(iterador) + ". Salir")
                opcionFigura = input()
                
                try:
                    if(int(opcionFigura) < iterador and int(opcionFigura) > 0):
                        os.system("clear")
                        opcFiguraSelecBool = True
                        while(opcFiguraSelecBool):
                            print("Has seleccionado la figura: " + str(figuras[int(opcionFigura)-1][0]))
                            print("Elige una opción:")
                            print("1. Ver la figura final")
                            print("2. Ver la figura simplificada")
                            print("3. Comenzar el espectaculo directamente")
                            print("4. Salir")
                            opcionFiguraSelec = input()

                            if(opcionFiguraSelec == "1"):
                                os.system("clear")
                                print("Mostrando figura final")
                                # mostrar figura final
                            elif(opcionFiguraSelec == "2"):
                                os.system("clear")
                                print("Mostrando figura simplificada")
                                # mostrar figura simplificada
                                print(figuras[int(opcionFigura)-1][1])
                            elif(opcionFiguraSelec == "3"):
                                os.system("clear")
                                print("Comenzando espectaculo")
                                # comenzar espectaculo

                                opcFiguraSelecBool = False
                            elif(opcionFiguraSelec == "4"):
                                os.system("clear")
                                print("Saliendo de la figura seleccionada")
                                opcFiguraSelecBool = False
                            else:
                                os.system("clear")
                                print("Opción no válida")
                
                    elif(opcionFigura == str(iterador)):
                        os.system("clear")
                        print("Saliendo de la selección de figuras")
                        programaFigurasBool = False
                    else:
                        os.system("clear")
                        print("Opción no válida")
                except ValueError:
                    os.system("clear")
                    print("Opción no válida")

        elif(opcion == "2"):
            os.system("clear")
            print("Saliendo del programa")
            programaActiveBool = False
        else:
            os.system("clear")
            print("Opción no válida")

    #strMapa = manejoMapa()

    #IP_WEATHER = socket.gethostbyname(socket.gethostname())

    #conexionClima(IP_WEATHER, sys.argv[5])

    
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Max_Drones> <IP_Broker> <Puerto_Broker> <IP_Weather> <Puerto_Weather>")
