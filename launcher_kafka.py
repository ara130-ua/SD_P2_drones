import subprocess
import time

IP_KAFKA = "172.20.10.2"

#   ATENCION
#   Para un correcto funcionamiento es necesario que kafka se encuentre en la carpeta home del usuario

# Lanzamos el zookeeper
comando_zookeeper = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/zookeeper-server-start.sh /home/joanclq/kafka/config/zookeeper.properties; exec bash '"

# Lanzmos el broker
comando_broker = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-server-start.sh /home/joanclq/kafka/config/server.properties; exec bash'"

# Creamos el topic
create_topic1 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --create --topic mapas1-topic --bootstrap-server " + IP_KAFKA + ":9092; exec bash'"
create_topic2 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --create --topic movimientos1-topic --bootstrap-server " + IP_KAFKA + ":9092; exec bash'"

# Creamos el topic
create_topic3 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --create --topic mapas2-topic --bootstrap-server " + IP_KAFKA + ":9092; exec bash'"
create_topic4 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --create --topic movimientos2-topic --bootstrap-server " + IP_KAFKA + ":9092; exec bash'"

# Borramos el topic
delete_topic1 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --delete --topic mapas1-topic --bootstrap-server " + IP_KAFKA + ":9092; exec bash'"
delete_topic2 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --delete --topic movimientos1-topic --bootstrap-server " + IP_KAFKA + ":9092; exec bash'"

# Borramos el topic
delete_topic3 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --delete --topic mapas2-topic --bootstrap-server " + IP_KAFKA + ":9092; exec bash'"
delete_topic4 = "gnome-terminal -- bash -c '/home/joanclq/kafka/bin/kafka-topics.sh --delete --topic movimientos2-topic --bootstrap-server " + IP_KAFKA + ":9092; exec bash'"

# Ejecutar los comandos en terminales separadas
subprocess.run(comando_zookeeper, shell=True)
time.sleep(2)
subprocess.run(comando_broker, shell=True)
time.sleep(2)

subprocess.run(delete_topic1, shell=True)
subprocess.run(delete_topic2, shell=True)
subprocess.run(delete_topic3, shell=True)
subprocess.run(delete_topic4, shell=True)

subprocess.run(create_topic1, shell=True)
subprocess.run(create_topic2, shell=True)
subprocess.run(create_topic3, shell=True)
subprocess.run(create_topic4, shell=True)