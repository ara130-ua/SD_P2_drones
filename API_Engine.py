import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

from fastapi import FastAPI, Response
import time

app = FastAPI()

@app.get("/events", response_class=Response)
async def events():
    def event_stream():
        while True:
            datos = obtener_datos()
            yield f"data: {json.dumps(datos)}\n\n"
            time.sleep(1)

    return event_stream()

# Ruta que renderiza el HTML con los datos actualizados del JSON
@app.get("/", response_class=HTMLResponse)
async def mostrar_datos(request: Request):

    # Renderizar el HTML y pasar los datos al template
    return templates.TemplateResponse("index.html", {"request": request, "datos": obtener_datos()})

# Leer los datos desde tu archivo JSON (o de donde los obtengas)
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

def obtener_datos():

    conn = sqlite3.connect('bd1.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM mapa")
    datos = cursor.fetchall()

    conn.close()

    return datos

    

