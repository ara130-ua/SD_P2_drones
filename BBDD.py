import sqlite3

conexion = sqlite3.connect("bd1.db")

try:
    #tabla drones
    conexion.execute("create table drones (id integer primary key autoincrement, alias text, token integer, estado text, coordenadaX integer, coordenadaY integer, autenticado bool)")

    print("se creo la tabla drones")
#si la tabla ya existe, no la crea
except sqlite3.OperationalError:
    print("La tabla drones ya existe")


try:
    #tabla weather (clima)
    conexion.execute("create table weather (id integer primary key autoincrement, ciudad text, pais text)")
    print("se creo la tabla wheater")

    cursor = conexion.cursor()

    # Metemos las coordenadas de las ciudades en la tabla weather
    cursor.execute("insert into weather (ciudad, pais) values ('Alicante', 'es')")
    cursor.execute("insert into weather (ciudad, pais) values ('Madrid', 'es')")
    cursor.execute("insert into weather (ciudad, pais) values ('Barcelona', 'es')")
    cursor.execute("insert into weather (ciudad, pais) values ('Valencia', 'es')")
    cursor.execute("insert into weather (ciudad, pais) values ('Sevilla', 'es')")
    cursor.execute("insert into weather (ciudad, pais) values ('Zaragoza', 'es')")
    cursor.execute("insert into weather (ciudad, pais) values ('Malaga', 'es')")
    cursor.execute("insert into weather (ciudad, pais) values ('Murcia', 'es')")
    cursor.execute("insert into weather (ciudad, pais) values ('Palma', 'es')")

    #ahora ciudades de europa
    cursor.execute("insert into weather (ciudad, pais) values ('Paris', 'fr')")
    cursor.execute("insert into weather (ciudad, pais) values ('Berlin', 'de')")
    cursor.execute("insert into weather (ciudad, pais) values ('Roma', 'it')")
    cursor.execute("insert into weather (ciudad, pais) values ('Praga', 'cz')")
    cursor.execute("insert into weather (ciudad, pais) values ('Viena', 'at')")
    cursor.execute("insert into weather (ciudad, pais) values ('Londres', 'gb')")

    conexion.commit()
    conexion.close()
    
except sqlite3.OperationalError:
    print("La tabla wheather ya existe")

try:
    #tabla registro_auditoria
    conexion.execute('''
        CREATE TABLE registro_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT,
            accion TEXT,
            origen TEXT,
            descripcion TEXT
        )
    ''')
    print("se creo la tabla registro_auditoria")
except sqlite3.OperationalError:
    print("La tabla registro_auditoria ya existe")

try:
    # tabla mapas
    conexion.execute('''
        CREATE TABLE mapa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idDrone INTEGER,
            estado char(1),
            coordenadaX INTEGER,
            coordenadaY INTEGER,
        )
    ''')
    print("se creo la tabla mapa")
except sqlite3.OperationalError:
    print("La tabla mapa ya existe")