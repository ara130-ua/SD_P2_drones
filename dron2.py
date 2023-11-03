from kafka import KafkaProducer
from kafka import KafkaConsumer
from json import loads
from json import dumps
import time
import random
import sys

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
def consumidor_mapas(id_dron, pos_actual, pos_final):
    consumer = KafkaConsumer(
        'mapas-topic',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id = id_dron,
        value_deserializer=lambda m: loads(m.decode('utf-8')),
        bootstrap_servers=[IP_KAFKA + ':9092'])
  
    
    #Comprobar en la segunda figura
    primerConsumidorBool = True

    for m in consumer:

        if(pos_final == run(pos_actual, pos_final)):
            listaDronMov[0] = 'G'
            productor(listaDronMov)

        if(primerConsumidorBool == False and isMapaActualizado(m.value, pos_actual, id_dron) and pos_actual != pos_final):
            print("loque seas")
            print(stringMapa(m.value))
            print("loque seas")

            listaDronMov[2] = run(pos_actual, pos_final)
            #['R',1,(2,3)]
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

      
        

def isMapaActualizado(mapa, pos_actual,id_dron):

    if(mapa[pos_actual[0]-1][pos_actual[1]-1] == id_dron):
        return True
    return False

#manda los movimientos al topic de los moviemtos
def productor(movimiento):
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=[IP_KAFKA + ':9092'])

    producer.send("movimientos-topic", value=movimiento)
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

    print("Posicion actualizada -->" + str((posInt_X, posInt_Y)))

    return (posInt_X, posInt_Y)

def stringMapa(listaMapa):
    strMapa = ""
    for fila in listaMapa:
        strMapa = strMapa + "| "
        for elemento in fila:
            strMapa = strMapa + "[" + elemento[0] + "," + str(elemento[1]) + "] "
        strMapa = strMapa + "|\n"

    return strMapa
    
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


consumidor_mapas(id_dron, pos_actual, pos_final)