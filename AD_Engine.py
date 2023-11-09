import socket
import subprocess
import threading
import sys
import sqlite3
import time
import json
import os
from kafka import KafkaProducer
from json import dumps
from json import loads
from kafka import KafkaConsumer

HEADER = 64
FORMAT = 'utf-8'
SERVER = "localhost" #socket.gethostbyname(socket.gethostname())

#----------------------------------------------------------#

### Funciones que manejan kafka ###

def productor(mapa):
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=[ADDR_BROKER])
    
    print("Mapa enviado: " + str(mapa))
    producer.send('mapas1-topic', value=mapa)
    time.sleep(1)

def consumidor(listaDronMov, num_drones):
    consumer = KafkaConsumer(
        'movimientos1-topic',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='engine',
        value_deserializer=lambda m: loads(m.decode('utf-8')),
        bootstrap_servers=[ADDR_BROKER]) 
    
    finalizados = 0
    enBase = 0
    volverBase = False

    for m in consumer:
        
        if(m.value[0] == 'G'):
            finalizados = finalizados + 1
            print("Dron " + str(m.value[1]) + " finalizado")

        if(finalizados == num_drones):
            productor("FIGURA COMPLETADA")
            finalizados = 0
            volverBase = True
            

        actualizarMovimientos(listaDronMov, m.value)
            
        productor(listaDronMov)

        if(volverBase==True):
            enBase = 0
            for dron in listaDronMov:
                if(dron[2] == (1,1)):
                    enBase = enBase + 1
            if(enBase == 8):
                return True

def espectaculo(listaMapa, numMaxDrones):
    productor(listaMapa)
    listaDronMovInicial = []
    for dronMov in listaMapa:
        listaDronMovInicial.append(['R', dronMov[0], (1,1)])
    
    if(numMaxDrones < len(listaMapa)):
        print("No hay suficientes drones para realizar el espectaculo")
    else:
        if(consumidor(listaDronMovInicial, len(listaMapa))):
            print("Figura finalizada")

        delete_topic1 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --delete --topic mapas1-topic --bootstrap-server " + ADDR_BROKER + "; exec bash'"
        delete_topic2 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --delete --topic movimientos1-topic --bootstrap-server " + ADDR_BROKER + "; exec bash'"
        subprocess.run(delete_topic2, shell=True) 
        subprocess.run(delete_topic1, shell=True)
        # si hace algo raro time.sleep(5)



### Funciones que manejan kafka ###

#----------------------------------------------------------#

### Funciones de servidor ###

def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    try:
        client.send(send_length)
        print("Enviando mensaje: ", message)
        client.send(message)
    except Exception as exc:
        print("Se ha cerrado la conexión inesperadamente")
        client.close()

def receive(client):
    try:
        msg_length = client.recv(HEADER).decode(FORMAT)
        if msg_length:
            print(f"Se ha recibido algo {msg_length}")
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(FORMAT)
            print(f"Se ha recibido: {msg}")
            return msg
        else:
            #print("No se ha recibido nada")
            return None
    except:
        print("No se ha encontrado conexión o se ha caido")
        return None

    
### Funciones de servidor ###

#----------------------------------------------------------#

### Funciones de BBDD ###

def climaBBDD(datos_clima):
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
    try:
        cursor = conexion.cursor()
        cursor.execute("select * from weather order by id desc limit 1")
        ultimaFila = cursor.fetchone()
        conexion.close()
        # convertimos los datos a una tupla y la devolvemos
        datosClimaActual = ultimaFila[1], ultimaFila[2]
    except sqlite3.OperationalError:
        print("Error al leer la última fila de la BBDD")
        conexion.close()
        return None
    return datosClimaActual

    # no está testado #
def leerTokenDron(id):
    # nos conectamos a la BBDD y leemos el token del dron con la id recibida
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("select token from drones where id="+str(id))
        token = cursor.fetchone()[0]
        conexion.close()
    except sqlite3.OperationalError:
        print("Error al leer el token del dron")
        conexion.close()
        return None
    # devolvemos el token
    return token

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
        if(datos_clima == None):
            conectado = False
            break
        print(f"Se ha recibido del AD_Weather {addr} los datos de clima: {datos_clima}")
        # guardar en la BBDD
        print(climaBBDD(datos_clima))
        # saca la temperatura del string datos_clima
        # si la temperatura es negativa, se envia a los drones a la base
        for i in datos_clima:
            if(i == "-"):
                productor("CLIMA ADVERSO")


        time.sleep(10)
    print(f"Se ha cerrado la conexión con el AD_Weather {addr}")

### Funciones que manejan la conexion con el AD_Wheather ###

#----------------------------------------------------------#

### Funciones que manejan la conexion con los drones ###

def manejoTokenDrones(conn, addr):
    print(f"Se ha conectado el dron {addr}")

    tokenDron = receive(conn)
    if tokenDron:
        id, token = tokenDron.split(",")
        print(f"Se ha recibido del dron {addr} con id: {id} el token: {token}")
        # leemos de la base de datos el token del dron con la id recibida
        if(str(leerTokenDron(id)) == token):
            send("OK", conn)
            print("Token correcto")
            return True
        else:
            send("KO", conn)
            print("Token incorrecto")
            return False

                
def autentificacionDrones(numDrones, numDronesFigura):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR_ENGINE) 
    print(f"AD_Engine escuchando en  {ADDR_ENGINE}")
    terminados = 0
    for i in range(numDrones):
        server.listen()
        conn, addr = server.accept()
        if manejoTokenDrones(conn, addr):
            terminados = terminados + 1
    # conexion con el número de drones que vayan a participar en la figura
    # en el caso de que no se conecten todos, se cancela el espectaculo
    # comprobar que todos los drones se han conectado
    if(terminados == numDronesFigura):
        print("Todos los drones se han conectado")
        return True
    


### Funciones que manejan la conexion con los drones ###

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

def actualizarMovimientos(listaDronMov, dronMov):
    for dron in listaDronMov:
        if(dron[1] == int(dronMov[1])):
            dron[2] = (dronMov[2][0], dronMov[2][1])
            return listaDronMov
        
# listaDronMovActuales = [['R', ID, (X,Y)], ['R',ID,(X,Y)], ...]
def crearMapa(listaDronMovActuales):
    mapaBytes = [[0 for _ in range(20)] for _ in range(20)]
    listaMapa = []
  
    for coordX in mapaBytes:
        listaCoordX = []
        for coordY in coordX:
            listaCoordX.append(('E', 0))
        listaMapa.append(listaCoordX)
        
        
    for dron in listaDronMovActuales:
        listaMapa = actualizaMapa(listaMapa, dron)

    return(listaMapa)

# dronMov = [(ID,(X,Y))]
def actualizaMapa(listaMapa, dronMov):
    estado = 'G'
    Id = dronMov[0]
    movimiento = (int(dronMov[1][0])-1, int(dronMov[1][1])-1)
    listaMapa[movimiento[0]][movimiento[1]] = (estado, Id)
    return listaMapa
       

def stringMapa(listaMapa):
    strMapa = ""
    for fila in listaMapa:
        strMapa = strMapa + "| "
        for elemento in fila:
            strMapa = strMapa + "[" + elemento[0] + "," + str(elemento[1]) + "] "
        strMapa = strMapa + "|\n"

    return strMapa

### Funciones que manejan el fichero de drones y el mapa ###

#----------------------------------------------------------#

#usaremos 6 argumentos, la BBDD no necesita de conexion
# número máximo de drones
# puerto de escucha del AD_Engine
# puerto del AD_Engine
# IP y puerto del Broker
# IP y puerto del AD_Wheather
if  (len(sys.argv) == 7):
    
    # zona de argumentos
    
    numMaxDrones = int(sys.argv[2])
    PORT_ENGINE = int(sys.argv[1])
    ADDR_ENGINE = (SERVER, PORT_ENGINE)

    IP_BROKER = str(sys.argv[3])
    PORT_BROKER = sys.argv[4]

    ADDR_BROKER = str(IP_BROKER) + ":" + str(PORT_BROKER)

    IP_WEATHER = sys.argv[5]
    PORT_WEATHER = int(sys.argv[6])
    ADDR_WEATHER = (IP_WEATHER, PORT_WEATHER)

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
                        listaMapa = figuras[int(opcionFigura)-1][1]
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
                                print(stringMapa(crearMapa(listaMapa)))
                                # mostrar figura final
                            elif(opcionFiguraSelec == "2"):
                                os.system("clear")
                                print("Mostrando figura simplificada")
                                # mostrar figura simplificada
                                print(listaMapa)
                            elif(opcionFiguraSelec == "3"):
                                os.system("clear")
                                print("Comenzando espectaculo")
                                # comenzar espectaculo
                        
                                # Autenticación de los drones
                                if(autentificacionDrones(numMaxDrones, len(listaMapa))):
                                
                                    print("Servidor clima")
                                    conexionClima(IP_WEATHER, PORT_WEATHER)

                                    espectaculo(listaMapa, numMaxDrones)

                                    
                                    # Hacer un bucle que cada x tiempo lea la BBDD y si hay un cambio en la temperatura (negativo)
                                    # llama a la función de vuelta a base, que envia a los drones a la posicion (1,1)
                                

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


    
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto_engine> <Max_Drones> <IP_Broker> <Puerto_Broker> <IP_Weather> <Puerto_Weather>")
