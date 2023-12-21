from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from socketio import AsyncServer, ASGIApp
import asyncio
import json

# python3 -m venv fastapi-env
# source fastapi-env/bin/activate

app = FastAPI()
templates = Jinja2Templates(directory="templates")

sio = AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app.mount('/socket.io', ASGIApp(sio, app))


# Ruta que renderiza el HTML con los datos actualizados del JSON
@app.get("/", response_class=HTMLResponse)
async def mostrar_datos(request: Request):

    # Renderizar el HTML y pasar los datos al template
    return templates.TemplateResponse("prueba.html", {"request": request, "datos": obtener_datos()})

@app.get("/drones", response_class=JSONResponse)
async def obtener_datos_drones():
    return obtener_datos()

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



    
