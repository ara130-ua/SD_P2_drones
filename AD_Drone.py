import socket
import sys

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'

# conexión con el módulo AD_Registry para darse de alta en el sistema
def dronRegistry(ip_reg, puerto_reg, alias):
    
    ADDR = (str(ip_reg), int(puerto_reg))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Se ha establecido conexión en [{ADDR}]")
    send(alias, client)
    return receive(client)

def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    print("Enviando mensaje: ", message)
    client.send(message)
    

def receive(client):
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        print(f"Se ha recibido del servidor: {msg}")
        id, token = msg.split(",")
        return id, token
    else:
        print("No se ha recibido nada del servidor")
        return None

########## MAIN ###########
# ip y puerto del engine
# ip y puerto kafka
# ip y puerto de registry
# alias del dron
if (len(sys.argv) == 8):
    id, token = dronRegistry(sys.argv[5], sys.argv[6], sys.argv[7])
    print( "id: ", id, " token: ", token)
    
else:
    print("No se ha podido conectar al servidor de registro, los argumentos son <IP_Engine> <Puerto_Engine> <IP_Kafka> <Puerto_Kafka> <IP_Registry> <Puerto_Registry> <Alias_Dron>")
        