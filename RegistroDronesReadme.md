Ejecución de los drones

Cuando empiece por primera vez el espectaculo se crearán los drones, y se guardarán en la base de datos,


### Registry ###

Su ejecución empezará leyendo del archivo json los mapas,
abrirá un socket por el que el engine le dirá que mapa se va a utilizar y creará la cantidad de drones en la BBDD (no les asignará ningún valor).
después se hará un bucle cuyo rango será igual al número de drones que hay en el mapa, y se pondrá a escuchar las peticiones de los drones.

Si los mapas tienen diferente tamaño, habría que controlarlo:
- Inicializar más drones si el número de drones es mayor.
- Utilizar el número justo de drones si es menor.
Esto se debe comprobar tanto en el registry como en el engine.

Una vez termine el registro de los drones, volverá a escuchar al engine para el siguiente mapa.
El engine le pasará el mapa y los drones se conectarán al registry para recibir su nuevo token
los drones deben enviar su id para recibir el token actualizado, 
