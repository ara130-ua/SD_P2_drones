import datetime
import sqlite3

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



# Ejemplos de uso:

# Autenticación exitosa
auditar_evento('Autenticación', '192.168.1.1', 'Usuario autenticado correctamente')

# Intento de autenticación fallido
auditar_evento('Intento de autenticación fallido', '192.168.1.2', 'Usuario no reconocido')

# Cambio de clima
auditar_evento('Cambio de clima', 'Estación meteorológica', 'Se espera lluvia para la próxima hora')
