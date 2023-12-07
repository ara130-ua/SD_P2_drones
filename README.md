**SD Art with Drones**
-
**La aplicación ha sido creada por Joan Climent Quiñones y Adrián Ríos Armero**

Art with Drones es una aplicación desarrollado con python, en esta se pretende simular un espectáculo de drones
los cuales se mueven a las posiciones proporcionadas por un engine y crean figuras en un mapa de dos dimensiones.

Puedes iniciar esta aplicación con launcher_programs.py


**Puertos de los modulos**
AD_Drone = 5050
AD_Registry = 6050
AD_Wheather = 7050
AD_Engine = 8050
kafka = 9092

Ejecutar en una terminal a parte: uvicorn AD_Registry:app --reload





