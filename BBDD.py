import sqlite3

conexion = sqlite3.connect("bd1.db")

try:
    #tabla drones
    conexion.execute("create table drones (id integer primary key autoincrement, alias text, token integer, estado text, coordenadaX integer, coordenadaY integer)")

    print("se creo la tabla drones")
#si la tabla ya existe, no la crea
except sqlite3.OperationalError:
    print("La tabla drones ya existe")


try:
    #tabla weather (clima)
    conexion.execute("create table weather (id integer primary key autoincrement, nombre text, latitud real, longitud real)")
    print("se creo la tabla wheater")

    # Metemos las coordenadas de las ciudades en la tabla weather
    conexion.execute("insert into weather(nombre, latitud, longitud) values ('Buenos Aires', -34.61315, -58.37723)")
    conexion.execute("insert into weather(nombre, latitud, longitud) values ('Cordoba', -31.4135, -64.18105)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Rosario', -32.94682, -60.63932)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Mendoza', -32.89084, -68.82717)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('La Plata', -34.93139, -57.94889)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Mar del Plata', -38.00228, -57.55754)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('San Miguel de Tucuman', -26.82414, -65.2226)")
    #ahora de españa
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Madrid', 40.4165, -3.70256)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Barcelona', 41.38879, 2.15899)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Valencia', 39.46975, -0.37739)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Sevilla', 37.38283, -5.97317)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Zaragoza', 41.65606, -0.87734)")
    #ahora de europa
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Paris', 48.85341, 2.3488)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Berlin', 52.52437, 13.41053)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Roma', 41.89193, 12.51133)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Londres', 51.50853, -0.12574)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Lisboa', 38.71667, -9.13333)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Amsterdam', 52.37403, 4.88969)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Bruselas', 50.85045, 4.34878)")
    conexion.execute("insert into weather (nombre, latitud, longitud) values ('Viena', 48.20849, 16.37208)")

except sqlite3.OperationalError:
    print("La tabla wheather ya existe")