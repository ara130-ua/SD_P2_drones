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

    # Renderizar el HTML y pasar los datos al templates
    return templates.TemplateResponse("prueba.html", {"request": request, "datos": getMovimientosMapaBBDD()})

@app.get("/drones", response_class=JSONResponse)
async def obtener_datos_drones():
    return getMovimientosMapaBBDD()

@app.get("/temp", response_class=JSONResponse)
async def obtener_temp():
    return getTempBBDD()

@app.get("/logs",response_class=JSONResponse)
async def obtener_logs():
    return getLogsBBDD()

def getLogsBBDD():
    conexion = sqlite3.connect("bd1.db")
    cursor = conexion.cursor()
    cursor.execute("select * from registro_auditoria")
    logs = []
    for row in cursor:
        logs.append({"accion": row[2], "ip_maquina":row[3],"fecha": row[1], "mensaje": row[4]})
    conexion.close()
    return logs

def getTempBBDD():
    conexion = sqlite3.connect("bd1.db")
    cursor = conexion.cursor()
    cursor.execute("select * from temperatura_actual")
    temp = []
    for row in cursor:
        temp.append({"ciudad": row[1], "temperatura": row[2]})
    conexion.close()
    return temp
    
def getMovimientosMapaBBDD():
    conexion = sqlite3.connect("bd1.db")
    cursor = conexion.cursor()
    cursor.execute("select idDron, estado, coordenadaX, coordenadaY from mapas")
    movimientos = []
    for row in cursor:
        movimientos.append({"id": row[0], "estado": row[1], "pos_X": row[2], "pos_Y": row[3]})
    conexion.close()
    return movimientos
