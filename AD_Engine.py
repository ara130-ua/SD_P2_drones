import base64
import datetime
import random
import secrets
import socket
import ssl
import subprocess
import threading
import sys
import sqlite3
import time
import json
import os
from kafka import KafkaProducer
from json import dumps
from json import loads
from kafka import KafkaConsumer
import pygame
import requests
from fastapi import FastAPI
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

app = FastAPI()

HEADER = 64
FORMAT = 'utf-8'
SERVER = "localhost" #socket.gethostbyname(socket.gethostname())

#----------------------------------------------------------#

### Funciones que manejan kafka ###

def productor(mapa):

    print("Mapa enviado: " + str(mapa))

    mapa = encrypt_message(mapa,contraseñaKafka)
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=[ADDR_BROKER])
    
    print("Mapa encriptado enviado: " + str(mapa))
    producer.send('mapas1-topic', value=mapa)
    time.sleep(1)

def consumidor(listaDronMov, num_drones):
    consumer = KafkaConsumer(
        'movimientos1-topic',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='engine',
        value_deserializer=lambda m: loads(m.decode('utf-8')),
        bootstrap_servers=[ADDR_BROKER]) 

    finalizados = 0
    enBase = 0
    volverBase = False

    for m in consumer:

        m = decrypt_message(m.value, contraseñaKafka)
        
        if(setPosEstDrones(m[1], m[0], m[2][0], m[2][1])):
            print("Posicion y estado del dron " + str(m[1]) + " actualizados correctamente")
        actualizarMovimientos(listaDronMov, m) # podemos eliminarlo

        if(m[0] == 'G'):
            actualizarMovimientos(listaDronMov, m, True) # podemos eliminarlo
            finalizados = finalizados + 1
            print("Dron " + str(m[1]) + " finalizado")
            print(listaDronMov)

        if(finalizados == num_drones):
            productor(getPosEstDrones())
            productor("FIGURA COMPLETADA")
            finalizados = 0
            volverBase = True
            
        pygameMapa(crearMapa(listaDronMov))
        productor(getPosEstDrones())

        if(volverBase==True):
            enBase = 0
            for dron in listaDronMov: # cambiar por getPosEstDrones()
                if(dron[2] == (1,1)):
                    enBase = enBase + 1
            if(enBase == num_drones):
                return True

def espectaculo(listaMapa, numMaxDrones):
    productor(listaMapa)
    listaDronMovInicial = []
    for dronMov in listaMapa:
        listaDronMovInicial.append(['R', dronMov[0], (1,1)])
    
    if(numMaxDrones < len(listaMapa)):
        print("No hay suficientes drones para realizar el espectaculo")
    else:
        if(consumidor(listaDronMovInicial, len(listaMapa))):
            print("Figura finalizada")

        delete_topic1 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --delete --topic mapas1-topic --bootstrap-server " + ADDR_BROKER + " && exit; exec bash'"
        delete_topic2 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --delete --topic movimientos1-topic --bootstrap-server " + ADDR_BROKER + " && exit; exec bash'"
        subprocess.run(delete_topic2, shell=True) 
        subprocess.run(delete_topic1, shell=True)
        # si hace algo raro time.sleep(5)



### Funciones que manejan kafka ###
        
#----------------------------------------------------------#

### Funcion para encriptar/desencriptar los mensajes de kafka ###

def encrypt_message(message, key):
    cipher = Cipher(algorithms.AES(key), modes.CFB(b'\x00' * 16), backend=default_backend())
    
    if type(message) is list:
        message = ' '.join(map(str, message))

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode()) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode()

def decrypt_message(ciphertext, key):

    ciphertext = base64.b64decode(ciphertext)
    print("Ciphertext: " + str(ciphertext) + " con tipo de dato: " + str(type(ciphertext)))

    cipher = Cipher(algorithms.AES(key), modes.CFB(b'\x00' * 16), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

    mensaje = decrypted_message.decode()
    print("Mensaje desencriptado: " + str(mensaje) + " con tipo de dato: " + str(type(mensaje)))

    return convertir_movimiento_strTOlist(mensaje)

def convertir_movimiento_strTOlist(cadena):
    lista = []
    estado = cadena[2]
    id = cadena[7]

    if cadena[13].isdigit():
        posx = cadena[12] + cadena[13]
        if cadena[17].isdigit():
            posy = cadena[16] + cadena[17]
        else:
            posy = cadena[16]
    else:
        posx = cadena[12]
        if cadena[16].isdigit():
            posy = cadena[15] + cadena[16]
        else:
            posy = cadena[15]

    tupla = (int(posx), int(posy))
    lista.append(str(estado))
    lista.append(str(id))
    lista.append(tupla)
    return lista

### Funcion para encriptar/desencriptar los mensajes de kafka ###

#----------------------------------------------------------#

### Funciones de servidor ###

def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    try:
        client.send(send_length)
        print("Enviando mensaje: ", message)
        client.send(message)
    except Exception as exc:
        print("Se ha cerrado la conexión inesperadamente")
        client.close()

def receive(client):
    try:
        msg_length = client.recv(HEADER).decode(FORMAT)
        if msg_length:
            print(f"Se ha recibido algo {msg_length}")
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(FORMAT)
            print(f"Se ha recibido: {msg}")
            return msg
        else:
            #print("No se ha recibido nada")
            return None
    except:
        print("No se ha encontrado conexión o se ha caido")
        return None

    
### Funciones de servidor ###

#----------------------------------------------------------#

### Funciones de BBDD ###

def climaBBDD(datos_clima):
    tuplaClima = eval(datos_clima)
    nombreCiudad = tuplaClima[0]
    temperatura = tuplaClima[1]
    conexion = sqlite3.connect("bd1.db")

    try:
        # comprobar los tipos de datos de nombre y de temperatura
        conexion.execute("insert into weather (nombre, temperatura) values ('"+nombreCiudad+"',"+str(temperatura)+")")
        conexion.commit()
        conexion.close()
        return("ciudad añadida a la BBDD")
    except sqlite3.OperationalError:
        print("Error al añadir la ciudad a la BBDD")
        conexion.close()
        return "Error", "Base de datos"
    

def leerUltFilaClima():
    # nos conectamos a la BBDD y leemos la última fila
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("select * from weather order by id desc limit 1")
        ultimaFila = cursor.fetchone()
        conexion.close()
        # convertimos los datos a una tupla y la devolvemos
        datosClimaActual = ultimaFila[1], ultimaFila[2]
    except sqlite3.OperationalError:
        print("Error al leer la última fila de la BBDD")
        conexion.close()
        return None
    return datosClimaActual

    # no está testado #
def leerTokenDron(id):
    # nos conectamos a la BBDD y leemos el token del dron con la id recibida
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("select token from drones where id="+str(id))
        token = cursor.fetchone()[0]
        conexion.close()
    except sqlite3.OperationalError:
        print("Error al leer el token del dron")
        conexion.close()
        return None
    # inicializamos las posiciones y el estado del dron y devolvemos el token
    setPosInicialDron(id)
    return token

def setPosInicialDron(id):
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("update drones set estado='R', coordenadaX=1, coordenadaY=1 where id="+str(id))
        conexion.commit()
        conexion.close()
    except:
        print("Error al inicializar la posición y el estado del dron")
        conexion.close()

def getPosEstDrones():
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("select estado, id, coordenadaX, coordenadaY from drones")
        infoDrones = cursor.fetchall()
        conexion.close()
    except:
        print("Error al leer la posición y el estado de los drones")
        conexion.close()
        return None
    
    # devolvemos la información de los drones
    listaDrones = []
    for dron in infoDrones:
        listaDrones.append([dron[0], dron[1], (dron[2], dron[3])])
    return listaDrones

def setPosEstDrones(id, estado, coordenadaX, coordenadaY):
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("update drones set estado='"+estado+"', coordenadaX="+str(coordenadaX)+", coordenadaY="+str(coordenadaY)+" where id="+str(id))
        conexion.commit()
        conexion.close()
    except:
        print("Error al actualizar la posición y el estado de los drones")
        conexion.close()
        return False
    
    # devolvemos la información de los drones
    return True

def setEstAutenticadoDron(id, estado):
    
    if(estado):
        estAux = "true"
    else:
        estAux = "false"    
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("update drones set autenticado='"+estAux+"' where id="+str(id))
        conexion.commit()
        conexion.close()
    except:
        print("Error al actualizar el estado de autenticado del dron")
        conexion.close()


def deleteTokenDron(id):
    # nos conectamos a la BBDD
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("update drones set token=null where id="+str(id))
        conexion.commit()
        conexion.close()
        print(f"Token del dron {id} borrado")
    except:
        print("Error al borrar el token del dron")
        conexion.close()
        
### Funciones de BBDD ###

#----------------------------------------------------------#

### Funciones que manejan la conexion con el AD_Wheather ###

def conexionClima():

    try:
        thread = threading.Thread(target=manejoClima, args=())
        thread.start()
    except:
        print("Error al crear el hilo")
        
    
def manejoClima():
    # sacaremos del fichero de texto ciudades.txt una ciudad aleatoria
    while True:
        try:
            # leemos el fichero de texto
            with open('ciudades.txt', 'r') as archivo:
                archivo = archivo.read()
                # separamos las ciudades por el salto de linea
                ciudades = archivo.split("\n")
                # elegimos una ciudad aleatoria
                ciudad = ciudades[random.randint(0, len(ciudades)-1)]
                split = ciudad.split(",")
                ciudad = split[0]
                pais = split[1]
                # llamamos a la api de openweather
                temp, name = openweather(ciudad, pais)

                temp = round(temp, 2)
            
            print("La temperatura en", name, "es de", temp,"ºC.")

            if(temp < 0):
                productor("CLIMA ADVERSO")

            time.sleep(15)
        except:
            print("Error al conectar con Openweather")
            
        

def openweather(ciudad, pais=''):
    url = 'https://api.openweathermap.org/data/2.5/weather?q='+ ciudad +','+ pais +'&appid=ab5fabb14bb7f9339114ee722d636a74'
    r = requests.get(url)
    j = r.json()
    temp = j['main']['temp']
    temp = temp - 273.15
    name = j['name']
    return temp, name

### Nueva funcion con OpenWeather ###

#----------------------------------------------------------#

### Funciones que manejan la conexion con los drones ###

def manejoTokenDrones(conn, addr):
    print(f"Se ha conectado el dron {addr}")

    tokenDron = receive(conn)
    if tokenDron:
        id, token = tokenDron.split(",")
        print(f"Se ha recibido del dron {addr} con id: {id} el token: {token}")
        # leemos de la base de datos el token del dron con la id recibida
        if(str(leerTokenDron(id)) == token):
            send("OK", conn)
            print("Token correcto")
            # funcion para actualizar el estado del dron a autenticado y eliminar el token dado por registry
            setEstAutenticadoDron(id, True)
            deleteTokenDron(id)
            return True
        else:
            send("KO", conn)
            print("Token incorrecto")
            setEstAutenticadoDron(id, False)
            return False

                
def autentificacionDrones(numDrones, numDronesFigura):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR_ENGINE) 
    print(f"AD_Engine escuchando en  {ADDR_ENGINE}")
    terminados = 0
    for i in range(numDrones):
        server.listen()
        conn, addr = server.accept()
        if manejoTokenDrones(conn, addr):
            terminados = terminados + 1
    # conexion con el número de drones que vayan a participar en la figura
    # en el caso de que no se conecten todos, se cancela el espectaculo
    # comprobar que todos los drones se han conectado
    if(terminados == numDronesFigura):
        print("Todos los drones se han conectado")
        return True
    


### Funciones que manejan la conexion con los drones ###

#----------------------------------------------------------#

### Funciones que manejan el fichero de drones y el mapa ###

def manejoFichero():
   
    with open('AwD_figuras.json', 'r') as archivo:
        # cargamos el archivo json
        json_data = json.load(archivo)

        figuras = json_data["figuras"]
        lista_inicial = []
        # Iteramos sobre figuras
        for figura in figuras:

            info_dron = []
            lista_figura = []

            lista_figura.append(figura["Nombre"])
            drones = figura["Drones"]
            bucleFigura = True
            # Utilizamos el booleano para que no se hagan duplicados
            for dron in drones:
                if(bucleFigura):
                    dron_id = dron["ID"]
                    pos_x, pos_y = map(int, dron["POS"].split(","))
                    if dron_id == 1 and len(info_dron) > 1:
                        bucleFigura = False
                    else:
                        info_dron.append((dron_id, (pos_x, pos_y)))

            lista_figura.append(info_dron)
            lista_inicial.append(lista_figura)
            
    return(lista_inicial)

def actualizarMovimientos(listaDronMov, dronMov, isFinalizado=False):
    for dron in listaDronMov:
        if(dron[1] == int(dronMov[1])):
            if(isFinalizado ):
                dron[0] = 'G'
            else:
                dron[0] = 'R'

            dron[2] = (dronMov[2][0], dronMov[2][1])
            return listaDronMov
        
# listaDronMovActuales = [['R', ID, (X,Y)], ['R',ID,(X,Y)], ...]
def crearMapa(listaDronMovActuales):
    mapaBytes = [[0 for _ in range(20)] for _ in range(20)]
    listaMapa = []
  
    for coordX in mapaBytes:
        listaCoordX = []
        for coordY in coordX:
            listaCoordX.append(('E', 0))
        listaMapa.append(listaCoordX)
        
        
    for dron in listaDronMovActuales:
        listaMapa = actualizaMapa(listaMapa, dron)

    return(listaMapa)

# dronMov = ['R',ID,(X,Y)]
def actualizaMapa(listaMapa, dronMov):
    estado = dronMov[0]
    Id = dronMov[1]
    movimiento = (int(dronMov[2][0])-1, int(dronMov[2][1])-1)
    # metemos el estado y el id en la posicion del mapa
    listaMapa[movimiento[0]][movimiento[1]] = (estado, Id)
    return listaMapa
       

def stringMapa(listaMapa):
    strMapa = ""
    for fila in listaMapa:
        strMapa = strMapa + "| "
        for elemento in fila:
            strMapa = strMapa + "[" + elemento[0] + "," + str(elemento[1]) + "] "
        strMapa = strMapa + "|\n"

    return strMapa

### Funciones que manejan el fichero de drones y el mapa ###


#----------------------------------------------------#

### Funciones para el manejo de pygame ###


# Función para dibujar el mapa de bits
def draw_grid(screen):
    for x in range(0, WINDOW_SIZE[0], GRID_SIZE):
        pygame.draw.line(screen, (255, 255, 255), (x, 0), (x, WINDOW_SIZE[1]))
    for y in range(0, WINDOW_SIZE[1], GRID_SIZE):
        pygame.draw.line(screen, (255, 255, 255), (0, y), (WINDOW_SIZE[0], y))


def pygameMapa(listaMapa):

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))
    draw_grid(screen)


    
    #listaMapa tiene el siguiente formato: [[(color, id), (color, id), ...], [(color, id), (color, id), ...], ...
    for y, fila in enumerate(listaMapa):
        for x, elemento in enumerate(fila):
            color = elemento[0]

            if color == 'G':
                drone_color = (0, 255, 0)  # Verde
                drone_rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, DRONE_SIZE, DRONE_SIZE)
                pygame.draw.rect(screen, drone_color, drone_rect)
            elif color == 'R':
                drone_color = (255, 0, 0)  # Rojo
                drone_rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, DRONE_SIZE, DRONE_SIZE)
                pygame.draw.rect(screen, drone_color, drone_rect)

    pygame.display.update()


### Funciones para el manejo de pygame ###


#----------------------------------------------------------#

### Funciones para la autenticación de los drones via API ###

# variable global para controlar el número de drones autenticados

@app.get("/autenticacionDron")
def autenticacionDronAPI(id: int, token: str):
    global terminados 
    
    # verificamos el token en la BBDD
    if(str(leerTokenDron(id)) == token):
        print("OK")
        print("Token correcto")
        print("El dron con id "+ str(id) + " se ha autenticado correctamente.")
        # funcion para actualizar el estado del dron a autenticado y eliminar el token dado por registry
        setEstAutenticadoDron(id, True)
        deleteTokenDron(id)
        return {"mensaje": "Token correcto"}
    else:
        print("KO")
        print("Token incorrecto")
        setEstAutenticadoDron(id, False)
        print("El dron con id "+ str(id) + " no se ha podido autenticar.")
        return {"mensaje": "Token incorrecto"}

def checkAutenticados():
    # nos conectamos a la BBDD y devolvemos el numero de drones que estan autenticados (autenticado = true)
    conexion = sqlite3.connect("bd1.db")
    try:
        cursor = conexion.cursor()
        cursor.execute("select count(*) from drones where autenticado='true'")
        autenticados = cursor.fetchone()[0]
        print("Hay " + str(autenticados) + " drones autenticados")
        conexion.close()
    except:
        print("Error al leer el numero de drones autenticados")
        conexion.close()
        return None
    # devolvemos el numero de drones autenticados
    return autenticados

def checkDronesAutenticados(numDronesFigura):

    while int(checkAutenticados()) <= numDronesFigura:
        if(int(checkAutenticados()) == numDronesFigura):
            print("Todos los drones se han autenticado")
            return True
        
        time.sleep(1)


### Funciones para la autenticación de los drones via API ###

#----------------------------------------------------------#
        
### Funciones para compartir la contraseña de Kafka ###
        
def generar_clave_simetrica(longitud):
    # Genera una clave simétrica aleatoria en formato binario
    clave_binaria = secrets.token_bytes(longitud)
    return clave_binaria

def shareKafkaPassword(contraseñaKafka):
    # Funcion que maneja cada conexion
    def deal_with_client(connstream, completados):
        data = connstream.recv(1024)
        # empty data means the client is finished with us    
        print('Recibido ', repr(data))
        completados = completados + 1
        print("Contraseña enviada a ", completados, " drones")
        #data = connstream.recv(1024)
        print("Enviando contraseña de kafka", contraseñaKafka)     
        connstream.send(contraseñaKafka)

        return completados

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # Se carga el certificado con clave pública y privada
    #context.load_cert_chain(certfile="mycertfile", keyfile="mykeyfile")
    context.load_cert_chain(cert, cert)

    bindsocket = socket.socket()
    bindsocket.bind((SERVER, PORT_ENGINE))
    bindsocket.listen(5)


    print('Escuchando en ',SERVER, PORT_ENGINE, ' para comparir la clave')

    completados = 0

    while completados < numMaxDrones:
        newsocket, fromaddr = bindsocket.accept()
        connstream = context.wrap_socket(newsocket, server_side=True)
        print('Conexion recibida')
        try:
            completados=deal_with_client(connstream, completados)
        except ssl.SSLEOFError:
            print("El cliente cerró la conexión")
        finally:
            try:
                connstream.shutdown(socket.SHUT_RDWR)
                connstream.close()
            except OSError:
                print("El socket ya está cerrado")


### Funciones para compartir la contraseña de Kafka ###

#----------------------------------------------------------#
                
### Funciones para el registro de eventos en BBDD ###

# Para auditar un evento, llamamos a la siguiente funcion:
def auditar_evento(accion, ip_origen, descripcion):
    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.datetime.now()

    # Crear una entrada de registro estructurada
    entrada_registro = {
        'fecha_hora': fecha_hora_actual.strftime('%Y-%m-%d %H:%M:%S'),
        'accion': accion,
        'origen': ip_origen,
        'descripcion': descripcion
    }

    # Agregar la entrada de registro a un archivo de registro o imprimir en la consola
    registrar_evento(entrada_registro)    

def registrar_evento(entrada_registro):
    # Conectar a la base de datos SQLite
    conexion = sqlite3.connect('bd1.db')
    cursor = conexion.cursor()

    # Insertar la entrada de registro en la base de datos
    cursor.execute('''
        INSERT INTO registro_auditoria (fecha_hora, accion, origen, descripcion)
        VALUES (?, ?, ?, ?)
    ''', (entrada_registro['fecha_hora'], 
          entrada_registro['accion'], entrada_registro['origen'], entrada_registro['descripcion']))

    # Confirmar los cambios y cerrar la conexión
    conexion.commit()
    conexion.close()        

### Funciones para el registro de eventos en BBDD ###

#----------------------------------------------------------#
                
def removeDronesBBDD():
    os.system("rm bd1.db")
    os.system("python BBDD.py")
            

#usaremos 6 argumentos, la BBDD no necesita de conexion
# número máximo de drones
# puerto de escucha del AD_Engine
# puerto del AD_Engine
# IP y puerto del Broker
# IP y puerto del AD_Wheather
if  (len(sys.argv) == 7):
    
    # zona de argumentos
    
    numMaxDrones = int(sys.argv[2])
    PORT_ENGINE = int(sys.argv[1])
    ADDR_ENGINE = (SERVER, PORT_ENGINE)

    IP_BROKER = str(sys.argv[3])
    PORT_BROKER = sys.argv[4]

    ADDR_BROKER = str(IP_BROKER) + ":" + str(PORT_BROKER)

    IP_WEATHER = sys.argv[5]
    PORT_WEATHER = int(sys.argv[6])
    ADDR_WEATHER = (IP_WEATHER, PORT_WEATHER)

    cert = 'certServ.pem'

    ############################ PYGAME ############################

    # export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6

    # Inicializa Pygame
    pygame.init()

    # Definir constantes
    WINDOW_SIZE = (400, 400)
    GRID_SIZE = 20
    DRONE_SIZE = 20

    # Crea la ventana de juego
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Mapa impreso desde el AD_Engine")

    ################################################################

    print("Bienvenido al AD_Engine")
    programaActiveBool = True
    figuras = manejoFichero()

    contraseñaKafka = generar_clave_simetrica(32)
    
    # Bucle de menú principal
    while(programaActiveBool):
        print("Elige una opción:")
        print("1. Ver figuras disponibles")
        print("2. Salir")
        opcion = input()

        if(opcion == "1"):
            os.system("clear")
            # bucle de figuras
            programaFigurasBool = True
            while(programaFigurasBool):
                iterador = 1
                print("Selecciona una figura: ")
                for figura in figuras:
                    print(str(iterador) + ". " + figura[0])
                    iterador = iterador + 1
                print(str(iterador) + ". Salir")
                opcionFigura = input()
                
                try:
                    if(int(opcionFigura) < iterador and int(opcionFigura) > 0):
                        os.system("clear")
                        opcFiguraSelecBool = True
                        listaMapa = figuras[int(opcionFigura)-1][1]
                        while(opcFiguraSelecBool):
                            print("Has seleccionado la figura: " + str(figuras[int(opcionFigura)-1][0]))
                            print("Elige una opción:")
                            print("1. Ver la figura final")
                            print("2. Ver la figura simplificada")
                            print("3. Comenzar el espectaculo directamente")
                            print("4. Salir")
                            opcionFiguraSelec = input()

                            if(opcionFiguraSelec == "1"):
                                os.system("clear")
                                print("Mostrando figura final")
                                pygameMapa(crearMapa(listaMapa))
                                # mostrar figura final
                            elif(opcionFiguraSelec == "2"):
                                os.system("clear")
                                print("Mostrando figura simplificada")
                                # mostrar figura simplificada
                                print(listaMapa)
                            elif(opcionFiguraSelec == "3"):
                                os.system("clear")
                                print("Comenzando espectaculo")
                                # comenzar espectaculo
                        
                                # Autenticación de los drones
                                if( checkDronesAutenticados(len(listaMapa)) ):
                                    # Lanzamos el socket para compartir la contraseña de kafka
                                    shareKafkaPassword(contraseñaKafka)

                                    print("Conectando con  Openweather...")
                                    conexionClima()

                                    espectaculo(listaMapa, numMaxDrones)

                                    
                                    removeDronesBBDD()
                                    # Hacer un bucle que cada x tiempo lea la BBDD y si hay un cambio en la temperatura (negativo)
                                    # llama a la función de vuelta a base, que envia a los drones a la posicion (1,1)
                                

                                opcFiguraSelecBool = False
                            elif(opcionFiguraSelec == "4"):
                                os.system("clear")
                                print("Saliendo de la figura seleccionada")
                                opcFiguraSelecBool = False
                            else:
                                os.system("clear")
                                print("Opción no válida (a)")
                
                    elif(opcionFigura == str(iterador)):
                        os.system("clear")
                        print("Saliendo de la selección de figuras")
                        programaFigurasBool = False
                    else:
                        os.system("clear")
                        print("Opción no válida (b)")
                except ValueError:
                    os.system("clear")
                    print("Opción no válida (c)" + str(ValueError))

        elif(opcion == "2"):
            os.system("clear")
            print("Saliendo del programa")
            programaActiveBool = False
        else:
            os.system("clear")
            print("Opción no válida (d)")


    
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto_engine> <Max_Drones> <IP_Broker> <Puerto_Broker> <IP_Weather> <Puerto_Weather>")
