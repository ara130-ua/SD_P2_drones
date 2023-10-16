import subprocess
import time

#   ATENCION
#   Para un correcto funcionamiento es necesario que kafka se encuentre en la carpeta home del usuario

# Lanzamos el zookeeper
comando_zookeeper = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/zookeeper-server-start.sh /home/joanclq/kafka/config/zookeeper.properties; exec bash '"

# Lanzmos el broker
comando_broker = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-server-start.sh /home/joanclq/kafka/config/server.properties; exec bash'"

# Creamos el topic
create_topic = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --create --topic iabd-topic --bootstrap-server localhost:9092; exec bash'"

# Ejecutar los comandos en terminales separadas
subprocess.run(comando_zookeeper, shell=True)
time.sleep(2)
subprocess.run(comando_broker, shell=True)
time.sleep(2)
subprocess.run(create_topic, shell=True)
