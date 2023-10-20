import socket
import random
import time

SERVER = '127.0.0.1'
PORT = 7050
FORMAT = 'utf-8'
HEADER = 64

def send(msg, clientE):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    cliente.send(send_length)
    print("Enviando mensaje: ", message)
    cliente.send(message)

def manejoClima():
    with open('clima.txt', 'r') as archivo:
        lineas = archivo.readlines()

    datos_clima = []
    for linea in lineas:
        # Eliminamos espacios en blanco
        linea = linea.strip()
        if linea:
            elementos = linea.split('|')

            if len(elementos) == 2:
                datos_clima.append(str(elementos[0]), int(elementos[1]))
    
    return(datos_clima)


# main
print("Bienvenido al AD_Wheather")

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
cliente.connect(ADDR)
print(f"Se ha establecido conexión en [{ADDR}]")

datos_clima = manejoClima()

# elegimos un clima aleatorio y cada cierto tiempo lo enviamos al AD_Engine

while True:
    clima = random.choice(datos_clima)
    send(clima, cliente)
    time.sleep(10) # mirar luego el tiempo de envio













