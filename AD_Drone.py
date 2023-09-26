import socket
import sys

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
FIN = "FIN"

########## MAIN ###########

if (len(sys.argv) == 3):
    SERVER = sys.argv[1]
    PORT = sys.argv[2]
    ADDR = (SERVER,PORT)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Se ha establecido la conexión con [{ADDR}]")

    
else:
    print("No se ha podido conectar al servidor de registro")
        