import socket
import threading
import time
import sys
import sqlite3
from fastapi import FastAPI

app = FastAPI()

HEADER = 64
SERVER = "localhost" #socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'

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
    
### Funciones de la BBDD ###
    
def deleteTokenDron(id):
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("update drones set token=null where id="+str(id))
        conexion.commit()
        conexion.close()
    except:
        print("Error al borrar el token del dron")
        conexion.close()
        
def getTokenDron(id):
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("select token from drones where id="+str(id))
        token = cursor.fetchone()[0]
        conexion.close()
        return token
    except:
        print("Error al obtener el token del dron")
        conexion.close()
        return "Error"
        
### Funciones de la BBDD ###

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
            print(f"Se ha recibido del dron {addr}: {msg_length}")
            msg_length = int(msg_length)
            alias = conn.recv(msg_length).decode(FORMAT)
            print(f"Se ha recibido del dron {addr} el alias: {alias}")
            # pasamos el alias a la bbdd
            # leeremos de la bbdd el id y el token, y se lo devolveremos al dron
            id, token = create_Dron(alias)
            respuesta = str(id)+","+str(token)
            send(respuesta, conn)

            # hacemos un timeout de 20 seg y comprobamos que el token del dron se ha borrado de la BBDD
            dronAutenticado = False
            while(not(dronAutenticado)):
                time.sleep(20)
                if(getTokenDron(id) != None):
                    print(f"El dron {alias} no se ha autenticado")
                    deleteTokenDron(id)
            
                    

def send(msg, server):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    server.send(send_length) 
    print("Enviando mensaje: ", message)
    server.send(message)


def registro_dron():
    server.listen()
    print(f"AD_Registry escuchando en  {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=manejo_dron, args=(conn, addr))
        thread.start()

def getDrones():
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("select id, alias from drones")
        drones = cursor.fetchall()
        conexion.close()
    except:
        print("Error al obtener los drones")
        conexion.close()
        return "Error"
    listaDrones = []
    for dron in drones:
        listaDrones.append([dron[0], dron[1]])
    return listaDrones

def updateIdsDrones(listaDrones):
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        it = 1
        for dron in listaDrones:
            cursor.execute("update drones set id="+ str(it) +" where alias='"+dron[1]+"'")
            it = it + 1
        conexion.commit()
        conexion.close()
    except:
        print("Error al actualizar los ids de los drones")
        conexion.close()
        return "Error"


# Funciones de la API REST
# Funcion de registro de dron
# Devuelve el token del dron y el id
@app.get("/registroDron")
def registroDron(alias: str):

    id, token = create_Dron(str(alias))

    print("Se ha registrado el dron: " + alias + " via API REST")
    return {"token": token, "id": id}



# main
# Parametros de AD_Registry
# puerto de escucha
# ip y puerto de la bbdd (al no haber la vamos a omitir)
#La lista de argumentos cuenta la llamada al programa como sys.arv[0]
if(len(sys.argv) == 2):

    PORT = int(sys.argv[1])
    ADDR = (SERVER,PORT)


    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    registro_dron()
    print("Fuera del hilo")


else:
    print("AD_Registry necesita estos argumentos <Puerto de escucha>")
