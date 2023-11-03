import time
from kafka import KafkaConsumer
from kafka import KafkaProducer
from json import loads
from json import dumps
import json

def consumidor(num_drones):
    consumer = KafkaConsumer(
        'movimientos-topic',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='engine',
        value_deserializer=lambda m: loads(m.decode('utf-8')),
        bootstrap_servers=['localhost:9092'])
    
    finalizados = 0

    for m in consumer: 
        if(m.value == "finish"):
            finalizados = finalizados +1
        if(finalizados == num_drones):
            return True
        
        actualiza_mapa(m.value)

def actualiza_mapa(movimiento):
    print ("Movimiento recibido: " + movimiento)
    mapa = "Esto es un mapa actualizado con el movimiento: " + str(movimiento) 
    productor(mapa)

def productor(mapa):
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=['localhost:9092'])
    
    print("Mapa enviado: " + mapa)
    producer.send("mapas-topic", value=mapa)
    time.sleep(1)


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


#----------------------------------------------------------#

### Funciones que manejan el fichero de drones y el mapa ###


#### main ####
num_drones = 2
lista_mapa = manejoMapa()
mapa = stringMapa(lista_mapa)
#envia el mapa 
productor(mapa)

#empieza a recoger los movimientos de los drones
if(consumidor(num_drones)):
    print("FIGURA COMPLETADA")
