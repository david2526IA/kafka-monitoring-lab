# Kafka Monitoring Lab

Proyecto de monitorizacion de servidores con Python, Apache Kafka, Docker y MongoDB Atlas.

El objetivo es simular metricas de varios servidores, enviarlas a Kafka en tiempo real, consumirlas desde Python y guardarlas en MongoDB Atlas. Ademas, el consumidor calcula KPIs cada 20 mensajes mediante una ventana tumbling.

## Arquitectura

El flujo implementado es:

```text
Productor Python -> Kafka -> Consumidor Python -> MongoDB Atlas
```

El productor genera metricas simuladas y las envia al topic `system-metrics-topic`. El consumidor lee los mensajes, guarda cada evento bruto en `system_metrics_raw` y cada 20 mensajes guarda un documento de KPIs en `system_metrics_kpis`.

## Estructura

```text
consumer/
  consumidor_metrics.py
docker/
  docker-compose.yml
producer/
  productor_metrics.py
docs/
  evidencias.md
requirements.txt
.env.example
```

## Servidores simulados

- web01
- web02
- db01
- app01
- cache01

## Metricas generadas

- cpu_percent
- memory_percent
- disk_io_mbps
- network_mbps
- error_count

## Requisitos

- Docker Desktop
- Python 3.10 o superior
- Cuenta de MongoDB Atlas
- Git

## Instalacion

Crear y activar un entorno virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
py -m pip install --upgrade pip
pip install -r requirements.txt
```

Si el comando `python` esta disponible en el sistema, tambien se puede usar en lugar de `py`.

## Configuracion

Copiar el archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

Editar `.env` y cambiar `MONGO_URI` por la cadena de conexion real de MongoDB Atlas. Este archivo no debe subirse a GitHub porque contiene credenciales.

Variables usadas:

```text
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
KAFKA_TOPIC=system-metrics-topic
KAFKA_GROUP_ID=david2526_monitoring_group
PRODUCER_INTERVAL_SECONDS=5
KPI_WINDOW_SIZE=20

MONGO_URI=mongodb+srv://USER:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=kafka_monitoring_lab
MONGO_RAW_COLLECTION=system_metrics_raw
MONGO_KPI_COLLECTION=system_metrics_kpis
```

En MongoDB Atlas se debe permitir la IP actual en `Network Access` y crear un usuario de base de datos.

## Arrancar Kafka

Desde la raiz del proyecto:

```powershell
docker compose -f .\docker\docker-compose.yml up -d
```

Comprueba los contenedores:

```powershell
docker ps
```

## Crear el topic

```powershell
docker compose -f .\docker\docker-compose.yml exec kafka kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic system-metrics-topic --partitions 1 --replication-factor 1
```

Comprobar que existe:

```powershell
docker compose -f .\docker\docker-compose.yml exec kafka kafka-topics --bootstrap-server kafka:9092 --list
```

## Ejecutar el consumidor

En una terminal con el entorno virtual activado:

```powershell
py .\consumer\consumidor_metrics.py
```

El consumidor se queda en ejecucion esperando mensajes.

## Ejecutar el productor

En otra terminal con el entorno virtual activado:

```powershell
py .\producer\productor_metrics.py
```

Para pruebas rapidas se puede reducir el intervalo:

```powershell
$env:PRODUCER_INTERVAL_SECONDS="1"
py .\producer\productor_metrics.py
```

Dejar el productor ejecutandose hasta que envie al menos 20 mensajes. Cada ventana de 20 mensajes genera un documento KPI.

## MongoDB Atlas

El proyecto usa una unica base de datos:

```text
kafka_monitoring_lab
```

Con dos colecciones:

```text
system_metrics_raw
system_metrics_kpis
```

`system_metrics_raw` guarda los mensajes recibidos desde Kafka junto con metadatos de ingesta.

`system_metrics_kpis` guarda una ventana KPI cada 20 mensajes.

## Decision de implementacion

Se ha usado un unico consumidor para dos tareas:

- Insertar cada mensaje bruto en `system_metrics_raw`.
- Calcular e insertar KPIs cada 20 mensajes en `system_metrics_kpis`.

Esta opcion mantiene el proyecto simple y permite demostrar el flujo completo con un unico proceso consumidor. Para un sistema mas grande, se podria separar en dos consumidores distintos con `group_id` diferentes.

## KPIs calculados

Cada documento KPI contiene:

- message_count
- avg_cpu_percent
- avg_memory_percent
- avg_disk_io_mbps
- avg_network_mbps
- max_cpu_percent
- max_memory_percent
- total_errors
- window_started_at
- window_ended_at

La ventana es tumbling: mensajes 1-20 generan un KPI, mensajes 21-40 generan el siguiente y asi sucesivamente.

## Parar servicios

Parar productor o consumidor:

```text
Ctrl + C
```

Parar Kafka y Zookeeper:

```powershell
docker compose -f .\docker\docker-compose.yml down
```

## Evidencias

Las capturas y pruebas de funcionamiento estan en:

```text
docs/evidencias.md
```

Incluyen fork del repositorio, Kafka con Docker, topic creado, productor, consumidor, datos RAW en MongoDB Atlas y documentos KPI.

## Memoria y manual

La memoria final y el manual desde cero estan en:

```text
docs/memoria_manual_proyecto.md
docs/memoria_manual_proyecto.pdf
```

## Entrega

Comandos finales:

```powershell
git add .
git commit -m "Implement kafka monitoring pipeline"
git push origin main
git tag v1.0-entrega
git push origin v1.0-entrega
```
