import sqlite3

conexion = sqlite3.connect("bd2.db")

try:
    #tabla drones
    conexion.execute("create table drones (id integer primary key autoincrement, alias text, token integer)")

    print("se creo la tabla drones")
#si la tabla ya existe, no la crea
except sqlite3.OperationalError:
    print("La tabla drones ya existe")


try:
    #tabla weather (clima)
    conexion.execute("create table weather (id integer primary key autoincrement, nombre text, temperatura real)")
    print("se creo la tabla wheater")
except sqlite3.OperationalError:
    print("La tabla wheather ya existe")