import time
from kafka import KafkaConsumer
from kafka import KafkaProducer
from json import loads
from json import dumps

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


#### main ####
num_drones = 2
mapa = "1-5-9#2-5-4#3-5-9#4-2-0#5-1-4#6-9-9#7-5-9#8-5-9#9-5-9"
#envia el mapa 
productor(mapa)

#empieza a recoger los movimientos de los drones
if(consumidor(num_drones)):
    print("FIGURA COMPLETADA")
