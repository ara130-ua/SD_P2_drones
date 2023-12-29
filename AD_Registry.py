import socket
import threading
import time
import json
import sys
import sqlite3
from random import randint
from fastapi import FastAPI

app = FastAPI()

HEADER = 64
SERVER = "localhost" #socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'

#---------------------------------------------#

### Funciones del manejo de los drones ###

def manejo_dron(conn, addr):
    print(f"Se ha conectado el dron {addr}")
    try:
        msg_length = conn.recv(HEADER).decode(FORMAT)
    except Exception as exc:
        print("Se ha cerrado la conexión inesperadamente")
        conn.close()
    if msg_length:
        print(f"Se ha recibido del dron {addr}: {msg_length}")
        msg_length = int(msg_length)
        alias = conn.recv(msg_length).decode(FORMAT)
        print(f"Se ha recibido del dron {addr} el alias: {alias}")
        # pasamos el alias a la bbdd
        # leeremos de la bbdd el id y el token, y se lo devolveremos al dron
        id, token = create_Dron(alias)
        respuesta = str(id)+","+str(token)
        send(respuesta, conn)
    
def manejoAutDrones(numeroDrones):
    server.listen()
    print(f"AD_Registry escuchando en {SERVER}, para autenticar {numeroDrones} drones")
    while numeroDrones:
        conn, addr = server.accept()
        print(f"Se ha conectado el dron {addr}")
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except Exception as exc:
            print("Se ha cerrado la conexión inesperadamente")
            conn.close()
        if msg_length:
            print(f"Se ha recibido del dron {addr}: {msg_length}")
            msg_length = int(msg_length)
            id = conn.recv(msg_length).decode(FORMAT)
            print(f"Se ha recibido del dron {addr} el id: {id}")
            # generamos el token y se lo pasamos al dron
            token = setTokenDron(id)
            send(str(token), conn)



    
### Funciones del manejo de los drones ###

#---------------------------------------------#
    
### Funciones para el socket con el engine ###

def manejo_engine():
    server.listen()
    print(f"AD_Registry escuchando en  {SERVER}")
    print("Esperando que el engine le envie el mapa")
    conn, addr = server.accept()
    print(f"Se ha conectado el engine {addr}")
    try:
        msg_length = conn.recv(HEADER).decode(FORMAT)
    except Exception as exc:
        print("Se ha cerrado la conexión inesperadamente")
        conn.close()
    if msg_length:
        print(f"Se ha recibido del engine {addr}: {msg_length}")
        msg_length = int(msg_length)
        mapa = conn.recv(msg_length).decode(FORMAT)
        print(f"Se ha recibido del engine {addr} el mapa: {mapa}")
        return mapa

        # hacemos un timeout de 20 seg y comprobamos que el token del dron se ha borrado de la BBDD

### Funciones para el socket con el engine ###    

#---------------------------------------------#

### Funciones de la BBDD ###
    
def create_Dron(alias):
    conexion = sqlite3.connect("bd1.db")
    try:
        
        conexion.execute("insert into drones(alias) values ('"+alias+"')")
        #sacamos la id del dron que acabamos de crear
        cursor = conexion.execute("select id from drones where alias='"+alias+"'")
        #sacamos el id del dron
        id = cursor.fetchone()[0]
        token = id+1000
        #actualizamos el token del dron
        conexion.execute("update drones set token="+str(token)+" where alias='"+alias+"'")

        conexion.commit()
        print("Dron creado")

        return id, token
    except sqlite3.OperationalError:
        print("Error al crear el dron")
        conexion.close()

        return "Error", "Base de datos"
    
def deleteTokenDron(id):
    # hacemos un timeout de 20 seg y comprobamos que el token del dron se ha borrado de la BBDD
    time.sleep(20)
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("update drones set token=null where autenticado=false")
        conexion.commit()
        conexion.close()
    except:
        print("Error al borrar el token del dron")
        conexion.close()

def isTokenDronDeleted():
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("select token from drones")
        token = cursor.fetchone()[0]
        print(token)
        conexion.close()
        if(token == None):
            return True
        else:
            return False
    except:
        print("Error al obtener el token del dron")
        conexion.close()
        return "Error"
    
def getNumeroDronesBBDD():
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("select count(*) from drones")
        numeroDronesBBDD = cursor.fetchone()[0]
        conexion.close()
        return numeroDronesBBDD
    except:
        print("Error al obtener el numero de drones de la BBDD")
        conexion.close()
        return "Error"
        
def setTokenDron(id):
    tokenRandom = randint(1000,99999)
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("update drones set token="+str(tokenRandom)+" where id="+str(id))
        conexion.commit()
        cursor.execute("select token from drones where id="+str(id))
        token = cursor.fetchone()[0]
        conexion.close()
        return token
    except:
        print("Error al obtener el token del dron")
        conexion.close()
        return None
        
### Funciones de la BBDD ###
    
#---------------------------------------------#
    
### Funciones para el Mapa ###
    
def getNumeroDronesMapa(nombreMapa):
    with open ("AwD_figuras.json", "r") as archivo:
        datos = json.load(archivo)
        figuras = datos["figuras"]
        for elemento in datos:
            if(elemento["nombre"] == nombreMapa):
                return elemento["Drones"]
            


### Funciones para el Mapa ###
            
#---------------------------------------------#
    
### Funciones de sockets ###

def send(msg, server):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    server.send(send_length) 
    print("Enviando mensaje: ", message)
    server.send(message)


def registro_dron(numeroDrones):
    server.listen()
    print(f"AD_Registry escuchando en {SERVER}, para registrar {numeroDrones} drones")
    while numeroDrones:
        conn, addr = server.accept()
        thread = threading.Thread(target=manejo_dron, args=(conn, addr))
        thread.start()

### Funciones de sockets ###
        
#---------------------------------------------#
        
### Funciones de la API ###

# Funciones de la API
# Funcion de registro de dron
# Devuelve el token del dron y el id
@app.get("/registroDron")
def registroDron(alias: str):

    id, token = create_Dron(str(alias))

    print("Se ha registrado el dron: " + alias + " via API REST")
    return {"token": token, "id": id}

### Funciones de la API ###

#---------------------------------------------#

### Main ###

# Parametros de AD_Registry
# puerto de escucha
# ip y puerto de la bbdd (al no haber la vamos a omitir)
#La lista de argumentos cuenta la llamada al programa como sys.arv[0]
if(len(sys.argv) == 2):

    PORT = int(sys.argv[1])
    ADDR = (SERVER,PORT)


    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("AD_Registry iniciado")
    # Obtenemos el mapa que el engine va a procesar
    mapa = manejo_engine()
    numeroDrones = getNumeroDronesMapa(mapa)

    if(numeroDrones != None):
        # Abrimos el socket para registrar los drones
        registro_dron(numeroDrones)
        # borramos el token de los drones que no se han autenticado
        deleteTokenDron()
        if(isTokenDronDeleted()):
            print("Se han borrado los tokens de los drones que no se han autenticado")
        else:
            print("No se ha podido borrar los tokens de los drones")

    # controlamos el número de drones que se van a registrar
    while True:
        mapa = manejo_engine()
        numeroDrones = getNumeroDronesMapa(mapa)
        if getNumeroDronesBBDD() == numeroDrones:
            # abrimos socket para mandar token a los drones
            manejoAutDrones(numeroDrones)
            deleteTokenDron()
            if(isTokenDronDeleted()):
                print("Se han borrado los tokens de los drones que no se han autenticado")
            else:
                print("No se ha podido borrar los tokens de los drones")
        elif getNumeroDronesBBDD() < numeroDrones:
            print(f"Se necesitan {numeroDrones-getNumeroDronesBBDD()} drones más")
            # abrimos socket para registrar los drones
            registro_dron(numeroDrones-getNumeroDronesBBDD())
            manejoAutDrones(getNumeroDronesBBDD())
            deleteTokenDron()
            if(isTokenDronDeleted()):
                print("Se han borrado los tokens de los drones que no se han autenticado")
            else:
                print("No se ha podido borrar los tokens de los drones")
        elif getNumeroDronesBBDD() > numeroDrones:
            print(f"Hay {getNumeroDronesBBDD()} drones registrados, se necesitan {numeroDrones} drones")
            # abrimos socket para autenticar los drones
            manejoAutDrones(getNumeroDronesBBDD())
            deleteTokenDron()
            if(isTokenDronDeleted()):
                print("Se han borrado los tokens de los drones que no se han autenticado")
            else:
                print("No se ha podido borrar los tokens de los drones")


else:
    print("AD_Registry necesita estos argumentos <Puerto de escucha>")
