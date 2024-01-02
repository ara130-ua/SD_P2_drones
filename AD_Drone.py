import ast
import base64
import re
import socket
import ssl
import sys
from kafka import KafkaProducer
from kafka import KafkaConsumer
from json import loads
from json import dumps
import time
import pygame
import signal
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import requests


HEADER = 64
FORMAT = 'utf-8'

#----------------------------------------------------#


### Funciones para el manejo de kafka ###

#devuelve todos los mapas segun llegan al topic
def consumidor_mapas(id_dron, pos_actual, pos_final):
    consumer = KafkaConsumer(
        'mapas1-topic',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id = id_dron,
        value_deserializer=lambda m: loads(m.decode('utf-8')),
        bootstrap_servers=[ADDR_KAFKA])
  

    #LEER
    # hay que tener en cuenta que el producor de movimientos depende de si el mapa esta actualizado o no, esto implica que si al consumir un mapa 
    # mandamos inmediatamente un movimiento y leemos, puede que no demos tiempo a que el productor de movimientos actualice el mapa, por lo que
    # el consumidor de mapas no detectara que el mapa esta actualizado y mandara un movimiento REPETIDO.

    
    #Comprobar en la segunda figura
    primerConsumidorBool = True
    figuraCompleta = False

    #signal.signal(signal.SIGALRM, handle_alarm)
    
    for m in consumer:
        print("Recibido mapa en el consumidor de mapas: " + str(m.value) + "con tipo de dato: " + str(type(m.value)))
        
        mensaje = decrypt_message(m.value, contraseñaKafka)
        
        print("Recibido mapa: " + str(mensaje))
        
        if((pos_actual[0], pos_actual[1]) == (pos_final[0], pos_final[1]) and figuraCompleta == True):
            return True

        if(mensaje == "FIGURA COMPLETADA" or mensaje == "CLIMA ADVERSO"):
            pos_final = (1,1)
            figuraCompleta = True
            print("Vuelvo a casa")
            pos_actual = run(pos_actual, pos_final)
            listaDronMov = ['R', id_dron, pos_actual]
            productor(listaDronMov)
            continue

        if(primerConsumidorBool == False and (pos_actual[0], pos_actual[1]) == (pos_final[0], pos_final[1]) and listaDronMov[0] != 'G'):
            listaDronMov[0] = 'G'
            print("El dron con id: " + str(id_dron) + " ha llegado a su destino")
            productor(listaDronMov)
            #print(stringMapa(crearMapa(mensaje)))
            pygameMapa(crearMapa(mensaje))


        elif(primerConsumidorBool == False and isMapaActualizado(mensaje, pos_actual, id_dron) and (pos_actual[0], pos_actual[1]) != (pos_final[0], pos_final[1])):
            # crear y pintar el mapa
            #print(stringMapa(crearMapa(mensaje)))
            pygameMapa(crearMapa(mensaje))

            pos_actual = run(pos_actual, pos_final)
            print("Posicion actualizada -->" + str(pos_actual))
            listaDronMov[2] = pos_actual
            # ['R', ID, (X,Y)]
            productor(listaDronMov)

        elif(primerConsumidorBool):
            print("Saca la posicion final de :" + str(mensaje)+ " con tipo de dato: " + str(type(mensaje)) + " y el id del dron: " + str(id_dron))
            pos_final = saca_pos_final(mensaje, int(id_dron))
            print("La posicion a la que tengo que ir: "+ str(pos_final))
            pos_actual = run(pos_actual, pos_final)
            listaDronMov = ['R', id_dron, pos_actual]
            productor(listaDronMov)
            primerConsumidorBool = False
        else:
            #print(stringMapa(crearMapa(mensaje)))
            pygameMapa(crearMapa(mensaje))

        print(listaDronMov)
            
            
#manda los movimientos al topic de los moviemtos
def productor(movimiento):
    movimiento = encrypt_message(movimiento, contraseñaKafka)
    producer = KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=[ADDR_KAFKA])

    producer.send("movimientos1-topic", value=movimiento)
    time.sleep(1)
        
### Funciones para el manejo de kafka ###

#----------------------------------------------------#

# Funciones para encriptar y desencriptar mensajes
    
def encrypt_message(message, key):

    if(type(message) == list):
        message = str(message)

    cipher = Cipher(algorithms.AES(key), modes.CFB(b'\x00' * 16), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode()) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode()

# Funcion modificada para poder desencriptar listas
def decrypt_message(ciphertext, key):
    
    ciphertext = base64.b64decode(ciphertext)
    print("Ciphertext: " + str(ciphertext) + " con tipo de dato: " + str(type(ciphertext)))

    cipher = Cipher(algorithms.AES(key), modes.CFB(b'\x00' * 16), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()
    
    mensaje = decrypted_message.decode()
    
    print("Mensaje desencriptado: " + str(mensaje) + " con tipo de dato: " + str(type(mensaje)))
    
    return convertir_cadenas_a_lista(mensaje)

def convertir_cadenas_a_lista(cadenas):
    # Recibe una cadena de texto con el formato: "(1, (5, 5)) (2, (5, 15)) (3, (10, 5)) (4, (10, 15))"
    # Devuelve una lista con el formato: [(1, (5, 5)), (2, (5, 15)), (3, (10, 5)), (4, (10, 15))]
    lista = []
    num = 1

    if(cadenas[0] == "("):
        for i, elemento in enumerate(cadenas):
            if elemento == "(" and cadenas[i+1] == str(num):
                id = cadenas[i+1]

                if cadenas[i+6].isdigit():
                    posx = cadenas[i+5] + cadenas[i+6]
                    if cadenas[i+10].isdigit():
                        posy = cadenas[i+9] + cadenas[i+10]
                    else:
                        posy = cadenas[i+9]
                else:
                    posx = cadenas[i+5]
                    if cadenas[i+9].isdigit():
                        posy = cadenas[i+8] + cadenas[i+9]
                    else:
                        posy = cadenas[i+8]

                tuple = (int(posx), int(posy))
                tupletuple = (int(id), tuple)
                lista.append(tupletuple)
                num += 1

    elif(cadenas[0] == "["):
        
        for i, elemento in enumerate(cadenas):
            listaaux=[]
            if elemento == "[":
                estado = cadenas[i+2]
                id = cadenas[i+6]

                if cadenas[i+11].isdigit():
                    posx = cadenas[i+10] + cadenas[i+11]
                    if cadenas[i+15].isdigit():
                        posy = cadenas[i+14] + cadenas[i+15]
                    else:
                        posy = cadenas[i+14]
                else:
                    posx = cadenas[i+10]
                    if cadenas[i+14].isdigit():
                        posy = cadenas[i+13] + cadenas[i+14]
                    else:
                        posy = cadenas[i+13]

                tupla = (int(posx), int(posy))
                listaaux.append(str(estado))
                listaaux.append(int(id))
                listaaux.append(tupla)
                lista.append(listaaux)
    else:
        return cadenas
        
    return lista

# Funciones para encriptar y desencriptar mensajes

#----------------------------------------------------#

### Funciones para el manejo de pygame ###


# Función para dibujar el mapa de bits
def draw_grid():
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
    draw_grid()


    
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

#----------------------------------------------------#

### Funciones para el manejo de movimientos ###

def run(pos_actual, pos_final):
    #realiza un movimiento en base al mapa y lo manda a la cola de mapas
    if(pos_actual is None or pos_final is None):
        pos_actual = (0,0)
        pos_final = (0,0)

    posInt_X = pos_actual[0]
    posInt_Y = pos_actual[1]

    if(pos_actual[0] < pos_final[0]):
        posInt_X = pos_actual[0]+1

    if(pos_actual[1] < pos_final[1]):
        posInt_Y = pos_actual[1]+1

    if(pos_actual[0] > pos_final[0]):
        posInt_X = pos_actual[0]-1

    if(pos_actual[1] > pos_final[1]):
        posInt_Y = pos_actual[1]-1

    return (posInt_X, posInt_Y)

def saca_pos_final(listaFigura, id_dron):
    #saca la posicion final del mapa
    #el mapa tiene que tener el siguiente formato: "id_dron-posX-posY#id_dron-posX-posY#..."
    print("saca pos final: " + str(listaFigura))

    for dron in listaFigura:
        if(dron[0] == id_dron):
            return dron[1]

### Funciones para el manejo de movimientos ###

#----------------------------------------------------#

### Funciones para el manejo de mapas ###

def isMapaActualizado(listaDronMov, pos_actual,id_dron):

    for dronMov in listaDronMov:
        if(dronMov[1] == int(id_dron) and (dronMov[2][0], dronMov[2][1]) == pos_actual):
            return True
    return False

def stringMapa(listaMapa):
    strMapa = ""
    for fila in listaMapa:
        strMapa = strMapa + "| "
        for elemento in fila:
            strMapa = strMapa + "[" + elemento[0] + "," + str(elemento[1]) + "] "
        strMapa = strMapa + "|\n"

    return strMapa

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
    listaMapa[movimiento[0]][movimiento[1]] = (estado, Id)
    return listaMapa


### Funciones para el manejo de mapas ###
        
#----------------------------------------------------#

### Funciones de conexión con los módulos ###

# conexión con el módulo AD_Registry para darse de alta en el sistema

def dronRegistry(ip_reg, puerto_reg, alias, primeraVez):
    
    ADDR = (str(ip_reg), int(puerto_reg))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        print(f"Se ha establecido conexión en [{ADDR}]")
        send(alias, client)
        message = receive(client)
        # en la segunda vuelta únicamente se recibe el token
        if primeraVez:
            id, token = message.split(",")
            return id, token
        else:
            return message
    except Exception as exc:
        return None, None

# conexión con el módulo AD_Engine para darse de alta en el espectaculo
def dronEngine(ip_eng, puerto_eng, id, token):
    try:
        ADDR = (str(ip_eng), int(puerto_eng))

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        print(f"Se ha establecido conexión en [{ADDR}]")
        send(str(id)+","+str(token), client)
        message = receive(client)
        if message == "OK":
            return True
        else:
            return False
    except Exception as exc:
        print("No se ha podido conectar con el engine: " + str(exc))
        return False

    
### Funciones de conexión con los módulos ###

#----------------------------------------------------#

### Funciones de send y receive ###

def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    print("Enviando mensaje: ", send_length)
    client.send(send_length)
    print("Enviando mensaje: ", message)
    client.send(message)
    
# este método solo se usa con el registry ya que le da un formato al mensaje
def receive(client):
    try:
        msg_length = client.recv(HEADER).decode(FORMAT)
    except Exception as exc:
        print("Se ha cerrado la conexión inesperadamente")
        client.close()
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        print(f"Se ha recibido del servidor: {msg}")
        return msg
    else:
        print("No se ha recibido nada del servidor")
        return None
    
    
### Funciones de send y receive ###

#----------------------------------------------------#

### Funciones de conexion via API REST ###

def dronRegistryAPI(alias):
    try:
        response = requests.get("https://127.0.0.1:8000/registroDron?alias="+alias, verify="certificado-firmado.crt")
        if(response.status_code == 200):
            print("Se ha conectado correctamente al registry")
            json = response.json()
            id, token = json['id'], json['token']
            return id, token
        else:
            print("No se ha podido conectar al registry")
            return None
    except Exception as exc:
        print("No se ha podido conectar al registry por API ERROR: " + str(exc))
        return None

### Funciones de conexion via API REST ###

#----------------------------------------------------#

### Menu Registry ###

def menuRegistry(ALIAS_DRON):
    option = 0
    while option != 1 and option != 2:
        print("De que forma quiere conectarse al AD_Registry? (1/2)")
        print("1. Socket")
        print("2. API REST")
        option = int(input())
        if(option == 1):
            id, token = dronRegistry(IP_REGISTRY, PUERTO_REGISTRY, ALIAS_DRON)
        elif(option == 2):
            id, token = dronRegistryAPI(ALIAS_DRON)
        else:
            print("Opción no valida")
            print("")

    return id, token

### Menu Registry ###

#----------------------------------------------------#

### Auntenticacion Engine por API REST ###

def dronEngineAPI(id, token):

    try:
        response = requests.get(f"https://127.0.0.1:8001/autenticacionDron?id={id}&token={token}", verify="certificado-firmado.crt")
        json = response.json()

        if json["mensaje"] == "Token correcto":
            return True
        elif json["mensaje"] == "Token incorrecto":
            return False
        else: 
            print("Ha ocurrido un error inesperado al autenticar el dron")
            return False
    except Exception as exc:
        print("No se ha podido conectar al engine por API ERROR: " + str(exc))
        return False

### Auntenticacion Engine por API REST ###

#----------------------------------------------------#

### Conexion via socket seguro con engine para conseguir la contraseña de kafka ###
    
def dronEngineSocketSeguro(IP_ENGINE, PUERTO_ENGINE):
    # Se crea el contexto para el cliente indicándole que confie en certificados autofirmados
    #context = ssl.create_default_context()
    context = ssl._create_unverified_context()

    contraseñaKafka = None

    with socket.create_connection((IP_ENGINE, PUERTO_ENGINE)) as sock:
        with context.wrap_socket(sock, server_hostname=IP_ENGINE) as ssock:
            print(ssock.version()) #TLSv1.3
            print(ssock.getpeername()) #('127.0.0.1', 8443) Server
            print(ssock.getsockname()) #('127.0.0.1', 60605) Client     
            print('Enviando saludo al engine')
            mensaje="Hola soy el dron "+ALIAS_DRON
            ssock.send(mensaje.encode())
            data = ssock.recv(1024)
#            print('Recibida la contraseña ', repr(data))
            contraseñaKafka = data
    
    return contraseñaKafka

### Conexion via socket seguro con engine para conseguir la contraseña de kafka ###
    
#----------------------------------------------------#

########## MAIN ###########
# ip y puerto del engine
# ip y puerto kafka
# ip y puerto de registry
# puerto de escucha del dron
# alias del dron
if (len(sys.argv) == 9):

    IP_ENGINE = sys.argv[1] 
    PUERTO_ENGINE = sys.argv[2]

    IP_KAFKA = sys.argv[3]
    PUERTO_KAFKA = sys.argv[4]
    ADDR_KAFKA = IP_KAFKA + ":" + str(PUERTO_KAFKA)

    IP_REGISTRY = sys.argv[5]
    PUERTO_REGISTRY = sys.argv[6]

    PORT = sys.argv[7]
    ALIAS_DRON = sys.argv[8]

    pos_actual = (0,0)
    pos_final = (int,int)

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
    pygame.display.set_caption("Mapa impreso desde el dron: " + str(sys.argv[7]))

    ############################ PYGAME ############################

    
    id, token = menuRegistry(ALIAS_DRON)

    if id:

        print( "id: ", id, " token: ", token)
        
        # Conexion con el módulo AD_Engine para darse de alta en el espectaculo
        # Argumentos dronEngine( IP_Engine, Puerto_Engine, ID, Token)
    
        engineOnline = True
        primeraVez = True
        while engineOnline:

            if(primeraVez == False):
                id, token = menuRegistry(ALIAS_DRON)
            primeraVez=False

            if(dronEngineAPI(id, token)):
                # Pedimos al engine la contraseña de kafka
                input("Pulsa enter para pedir la contraseña de kafka")
                contraseñaKafka = dronEngineSocketSeguro(IP_ENGINE, PUERTO_ENGINE)
                
#                print("La contraseña de kafka es: " + str(contraseñaKafka))

                # conexion con el módulo AD_Kafka para recibir las ordenes
                # Argumentos consumidor( IP_Kafka, Puerto_Kafka, ID )
                try:
                    engineOnline = consumidor_mapas(str(id), pos_actual, pos_final)
    
                    if(engineOnline == False):
                        print("Se ha cerrado la conexión inesperadamente con el engine (1) " + str(exc))
                    engineOnline = False
                    print("Vuelvo a casa")
                    while(pos_actual != (1,1)):
                        
                        pos_actual = run(pos_actual, (1,1))
                        print("Posicion actualizada -->" + str(pos_actual))
                        time.sleep(1)
    
                except Exception as exc:
                    print("Se ha cerrado la conexión inesperadamente con el engine (2) " + str(exc))
                    engineOnline = False
                    print("Vuelvo a casa")
                    while(pos_actual != (1,1)):
                        pos_actual = run(pos_actual, (1,1))
                        print("Posicion actualizada -->" + str(pos_actual))
                        time.sleep(1)
                print("Quieres volver a participar en otra figura? (S/N)")
                respuesta = input()
                if(respuesta == "S" or respuesta == "s"):
                    engineOnline = True
                    pos_actual = (0,0)
                    pos_final = (int,int)
                else:
                    engineOnline = False
            else:
                print("No se ha podido entrar al espectaculo")
                engineOnline = False
    else:
        print("No se ha podido registrar el dron")
        
else:
    print("No se ha podido conectar al servidor de registro, los argumentos son <IP_Engine> <Puerto_Engine> <IP_Kafka> <Puerto_Kafka> <IP_Registry> <Puerto_Registry> <Puerto_escucha> <Alias_Dron>")
        