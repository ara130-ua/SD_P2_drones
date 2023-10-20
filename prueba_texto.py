def manejoFichero(maxDrones):
   
    fileWrite = 'figura.txt'
    datos_drones = []

   # Una manera de sacar el contenido en una string
   #f = file_manipulation(fileWrite, 'r')
   #contenido = f.read()
   
   # sacamos la información en lineas de los drones
    with open(fileWrite, 'r') as archivo:
        lineas = archivo.readlines()

    
    for linea in lineas:
        #haz que el primer carater y el ultimo sean un espacio
        linea = linea.removeprefix('<')
        linea = linea.removesuffix('>')
        
        
        print (linea)
        
        #Eliminamos espacios en blanco
        linea = linea.strip()
        if linea:
            elementos = linea.split( '-' )

            if len(elementos) == 3:
                datos_drones.append((int(elementos[0]), int(elementos[1]), int(elementos[2])))            

    #cerramos el fichero
    return(datos_drones)

##main
print ("Bienvenido al AD_Engine")
data = manejoFichero(99)

#escribe el contenido del fichero
print(data)