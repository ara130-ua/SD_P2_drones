import socket
import sys
from kafka import KafkaProducer
from kafka import KafkaConsumer
from json import loads
from json import dumps
import time
import pygame
import signal


HEADER = 64
FORMAT = 'utf-8'

#----------------------------------------------------#

def handle_alarm(signum, frame):
    raise TimeoutError()

### Funciones para el manejo de kafka ###

#devuelve todos los mapas segun llegan al topic
def consumidor_mapas(id_dron, pos_actual, pos_final):
    consumer = KafkaConsumer(
        'mapas1-topic',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id = id_dron,
        value_deserializer=lambda m: loads(m.decode('utf-8')),
        bootstrap_servers=[ADDR_KAFKA])
  

    #LEER
    # hay que tener en cuenta que el producor de movimientos depende de si el mapa esta actualizado o no, esto implica que si al consumir un mapa 
    # mandamos inmediatamente un movimiento y leemos, puede que no demos tiempo a que el productor de movimientos actualice el mapa, por lo que
    # el consumidor de mapas no detectara que el mapa esta actualizado y mandara un movimiento REPETIDO.

    
    #Comprobar en la segunda figura
    primerConsumidorBool = True
    figuraCompleta = False

    signal.signal(signal.SIGALRM, handle_alarm)
    
    for m in consumer:

        print("Recibido mapa: " + str(m.value))
        if((pos_actual[0], pos_actual[1]) == (pos_final[0], pos_final[1]) and figuraCompleta == True):
            return True

        if(m.value == "FIGURA COMPLETADA" or m.value == "CLIMA ADVERSO"):
            pos_final = (1,1)
            figuraCompleta = True
            print("Vuelvo a casa")
            pos_actual = run(pos_actual, pos_final)
            listaDronMov = ['R', id_dron, pos_actual]
            productor(listaDronMov)
            continue

        if(primerConsumidorBool == False and (pos_actual[0], pos_actual[1]) == (pos_final[0], pos_final[1]) and listaDronMov[0] != 'G'):
            listaDronMov[0] = 'G'
            print("El dron con id: " + str(id_dron) + " ha llegado a su destino")
            productor(listaDronMov)
            #print(stringMapa(crearMapa(m.value)))
            pygameMapa(crearMapa(m.value))


        elif(primerConsumidorBool == False and isMapaActualizado(m.value, pos_actual, id_dron) and (pos_actual[0], pos_actual[1]) != (pos_final[0], pos_final[1])):
            # crear y pintar el mapa
            #print(stringMapa(crearMapa(m.value)))
            pygameMapa(crearMapa(m.value))

            pos_actual = run(pos_actual, pos_final)
            print("Posicion actualizada -->" + str(pos_actual))
            listaDronMov[2] = pos_actual
            # ['R', ID, (X,Y)]
            productor(listaDronMov)

        elif(primerConsumidorBool):
            pos_final = saca_pos_final(m.value, int(id_dron))
            print("La posicion a la que tengo que ir: "+ str(pos_final))
            pos_actual = run(pos_actual, pos_final)
            listaDronMov = ['R', id_dron, pos_actual]
            productor(listaDronMov)
            primerConsumidorBool = False
        else:
            #print(stringMapa(crearMapa(m.value)))
            pygameMapa(crearMapa(m.value))

        print(listaDronMov)
            
            
#manda los movimientos al topic de los moviemtos
def productor(movimiento):
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=[ADDR_KAFKA])

    producer.send("movimientos1-topic", value=movimiento)
    time.sleep(1)
        
### Funciones para el manejo de kafka ###

#----------------------------------------------------#

### Funciones para el manejo de pygame ###


# Función para dibujar el mapa de bits
def draw_grid():
    for x in range(0, WINDOW_SIZE[0], GRID_SIZE):
        pygame.draw.line(screen, (255, 255, 255), (x, 0), (x, WINDOW_SIZE[1]))
    for y in range(0, WINDOW_SIZE[1], GRID_SIZE):
        pygame.draw.line(screen, (255, 255, 255), (0, y), (WINDOW_SIZE[0], y))


def pygameMapa(listaMapa):

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))
    draw_grid()


    
    #listaMapa tiene el siguiente formato: [[(color, id), (color, id), ...], [(color, id), (color, id), ...], ...
    for y, fila in enumerate(listaMapa):
        for x, elemento in enumerate(fila):
            color = elemento[0]

            if color == 'G':
                drone_color = (0, 255, 0)  # Verde
                drone_rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, DRONE_SIZE, DRONE_SIZE)
                pygame.draw.rect(screen, drone_color, drone_rect)
            elif color == 'R':
                drone_color = (255, 0, 0)  # Rojo
                drone_rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, DRONE_SIZE, DRONE_SIZE)
                pygame.draw.rect(screen, drone_color, drone_rect)

    pygame.display.update()


### Funciones para el manejo de pygame ###

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

    if(pos_actual[0] > pos_final[0]):
        posInt_X = pos_actual[0]-1

    if(pos_actual[1] > pos_final[1]):
        posInt_Y = pos_actual[1]-1

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

def stringMapa(listaMapa):
    strMapa = ""
    for fila in listaMapa:
        strMapa = strMapa + "| "
        for elemento in fila:
            strMapa = strMapa + "[" + elemento[0] + "," + str(elemento[1]) + "] "
        strMapa = strMapa + "|\n"

    return strMapa

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


### Funciones para el manejo de mapas ###
        
#----------------------------------------------------#

### Funciones de conexión con los módulos ###

# conexión con el módulo AD_Registry para darse de alta en el sistema
def dronRegistry(ip_reg, puerto_reg, alias):
    
    ADDR = (str(ip_reg), int(puerto_reg))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        print(f"Se ha establecido conexión en [{ADDR}]")
        send(alias, client)
        message = receive(client)
        id, token = message.split(",")
        return id, token
    except Exception as exc:
        return None, None

# conexión con el módulo AD_Engine para darse de alta en el espectaculo
def dronEngine(ip_eng, puerto_eng, id, token):
    try:
        ADDR = (str(ip_eng), int(puerto_eng))

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        print(f"Se ha establecido conexión en [{ADDR}]")
        send(id+","+token, client)
        message = receive(client)
        if message == "OK":
            return True
        else:
            return False
    except Exception as exc:
        print("No se ha podido conectar con el engine: " + str(exc))
        return False

    
### Funciones de conexión con los módulos ###

#----------------------------------------------------#

### Funciones de send y receive ###

def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    print("Enviando mensaje: ", send_length)
    client.send(send_length)
    print("Enviando mensaje: ", message)
    client.send(message)
    
# este método solo se usa con el registry ya que le da un formato al mensaje
def receive(client):
    try:
        msg_length = client.recv(HEADER).decode(FORMAT)
    except Exception as exc:
        print("Se ha cerrado la conexión inesperadamente")
        client.close()
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        print(f"Se ha recibido del servidor: {msg}")
        return msg
    else:
        print("No se ha recibido nada del servidor")
        return None
    
    
### Funciones de send y receive ###

#----------------------------------------------------#
    


########## MAIN ###########
# ip y puerto del engine
# ip y puerto kafka
# ip y puerto de registry
# puerto de escucha del dron
# alias del dron
if (len(sys.argv) == 9):

    IP_ENGINE = sys.argv[1] 
    PUERTO_ENGINE = sys.argv[2]

    IP_KAFKA = sys.argv[3]
    PUERTO_KAFKA = sys.argv[4]
    ADDR_KAFKA = IP_KAFKA + ":" + str(PUERTO_KAFKA)

    IP_REGISTRY = sys.argv[5]
    PUERTO_REGISTRY = sys.argv[6]

    PORT = sys.argv[7]
    ALIAS_DRON = sys.argv[8]

    pos_actual = (0,0)
    pos_final = (int,int)

    ############################ PYGAME ############################

    # export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6

    # Inicializa Pygame
    pygame.init()

    # Definir constantes
    WINDOW_SIZE = (400, 400)
    GRID_SIZE = 20
    DRONE_SIZE = 20

    # Crea la ventana de juego
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Mapa impreso desde el dron: " + str(sys.argv[7]))

    ################################################################

    #Argumentos dronRegistry( IP_Registry, Puerto_Registry, Alias_Dron )
    id, token = dronRegistry(IP_REGISTRY, PUERTO_REGISTRY, ALIAS_DRON)
    if id:

        print( "id: ", id, " token: ", token)
        
        # conexion con el módulo AD_Engine para darse de alta en el espectaculo
        #Argumentos dronEngine( IP_Engine, Puerto_Engine, ID, Token)
    
        engineOnline = True
        while engineOnline:
            if(dronEngine(IP_ENGINE, PUERTO_ENGINE, id, token)):
                # conexion con el módulo AD_Kafka para recibir las ordenes
                #Argumentos consumidor( IP_Kafka, Puerto_Kafka, ID )
                try:
                    engineOnline = consumidor_mapas(id, pos_actual, pos_final)
    
                    if(engineOnline == False):
                        print("Se ha cerrado la conexión inesperadamente con el engine" + str(exc))
                    engineOnline = False
                    print("Vuelvo a casa")
                    while(pos_actual != (1,1)):
                        
                        pos_actual = run(pos_actual, (1,1))
                        print("Posicion actualizada -->" + str(pos_actual))
                        time.sleep(1)
    
                except Exception as exc:
                    print("Se ha cerrado la conexión inesperadamente con el engine" + str(exc))
                    engineOnline = False
                    print("Vuelvo a casa")
                    while(pos_actual != (1,1)):
                        pos_actual = run(pos_actual, (1,1))
                        print("Posicion actualizada -->" + str(pos_actual))
                        time.sleep(1)
                print("Quieres volver a participar en otra figura? (S/N)")
                respuesta = input()
                if(respuesta == "S" or respuesta == "s"):
                    engineOnline = True
                    pos_actual = (0,0)
                    pos_final = (int,int)
                else:
                    engineOnline = False
            else:
                print("No se ha podido entrar al espectaculo")
                engineOnline = False
    else:
        print("No se ha podido registrar el dron")
        
else:
    print("No se ha podido conectar al servidor de registro, los argumentos son <IP_Engine> <Puerto_Engine> <IP_Kafka> <Puerto_Kafka> <IP_Registry> <Puerto_Registry> <Puerto_escucha> <Alias_Dron>")
        