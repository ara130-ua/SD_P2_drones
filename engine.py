import time
from kafka import KafkaConsumer
from kafka import KafkaProducer
from json import loads
from json import dumps
import json

IP_Kafka = "localhost"

def consumidor(listaDronMov, num_drones):
    consumer = KafkaConsumer(
        'movimientos-topic',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='engine',
        value_deserializer=lambda m: loads(m.decode('utf-8')),
        bootstrap_servers=[IP_Kafka + ':9092']) 
    
    finalizados = 0

    for m in consumer:
        
        if(m.value[0] == 'G'):
            finalizados = finalizados + 1
            print("Dron " + str(m.value[1]) + " finalizado")

        if(finalizados == num_drones):
            return True

        actualizarMovimientos(listaDronMov, m.value)
            
        productor(listaDronMov)
            

def productor(mapa):
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=[IP_Kafka + ':9092'])
    
    print("Mapa enviado: " + str(mapa))
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

def actualizarMovimientos(listaDronMov, dronMov):
    for dron in listaDronMov:
        if(dron[1] == int(dronMov[1])):
            dron[2] = (dronMov[2][0], dronMov[2][1])
            return listaDronMov
       

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
lista_mapa = manejoFichero()[0][1]
num_drones = 2 #len(lista_mapa)
#envia el mapa
listaDronMovInicial = [] 
productor(lista_mapa)
for dronMov in lista_mapa:
    listaDronMovInicial.append(['R', dronMov[0], (1,1)])


#empieza a recoger los movimientos de los drones
if(consumidor(listaDronMovInicial,num_drones)):
    print("FIGURA COMPLETADA")
