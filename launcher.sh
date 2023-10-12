gnome-terminal --tab --title="BBDD" --command="bash -c 'python BBDD.py 5050; $SHELL'"
gnome-terminal --tab --title="Registro" --command="bash -c 'python AD_Registry.py 5050; $SHELL'"
gnome-terminal --tab --title="Dron" --command="bash -c 'python AD_Drone.py 1 2 3 4 127.0.1.1 5050 dronsito; $SHELL'"

