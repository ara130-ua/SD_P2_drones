import socket
import random
import time
import sys

SERVER = "localhost" #socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])
FORMAT = 'utf-8'
HEADER = 64

# Añadir manejo de excepciones por si se cae el AD_Engine
def send(msg, cliente):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    cliente.send(send_length)
    print("Enviando mensaje: ", message)
    cliente.send(message)

   
        
    

def conexionEngine():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, PORT))
    server.listen()
    print(f"AD_Weather escuchando en {SERVER}")
    conn, addr = server.accept()
    manejoClima(conn, addr)


def manejoClima(conn, addr):
    print(f"Se ha conectado el AD_Engine {addr}")
    conectado = True
    while conectado:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except Exception as exc:
            print("Se ha cerrado la conexión inesperadamente")
            conn.close()
            conectado = False

        if msg_length:
            print("Se ha recibido del AD_Engine una petición de clima")
            strDatosClima = str(random.choice(datosClima))
            try:
                send(strDatosClima, conn)
            except Exception as exc:
                print("Se ha cerrado la conexión inesperadamente" + str(exc))
                conn.close()
                conectado = False
            
            print("Se ha enviado el clima al AD_Engine")
            msg_length = None
            time.sleep(12)
            
    
def manejoFicheroClima():
    with open('clima.txt', 'r') as archivo:
        lineas = archivo.readlines()

    datos_clima = []
    for linea in lineas:
        # Eliminamos espacios en blanco
        linea = linea.strip()
        if linea:
            elementos = linea.split('|')

            if len(elementos) == 2:
                datos_clima.append((str(elementos[0]), int(elementos[1])))
    
    return(datos_clima)



# main
# Añadir el puerto del AD_Wheather

print("Bienvenido al AD_Wheather")
datosClima = manejoFicheroClima()
conexionEngine()

