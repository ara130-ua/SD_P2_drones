import socket
import threading
import sys

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

def manejo_dron(conn, addr):
    print(f"Se ha conectado el dron {addr}")
    conectado = True
    while conectado:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except Exception as exc:
            print("Se ha cerrado la conexión inesperadamente")
            conn.close()
        if msg_length:
            msg_length = int(msg_length)
            alias = conn.recv(msg_length).decode(FORMAT)
            # pasamos el alias a la bbdd
            # leeremos de la bbdd el id y el token, y se lo devolveremos al dron



def registro_dron():
    server.listen()
    print(f"AD_Registry escuchando en  {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=manejo_dron, args=(conn, addr))


# main
# Parametros de AD_Registry
# puerto de escucha
# ip y puerto de la bbdd
if(len(sys.argv) == 4):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    registro_dron()
else:
    print("AD_Registry necesita estos argumentos <Puerto de escucha>, <IP de la BBDD>, <Puerto de la BBDD>")


#127.0.0.1