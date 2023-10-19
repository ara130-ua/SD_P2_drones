# SD_P1_drones
Sistemas distribuidos práctica de drones

**links de interes**
https://andres-plazas.medium.com/leer-y-escribir-datos-en-kafka-usando-python-2696154c3948

Paso a paso de la práctica:

El engine entra en modo de escucha, hasta que un fichero le dará la información de la figura con un formato concreto,
en este fichero encontramos la cantidad de drones que hay que desplegar y las coordenadas de cada pixel.

Para desplegar los drones, una de las soluciones puede ser, desplegar 100 drones que es el máximo de ids que tenemos disponibles, e intentar acceder a todos con el engine, y que cuando el engine los rechace, matar esos procesos.

Para el movimiento de los drones, podemos buscar un algoritmo de recorrido que lo haga en el menor número de movimientos, o lo podemos hacer de manera aleatoria, en la práctica no especifica ningún tipo de movimiento.

Manejo de ficheros python
https://tecnops.es/tutorial-de-python-parte-4/

chatGPT información del fichero
https://chat.openai.com/c/2ff0a61f-7550-4bb3-81a4-60c34c7fffe8
