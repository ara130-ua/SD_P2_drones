import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
#from socketio import AsyncServer, ASGIApp
import asyncio
import json

# python3 -m venv fastapi-env
# source fastapi-env/bin/activate

app = FastAPI()
templates = Jinja2Templates(directory="templates")


#sio = AsyncServer(async_mode='asgi', cors_allowed_origins='*')
#app.mount('/socket.io', ASGIApp(sio, app))


# Ruta que renderiza el HTML con los datos actualizados del JSON
@app.get("/", response_class=HTMLResponse)
async def mostrar_datos(request: Request):

    # Renderizar el HTML y pasar los datos al templatessssssssssssssssssssssssssssssssssssssssssssss
    return templates.TemplateResponse("prueba.html", {"request": request, "datos": obtenerMapaBBDD()})

@app.get("/drones", response_class=JSONResponse)
async def obtener_datos_drones():
    return obtenerMapaBBDD()

#[dron[0], dron[1], (dron[2], dron[3])]
def obtenerMapaBBDD():
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
        dron_id = dron[0]
        dron_estado = dron[1]
        pos_X, pos_Y = dron[2], dron[3]
        listaDrones.append({"id": dron_id, "estado": dron_estado, "pos_X": pos_X, "pos_Y": pos_Y})
    return listaDrones


# Leer los datos desde tu archivo JSON
def obtener_datos():
    with open("data.json", "r") as file:
        data = json.load(file)

        mapa = data["mapa"]
        
        movimientos = []

        for dron in mapa["Drones"]:
            dron_id = dron["id"]
            dron_estado = dron["estado"]
            pos_X, pos_Y = dron["pos"][0], dron["pos"][1]
            movimientos.append({"id": dron_id, "estado": dron_estado, "pos_X": pos_X, "pos_Y": pos_Y})

        return movimientos
