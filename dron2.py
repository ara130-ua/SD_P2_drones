from kafka import KafkaProducer
from kafka import KafkaConsumer
from json import loads
from json import dumps
import time
import random
import sys
import pygame

IP_KAFKA = "localhost"

#def consumidor_primerMapa(id_dron):
#    consumer = KafkaConsumer(
#        'mapas-topic',
#        auto_offset_reset='earliest',
#        enable_auto_commit=True,
#        group_id = id_dron,
#        value_deserializer=lambda m: loads(m.decode('utf-8')),
#       bootstrap_servers=[IP_KAFKA + ':9092'])
#
#   #devuelve el primer mapa
#    for m in consumer:
#        if(m.value):
#            return m.value
    

#devuelve todos los mapas segun llegan al topic
def consumidor_mapas(id_dron, pos_actual, pos_final,topicMap, topicMov):
    consumer = KafkaConsumer(
        topicMap,
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
    figuraCompleta = False
    
    for m in consumer:
        
        if((pos_actual[0], pos_actual[1]) == (pos_final[0], pos_final[1]) and figuraCompleta == True):
            return True

        if(m.value == "FIGURA COMPLETADA"):
            pos_final = (1,1)
            figuraCompleta = True
            print("Vuelvo a casa")
            pos_actual = run(pos_actual, pos_final)
            listaDronMov = ['R', id_dron, pos_actual]
            productor(listaDronMov, topicMov)
            continue

        if(primerConsumidorBool == False and (pos_actual[0], pos_actual[1]) == (pos_final[0], pos_final[1]) and listaDronMov[0] != 'G'):
            listaDronMov[0] = 'G'
            productor(listaDronMov, topicMov)
            #print(stringMapa(crearMapa(m.value)))
            pygameMapa(m.value)

        elif(primerConsumidorBool == False and isMapaActualizado(m.value, pos_actual, id_dron) and (pos_actual[0], pos_actual[1]) != (pos_final[0], pos_final[1])):
            # crear y pintar el mapa
            #print(stringMapa(crearMapa(m.value)))
            pygameMapa(m.value)

            pos_actual = run(pos_actual, pos_final)
            print("Posicion actualizada -->" + str(pos_actual))
            listaDronMov[2] = pos_actual
            # ['R', ID, (X,Y)]
            productor(listaDronMov, topicMov)

        elif(primerConsumidorBool):
            pos_final = saca_pos_final(m.value, int(id_dron))
            print("La posicion a la que tengo que ir: "+ str(pos_final))
            pos_actual = run(pos_actual, pos_final)
            listaDronMov = ['R', id_dron, pos_actual]
            productor(listaDronMov, topicMov)
            primerConsumidorBool = False
        else:
            #print(stringMapa(crearMapa(m.value)))
            pygameMapa(m.value)

   

def isMapaActualizado(listaDronMov, pos_actual,id_dron):

    for dronMov in listaDronMov:
        if(dronMov[1] == int(id_dron) and (dronMov[2][0], dronMov[2][1]) == pos_actual):
            return True
    return False    
    

#manda los movimientos al topic de los moviemtos
def productor(movimiento, topicMov):
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=[IP_KAFKA + ':9092'])

    producer.send(topicMov, value=movimiento)
    time.sleep(1)

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

# Inicializa Pygame
pygame.init()

# Definir constantes
WINDOW_SIZE = (400, 400)
GRID_SIZE = 20
DRONE_SIZE = 20

# Crea la ventana de juego
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Mapa impreso desde el dron: " + str(sys.argv[1]))


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
    
    #listaMapa tiene el siguiente formato [[color, id, (x,y)], [color, id, (x,y)], ...]
    for drone in listaMapa:
        color = drone[0]
        x = drone[2][0]
        y = drone[2][1]

        if color == 'R':
            drone_color = (255, 0, 0)  # Rojo
        else:
            drone_color = (0, 255, 0)  # Verde

        drone_rect = pygame.Rect((x-1) * GRID_SIZE, (y-1) * GRID_SIZE, DRONE_SIZE, DRONE_SIZE)
        pygame.draw.rect(screen, drone_color, drone_rect)

        #pygame.draw.rect(screen, drone_color, (x*20, y*20, DRONE_SIZE, DRONE_SIZE))

    pygame.display.update()

    
def saca_pos_final(listaFigura, id_dron):
    #saca la posicion final del mapa
    #el mapa tiene que tener el siguiente formato: "id_dron-posX-posY#id_dron-posX-posY#..."

    #posiciones = mapa.split("#")
    #for p in posiciones:
    #    if(p.split("-")[0] == str(id_dron)):
    #        return (int(p.split("-")[1]), int(p.split("-")[2]))

    for dron in listaFigura:
        if(dron[0] == id_dron):
            return dron[1]





############################################
################ main ######################
############################################


id_dron = str(sys.argv[1])

#formato para las posiciones (x,y)
pos_actual = (0,0)
pos_final = (int,int)

#coge el mapa que le servira para orientarse
#mapa = consumidor_primerMapa(id_dron)
engineConn = True


#saca la posicion a la que tendra que llegar el dron
#pos_final = saca_pos_final(mapa, int(id_dron))
#print("La posicion a la que tengo que ir: "+ str(pos_final))
topicMap = "mapas1-topic"
topicMov = "movimientos1-topic"

consumidor_mapas(id_dron, pos_actual, pos_final, topicMap, topicMov)
#time.sleep(10)

print("Empezamos la segunda figura")
pos_actual = (0,0)
pos_final = (int,int)

topicMap = "mapas2-topic"
topicMov = "movimientos2-topic"
consumidor_mapas(id_dron, pos_actual, pos_final, topicMap, topicMov)