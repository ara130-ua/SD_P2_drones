import socket
import sys

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'



# conexión con el módulo AD_Registry para darse de alta en el sistema
def dronRegistry(ip_reg, puerto_reg, alias):
    SERVER = ip_reg
    PORT = puerto_reg
    ADDR = (SERVER, PORT)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Se ha establecido conexión en [{ADDR}]")

    # envio del mensaje
    message = alias.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

#def send(msg):
#    message = msg.encode(FORMAT)
#    msg_length = len(message)
#    send_length = str(msg_length).encode(FORMAT)
#    send_length += b' ' * (HEADER - len(send_length))
#    client.send(send_length)
#    client.send(message)

########## MAIN ###########
# ip y puerto del engine
# ip y puerto kafka
# ip y puerto de registry
# alias del dron
if (len(sys.argv) == 8):
    dronRegistry(sys.argv[1], sys.argv[2], sys.argv[8])
else:
    print("No se ha podido conectar al servidor de registro")
        