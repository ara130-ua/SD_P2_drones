import socket
import sys
from kafka import KafkaProducer
from kafka import KafkaConsumer
from json import loads
from json import dumps
import time
import random


HEADER = 64
PORT = 5050 # hay que quitarlo y se quedará como argumento
FORMAT = 'utf-8'

#----------------------------------------------------#

### Funciones para el manejo de kafka ###

#devuelve todos los mapas segun llegan al topic
def consumidor_mapas(id_dron, pos_actual, pos_final):
    consumer = KafkaConsumer(
        'mapas-topic',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id = id_dron,
        value_deserializer=lambda m: loads(m.decode('utf-8')),
        bootstrap_servers=[IP_KAFKA + ':9092'])
  

    #LEER
    # hay que tener en cuenta que el producor de movimientos depende de si el mapa esta actualizado o no, esto implica que si al consumir un mapa 
    # mandamos inmediatamente un movimiento y leemos, puede que no demos tiempo a que el productor de movimientos actualice el mapa, por lo que
    # el consumidor de mapas no detectara que el mapa esta actualizado y mandara un movimiento REPETIDO.

    
    #Comprobar en la segunda figura
    primerConsumidorBool = True
    
    for m in consumer:

        if(primerConsumidorBool == False and (pos_actual[0], pos_actual[1]) == (pos_final[0], pos_final[1]) and listaDronMov[0] != 'G'):
            listaDronMov[0] = 'G'
            productor(listaDronMov)
            print(stringMapa(crearMapa(m.value)))

        elif(primerConsumidorBool == False and isMapaActualizado(m.value, pos_actual, id_dron) and (pos_actual[0], pos_actual[1]) != (pos_final[0], pos_final[1])):
            # crear y pintar el mapa
            print(stringMapa(crearMapa(m.value)))

            pos_actual = run(pos_actual, pos_final)
            print("Posicion actualizada -->" + str(pos_actual))
            listaDronMov[2] = pos_actual
            # ['R', ID, (X,Y)]
            productor(listaDronMov)

            #productor("finish") mirar que hacer cuando finish se le pase al engine, cuando sea finish no puede actualizar
            #print("no llega por cualquier motivo o ha terminado") 

        if(primerConsumidorBool):
            pos_final = saca_pos_final(m.value, int(id_dron))
            print("La posicion a la que tengo que ir: "+ str(pos_final))
            pos_actual = run(pos_actual, pos_final)
            listaDronMov = ['R', id_dron, pos_actual]
            productor(listaDronMov)
            primerConsumidorBool = False
            
            
#manda los movimientos al topic de los moviemtos
def productor(movimiento):
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=[IP_KAFKA + ':9092'])

    producer.send("movimientos-topic", value=movimiento)
    time.sleep(1)
        
### Funciones para el manejo de kafka ###

#----------------------------------------------------#

### Funciones para el manejo de movimientos ###

def run(pos_actual, pos_final):
    #realiza un movimiento en base al mapa y lo manda a la cola de mapas
    if(pos_actual is None or pos_final is None):
        pos_actual = (0,0)
        pos_final = (0,0)

    posInt_X = pos_actual[0]
    posInt_Y = pos_actual[1]

    if(pos_actual[0] < pos_final[0]):
        posInt_X = pos_actual[0]+1

    if(pos_actual[1] < pos_final[1]):
        posInt_Y = pos_actual[1]+1

    return (posInt_X, posInt_Y)

def saca_pos_final(listaFigura, id_dron):
    #saca la posicion final del mapa
    #el mapa tiene que tener el siguiente formato: "id_dron-posX-posY#id_dron-posX-posY#..."

    for dron in listaFigura:
        if(dron[0] == id_dron):
            return dron[1]

### Funciones para el manejo de movimientos ###

#----------------------------------------------------#

### Funciones para el manejo de mapas ###

def isMapaActualizado(listaDronMov, pos_actual,id_dron):

    for dronMov in listaDronMov:
        if(dronMov[1] == int(id_dron) and (dronMov[2][0], dronMov[2][1]) == pos_actual):
            return True
    return False

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

# dronMov = ['R',ID,(X,Y)]
def actualizaMapa(listaMapa, dronMov):
    estado = dronMov[0]
    Id = dronMov[1]
    movimiento = (int(dronMov[2][0])-1, int(dronMov[2][1])-1)
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

### Funciones para el manejo de mapas ###
        
#----------------------------------------------------#

### Funciones de conexión con los módulos ###

# conexión con el módulo AD_Registry para darse de alta en el sistema
def dronRegistry(ip_reg, puerto_reg, alias):
    
    ADDR = (str(ip_reg), int(puerto_reg))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Se ha establecido conexión en [{ADDR}]")
    send(alias, client)
    return receive(client)

# conexión con el módulo AD_Engine para darse de alta en el espectaculo
## NO SE HA PROBADO ##
def dronEngine(ip_eng, puerto_eng, id, token):
    
    ADDR = (str(ip_eng), int(puerto_eng))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Se ha establecido conexión en [{ADDR}]")
    send(id+","+token, client)
    respEngine = client.recv(HEADER).decode(FORMAT)
    if respEngine == "OK":
        print("Se ha dado de alta en el espectaculo")
        return True
    if respEngine == "KO":
        print("No se ha podido dar de alta en el espectaculo")
        return False
    
### Funciones de conexión con los módulos ###

#----------------------------------------------------#

### Funciones de send y receive ###

def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    print("Enviando mensaje: ", message)
    client.send(message)
    
# este método solo se usa con el registry ya que le da un formato al mensaje
def receive(client):
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        print(f"Se ha recibido del servidor: {msg}")
        id, token = msg.split(",")
        return id, token
    else:
        print("No se ha recibido nada del servidor")
        return None
    
### Funciones de send y receive ###

#----------------------------------------------------#
    


########## MAIN ###########
# ip y puerto del engine
# ip y puerto kafka
# ip y puerto de registry
# alias del dron
if (len(sys.argv) == 8):
    #Argumentos dronRegistry( IP_Registry, Puerto_Registry, Alias_Dron )
    id, token = dronRegistry(sys.argv[5], sys.argv[6], sys.argv[7])
    print( "id: ", id, " token: ", token)
    
    # conexion con el módulo AD_Engine para darse de alta en el espectaculo
    #Argumentos dronEngine( IP_Engine, Puerto_Engine, ID, Token)
    
    ## NO SE HA PROBADO ##
    if(dronEngine(sys.argv[1], sys.argv[2], id, token)):
        # conexion con el módulo AD_Kafka para recibir las ordenes
        #Argumentos consumidor( IP_Kafka, Puerto_Kafka, ID )
        consumidor_mapas(sys.argv[3], sys.argv[4], id)
       
    
else:
    print("No se ha podido conectar al servidor de registro, los argumentos son <IP_Engine> <Puerto_Engine> <IP_Kafka> <Puerto_Kafka> <IP_Registry> <Puerto_Registry> <Alias_Dron>")
        