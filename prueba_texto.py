import sqlite3
import json


# Description: Prueba de lectura de ficheros de texto
   
   # sacamos la información en lineas de los drones
def manejoClima():
    with open('clima.txt', 'r') as archivo:
        lineas = archivo.readlines()

    datos_clima = []
    for linea in lineas:
        # Eliminamos espacios en blanco
        linea = linea.strip()
        if linea:
            elementos = linea.split('|')

            if len(elementos) == 2:
                datos_clima.append((str(elementos[0]), str(elementos[1])))
    
    #cerramos el fichero
    print(datos_clima)

    return(datos_clima)

def leerUltFilaClima():
    # nos conectamos a la BBDD y leemos la última fila
    conexion = sqlite3.connect("bd1.db")
    cursor = conexion.cursor()
    cursor.execute("select * from weather order by id desc limit 1")
    ultimaFila = cursor.fetchone()
    conexion.close()
    # convertimos los datos a una tupla y la devolvemos
    datosClimaActual = ultimaFila[1], ultimaFila[2]
    return datosClimaActual


def leerArchivoJSON():
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

# dronMov = [E,ID,(X,Y)]
def manejoMapa(isMoved = False, dronMov = []):
    mapaBytes = [[0 for _ in range(20)] for _ in range(20)]
    listaMapa = []
  
    for coordX in mapaBytes:
        listaCoordX = []
        for coordY in coordX:
            listaCoordX.append(('E', 0))
        listaMapa.append(listaCoordX)

    if isMoved:
        estado = dronMov[0]
        Id = dronMov[1]
        movimiento = (dronMov[2][0]-1, dronMov[2][1]-1)
        
        listaMapa[movimiento[0]][movimiento[1]] = (estado, Id)


    return(listaMapa)

def stringMapa(listaMapa):
    strMapa = ""
    for fila in listaMapa:
        strMapa = strMapa + "| "
        for elemento in fila:
            strMapa = strMapa + "[" + elemento[0] + "," + str(elemento[1]) + "] "
        strMapa = strMapa + "|\n"

    return strMapa

    
##main
print("Bienvenido al AD_Engine")
data = manejoMapa(True, ['R',4,(4,4)])

print(stringMapa(data))
