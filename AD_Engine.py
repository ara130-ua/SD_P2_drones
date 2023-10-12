import socket
import threading
import sys
import sqlite3

#def consulta_Clima():
    

####main#####
print ("Bienvenido al AD_Engine")


#usaremos 6 argumentos, la BBDD no necesita de conexion
if  (len(sys.argv) == 6):
    PORT = int(sys.argv[1])
    MAX_DRONES = int(sys.argv[2])

    IP_BROKER = sys.argv[3]
    PORT_BROKER = int(sys.argv[4])

    ADDR_BROKER = (IP_BROKER, PORT_BROKER)

    IP_WEATHER= sys.argv[5]
    PORT_WEATHER= int(sys.argv[6])
    
    ADDR_WEATHER = (IP_WEATHER, PORT_WEATHER)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print (f"Establecida conexión en [{ADDR}]")

    msg=sys.argv[3]
    while msg != FIN :
        print("Envio al servidor: ", msg)
        send(msg)
        print("Recibo del Servidor: ", client.recv(2048).decode(FORMAT))
        msg=input()

    print ("SE ACABO LO QUE SE DABA")
    print("Envio al servidor: ", FIN)
    send(FIN)
    client.close()
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto> <Max_Drones> <IP_Broker> <Puerto_Broker> <IP_Weather> <Puerto_Weather>")
