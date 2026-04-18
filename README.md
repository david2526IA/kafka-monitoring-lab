# Kafka Monitoring Lab

Proyecto de monitorizacion de servidores con Python, Apache Kafka, Docker y MongoDB Atlas.

El objetivo es simular metricas de varios servidores, enviarlas a Kafka en tiempo real, consumirlas desde Python, guardarlas en MongoDB Atlas y calcular KPIs cada 20 mensajes mediante una ventana tumbling.

## Resumen del proyecto

| Elemento | Descripcion |
|---|---|
| Lenguaje principal | Python |
| Broker de mensajeria | Apache Kafka |
| Entorno local | Docker Compose |
| Persistencia | MongoDB Atlas |
| Productor | Genera metricas simuladas de servidores |
| Consumidor | Inserta eventos RAW y calcula KPIs |
| Topic Kafka | `system-metrics-topic` |
| Base de datos | `kafka_monitoring_lab` |
| Coleccion RAW | `system_metrics_raw` |
| Coleccion KPI | `system_metrics_kpis` |
| Tag de entrega | `v1.0-entrega` |

## Flujo de trabajo

```mermaid
flowchart TD
    A["Fork del repositorio base"] --> B["Clonado del fork en local"]
    B --> C["Creacion de entorno virtual Python"]
    C --> D["Instalacion de requirements.txt"]
    D --> E["Configuracion de .env con MongoDB Atlas"]
    E --> F["Arranque de Kafka y Zookeeper con Docker Compose"]
    F --> G["Creacion del topic system-metrics-topic"]
    G --> H["Ejecucion del consumidor"]
    H --> I["Ejecucion del productor"]
    I --> J["Envio de metricas JSON a Kafka"]
    J --> K["Insercion RAW en MongoDB Atlas"]
    K --> L["Calculo de KPIs cada 20 mensajes"]
    L --> M["Insercion de KPIs en MongoDB Atlas"]
    M --> N["Documentacion, evidencias, memoria y tag final"]
```

## Arquitectura

```mermaid
flowchart LR
    P["producer/productor_metrics.py<br/>Genera metricas simuladas"] --> K["Kafka broker<br/>localhost:29092"]
    K --> T["Topic<br/>system-metrics-topic"]
    T --> C["consumer/consumidor_metrics.py<br/>Lee mensajes JSON"]
    C --> R["MongoDB Atlas<br/>system_metrics_raw"]
    C --> W["Ventana tumbling<br/>20 mensajes"]
    W --> KPI["MongoDB Atlas<br/>system_metrics_kpis"]
    D["Docker Compose"] --> Z["Zookeeper<br/>kafka-lab-zookeeper"]
    D --> K
```

El productor genera metricas simuladas y las envia al topic `system-metrics-topic`. El consumidor lee los mensajes, guarda cada evento bruto en `system_metrics_raw` y cada 20 mensajes guarda un documento de KPIs en `system_metrics_kpis`.

## Estructura del repositorio

```text
kafka-monitoring-lab/
  consumer/
    consumidor_metrics.py
  docker/
    docker-compose.yml
  docs/
    evidencias.md
    memoria_manual_proyecto.md
    memoria_manual_proyecto.pdf
    img/
      01_fork_github.png
      02_docker_kafka_arrancado.png
      03_topic_kafka_creado.png
      04_productor_enviando.png
      05_consumidor_recibiendo.png
      06_mongodb_raw.png
      07_mongodb_kpis.png
      08_readme.png
      09_tag_github.png
  producer/
    productor_metrics.py
  .env.example
  .gitattributes
  .gitignore
  README.md
  requirements.txt
```

## Componentes principales

| Componente | Funcion |
|---|---|
| `producer/productor_metrics.py` | Genera metricas aleatorias y las publica en Kafka |
| `consumer/consumidor_metrics.py` | Consume mensajes, guarda RAW y calcula KPIs |
| `docker/docker-compose.yml` | Levanta Kafka y Zookeeper en local |
| `.env.example` | Plantilla de configuracion sin credenciales reales |
| `docs/evidencias.md` | Evidencias visuales de funcionamiento |
| `docs/memoria_manual_proyecto.md` | Memoria final y manual desde cero |
| `docs/memoria_manual_proyecto.pdf` | Version PDF de la memoria |

## Servidores simulados

El productor genera eventos para cinco servidores:

- `web01`
- `web02`
- `db01`
- `app01`
- `cache01`

## Metricas generadas

Cada mensaje enviado a Kafka contiene:

| Campo | Descripcion |
|---|---|
| `server_id` | Servidor simulado |
| `timestamp` | Fecha y hora UTC del evento |
| `cpu_percent` | Uso de CPU simulado |
| `memory_percent` | Uso de memoria simulado |
| `disk_io_mbps` | Entrada/salida de disco simulada |
| `network_mbps` | Trafico de red simulado |
| `error_count` | Numero de errores simulados |

Ejemplo de mensaje:

```json
{
  "server_id": "web01",
  "timestamp": "2026-04-16T10:15:30.000000+00:00",
  "cpu_percent": 42.8,
  "memory_percent": 67.4,
  "disk_io_mbps": 120.5,
  "network_mbps": 88.2,
  "error_count": 1
}
```

## Requisitos

- Docker Desktop
- Docker Compose
- Python 3.10 o superior
- Cuenta de MongoDB Atlas
- Git
- Navegador web para consultar MongoDB Atlas y GitHub

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

Dependencias usadas:

```text
kafka-python
pymongo
python-dotenv
certifi
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

En MongoDB Atlas se debe:

- permitir la IP actual en `Network Access`;
- crear un usuario de base de datos;
- copiar la cadena de conexion del driver Python;
- sustituir usuario, password y cluster en `MONGO_URI`.

## Arrancar Kafka

Desde la raiz del proyecto:

```powershell
docker compose -f .\docker\docker-compose.yml up -d
```

Comprobar contenedores:

```powershell
docker ps
```

Contenedores esperados:

```text
kafka-lab-zookeeper
kafka-lab-broker
```

## Crear el topic

Crear el topic:

```powershell
docker compose -f .\docker\docker-compose.yml exec kafka kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic system-metrics-topic --partitions 1 --replication-factor 1
```

Comprobar que existe:

```powershell
docker compose -f .\docker\docker-compose.yml exec kafka kafka-topics --bootstrap-server kafka:9092 --list
```

Resultado esperado:

```text
system-metrics-topic
```

## Ejecutar el consumidor

En una terminal con el entorno virtual activado:

```powershell
py .\consumer\consumidor_metrics.py
```

El consumidor se queda en ejecucion esperando mensajes. Al arrancar debe mostrar:

```text
[consumer] Kafka bootstrap servers: localhost:29092
[consumer] Topic: system-metrics-topic
[consumer] Group id: david2526_monitoring_group
[consumer] KPI window size: 20
[consumer] Connected to MongoDB Atlas.
```

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

## Validacion del funcionamiento

```mermaid
sequenceDiagram
    participant P as Productor Python
    participant K as Kafka
    participant C as Consumidor Python
    participant M as MongoDB Atlas

    P->>K: Envia metrica JSON
    K->>C: Entrega mensaje del topic
    C->>M: Inserta documento RAW
    C->>C: Acumula mensaje en ventana
    C->>M: Inserta KPI al completar 20 mensajes
```

Comprobaciones realizadas:

| Paso | Evidencia esperada |
|---|---|
| Docker | Kafka y Zookeeper arrancados |
| Topic | `system-metrics-topic` creado |
| Productor | Mensajes enviados con particion y offset |
| Consumidor | Mensajes recibidos e insertados |
| MongoDB RAW | Documentos individuales en `system_metrics_raw` |
| MongoDB KPI | Documentos agregados en `system_metrics_kpis` |
| GitHub | Tag `v1.0-entrega` disponible |

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

`system_metrics_raw` guarda los mensajes recibidos desde Kafka junto con metadatos de ingesta:

- `kafka_topic`
- `kafka_partition`
- `kafka_offset`
- `ingested_at`

`system_metrics_kpis` guarda una ventana KPI cada 20 mensajes.

## Decision de implementacion

Se ha usado un unico consumidor para dos tareas:

- insertar cada mensaje bruto en `system_metrics_raw`;
- calcular e insertar KPIs cada 20 mensajes en `system_metrics_kpis`.

Esta opcion mantiene el proyecto simple y permite demostrar el flujo completo con un unico proceso consumidor. Para un sistema mas grande, se podria separar en dos consumidores distintos con `group_id` diferentes.

## KPIs calculados

Cada documento KPI contiene:

| Campo | Descripcion |
|---|---|
| `window_number` | Numero de ventana procesada |
| `message_count` | Mensajes incluidos en la ventana |
| `window_started_at` | Timestamp del primer mensaje |
| `window_ended_at` | Timestamp del ultimo mensaje |
| `calculated_at` | Momento en el que se calculo el KPI |
| `servers` | Servidores presentes en la ventana |
| `avg_cpu_percent` | Media de CPU |
| `avg_memory_percent` | Media de memoria |
| `avg_disk_io_mbps` | Media de I/O de disco |
| `avg_network_mbps` | Media de red |
| `max_cpu_percent` | Maximo de CPU |
| `max_memory_percent` | Maximo de memoria |
| `total_errors` | Suma total de errores |

La ventana es tumbling:

```text
Mensajes 1-20   -> KPI 1
Mensajes 21-40  -> KPI 2
Mensajes 41-60  -> KPI 3
```

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
docs/img/
```

Incluyen:

- fork del repositorio;
- Kafka y Zookeeper arrancados con Docker;
- topic de Kafka creado;
- productor enviando metricas;
- consumidor recibiendo, insertando y calculando KPIs;
- documentos RAW en MongoDB Atlas;
- documentos KPI en MongoDB Atlas;
- README documentado;
- tag final de entrega.

## Memoria y manual

La memoria final y el manual desde cero estan en:

```text
docs/memoria_manual_proyecto.md
docs/memoria_manual_proyecto.pdf
```

El manual documenta el proceso completo desde cero: fork, clonado, entorno virtual, dependencias, MongoDB Atlas, Kafka, topic, productor, consumidor, evidencias, problemas encontrados y entrega.

## Checklist de entrega

| Elemento | Estado |
|---|---|
| Fork del repositorio | Completado |
| Productor Kafka | Completado |
| Consumidor Kafka | Completado |
| Docker Compose con Kafka/Zookeeper | Completado |
| Topic `system-metrics-topic` | Completado |
| Insercion RAW en MongoDB Atlas | Completado |
| Calculo e insercion de KPIs | Completado |
| README documentado | Completado |
| Evidencias con capturas | Completado |
| Memoria y manual | Completado |
| Tag `v1.0-entrega` | Completado |

## Entrega

Repositorio:

```text
https://github.com/david2526IA/kafka-monitoring-lab
```

Tag final:

```text
v1.0-entrega
```

Comandos base de entrega:

```powershell
git add .
git commit -m "Implement kafka monitoring pipeline"
git push origin main
git tag v1.0-entrega
git push origin v1.0-entrega
```

Si se actualiza documentacion o evidencias despues de crear el tag, se debe mover el tag al ultimo commit:

```powershell
git tag -f v1.0-entrega
git push origin -f v1.0-entrega
```
