# Memoria final y manual desde cero

Proyecto: Kafka Monitoring Lab

Autor del repositorio: david2526IA

Repositorio: https://github.com/david2526IA/kafka-monitoring-lab

Tag de entrega: v1.0-entrega

Fecha de cierre: 16/04/2026

## 1. Resumen del proyecto

Este proyecto implementa un pipeline de monitorizacion de servidores usando Python, Apache Kafka, Docker y MongoDB Atlas.

El sistema simula metricas de varios servidores, las envia a Kafka en formato JSON, las consume desde Python y las guarda en MongoDB Atlas. Ademas, el consumidor calcula KPIs cada 20 mensajes y los guarda en una coleccion separada.

Flujo general:

```text
Productor Python -> Kafka -> Consumidor Python -> MongoDB Atlas
```

## 2. Objetivos cubiertos

El trabajo realizado cubre los puntos principales del enunciado:

- Crear un fork del repositorio base.
- Completar el productor Kafka.
- Completar el consumidor Kafka.
- Ejecutar Kafka y Zookeeper con Docker.
- Crear el topic `system-metrics-topic`.
- Enviar metricas simuladas de servidores.
- Insertar datos brutos en MongoDB Atlas.
- Calcular KPIs cada 20 mensajes.
- Guardar KPIs en una segunda coleccion.
- Documentar el proyecto en `README.md`.
- Guardar evidencias en `docs/evidencias.md`.
- Subir el proyecto a GitHub.
- Crear y subir el tag `v1.0-entrega`.

## 3. Arquitectura

La arquitectura final es:

```text
producer/productor_metrics.py
        |
        v
Kafka topic: system-metrics-topic
        |
        v
consumer/consumidor_metrics.py
        |
        v
MongoDB Atlas
  - system_metrics_raw
  - system_metrics_kpis
```

El productor se ejecuta en bucle continuo. Cada iteracion genera una metrica simulada y la envia a Kafka.

El consumidor tambien se ejecuta en bucle continuo. Por cada mensaje recibido:

1. Inserta el mensaje bruto en `system_metrics_raw`.
2. Acumula el mensaje en una ventana temporal de 20 registros.
3. Cuando la ventana llega a 20 mensajes, calcula KPIs.
4. Inserta el documento KPI en `system_metrics_kpis`.
5. Vacia la ventana y empieza otra.

## 4. Tecnologias usadas

- Python 3.12.
- kafka-python.
- pymongo.
- python-dotenv.
- certifi.
- Docker Desktop.
- Apache Kafka con imagen `confluentinc/cp-kafka:7.4.4`.
- Zookeeper con imagen `confluentinc/cp-zookeeper:7.4.4`.
- MongoDB Atlas.
- Git y GitHub.
- Visual Studio Code.

## 5. Estructura final del repositorio

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
  .gitignore
  README.md
  requirements.txt
```

El archivo `.env` existe solo en local y no se sube a GitHub porque contiene credenciales.

## 6. Manual desde cero

Esta seccion explica como rehacer el proyecto desde cero.

### 6.1. Crear el fork

1. Abrir el repositorio base:

```text
https://github.com/josedavidmi/kafka-monitoring-lab
```

2. Pulsar `Fork` o `Tenedor`.
3. Crear el fork en la cuenta personal de GitHub.
4. Verificar que la URL pertenece al usuario propio.

En este caso:

```text
https://github.com/david2526IA/kafka-monitoring-lab
```

### 6.2. Clonar el fork

Desde PowerShell:

```powershell
cd "C:\Users\farqu\OneDrive\Desktop\proyecto_kafka"
git clone https://github.com/david2526IA/kafka-monitoring-lab.git
cd kafka-monitoring-lab
git status
```

### 6.3. Crear entorno virtual

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 6.4. Instalar dependencias

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

### 6.5. Configurar MongoDB Atlas

1. Entrar en MongoDB Atlas.
2. Crear o usar un cluster.
3. Anadir la IP actual en `Network Access`.
4. Crear un usuario de base de datos.
5. Ir a `Connect > Drivers > Python`.
6. Copiar la cadena `mongodb+srv://...`.
7. Sustituir `<db_password>` por la contrasena real.

### 6.6. Crear el archivo `.env`

Copiar el ejemplo:

```powershell
Copy-Item .env.example .env
```

Editar `.env`:

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

Importante: no subir `.env` a GitHub.

### 6.7. Arrancar Kafka con Docker

```powershell
docker compose -f .\docker\docker-compose.yml up -d
docker ps
```

Deben aparecer:

```text
kafka-lab-broker
kafka-lab-zookeeper
```

Si aparece un error de conexion con Docker, abrir Docker Desktop y esperar a que termine de arrancar.

### 6.8. Crear el topic de Kafka

```powershell
docker compose -f .\docker\docker-compose.yml exec kafka kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic system-metrics-topic --partitions 1 --replication-factor 1
```

Comprobarlo:

```powershell
docker compose -f .\docker\docker-compose.yml exec kafka kafka-topics --bootstrap-server kafka:9092 --list
```

Debe aparecer:

```text
system-metrics-topic
```

### 6.9. Ejecutar el consumidor

En una terminal:

```powershell
.\.venv\Scripts\Activate.ps1
py .\consumer\consumidor_metrics.py
```

Salida esperada:

```text
[consumer] Kafka bootstrap servers: localhost:29092
[consumer] Topic: system-metrics-topic
[consumer] Group id: david2526_monitoring_group
[consumer] KPI window size: 20
[consumer] Connected to MongoDB Atlas.
```

### 6.10. Ejecutar el productor

En otra terminal:

```powershell
.\.venv\Scripts\Activate.ps1
$env:PRODUCER_INTERVAL_SECONDS="1"
py .\producer\productor_metrics.py
```

Salida esperada:

```text
[producer] Message sent server=web01 partition=0 offset=...
```

### 6.11. Verificar el consumidor

El consumidor debe mostrar:

```text
[consumer] Message received and inserted server=...
[consumer] KPI window completed message_count=20 kpi_id=...
```

El mensaje KPI aparece cada vez que se completan 20 mensajes.

### 6.12. Verificar MongoDB Atlas

En MongoDB Atlas, abrir `Browse Collections`.

Base de datos:

```text
kafka_monitoring_lab
```

Colecciones:

```text
system_metrics_raw
system_metrics_kpis
```

En `system_metrics_raw` deben aparecer los mensajes individuales.

En `system_metrics_kpis` deben aparecer documentos con `message_count = 20`.

## 7. Implementacion del productor

Archivo:

```text
producer/productor_metrics.py
```

El productor:

- Carga variables desde `.env`.
- Usa `KafkaProducer`.
- Genera un servidor aleatorio entre `web01`, `web02`, `db01`, `app01` y `cache01`.
- Genera metricas aleatorias:
  - `cpu_percent`
  - `memory_percent`
  - `disk_io_mbps`
  - `network_mbps`
  - `error_count`
- Incluye timestamp UTC con `datetime.now(timezone.utc)`.
- Envia los mensajes al topic `system-metrics-topic`.
- Funciona en bucle hasta que se detiene con `Ctrl + C`.

## 8. Implementacion del consumidor

Archivo:

```text
consumer/consumidor_metrics.py
```

El consumidor:

- Carga variables desde `.env`.
- Usa `KafkaConsumer`.
- Se conecta a MongoDB Atlas con `pymongo`.
- Usa `certifi` para certificados TLS.
- Inserta cada mensaje bruto en `system_metrics_raw`.
- Acumula mensajes en una lista de ventana.
- Cuando la ventana llega a 20 mensajes, calcula KPIs.
- Inserta el documento KPI en `system_metrics_kpis`.

## 9. Decision de implementacion

Se eligio implementar un unico consumidor que guarda datos RAW y calcula KPIs.

Ventajas:

- Menos scripts que ejecutar.
- Mas facil de probar.
- Flujo completo en un unico proceso.
- Suficiente para el alcance del proyecto.

Alternativa posible:

- `consumidor_raw.py` para guardar RAW.
- `consumidor_kpis.py` para calcular KPIs.

En esa alternativa, cada consumidor tendria que usar un `group_id` diferente para que ambos lean todos los mensajes.

## 10. KPIs calculados

Cada ventana de 20 mensajes genera un documento con:

- `window_number`
- `message_count`
- `window_started_at`
- `window_ended_at`
- `calculated_at`
- `servers`
- `avg_cpu_percent`
- `avg_memory_percent`
- `avg_disk_io_mbps`
- `avg_network_mbps`
- `max_cpu_percent`
- `max_memory_percent`
- `total_errors`

La ventana es tumbling:

```text
Mensajes 1-20   -> KPI 1
Mensajes 21-40  -> KPI 2
Mensajes 41-60  -> KPI 3
```

## 11. Evidencias

Las evidencias estan en:

```text
docs/evidencias.md
docs/img/
```

Capturas incluidas:

- `01_fork_github.png`: fork del repositorio.
- `02_docker_kafka_arrancado.png`: Kafka y Zookeeper corriendo.
- `03_topic_kafka_creado.png`: topic creado.
- `04_productor_enviando.png`: productor enviando mensajes.
- `05_consumidor_recibiendo.png`: consumidor recibiendo, insertando y calculando KPIs.
- `06_mongodb_raw.png`: documentos RAW en MongoDB Atlas.
- `07_mongodb_kpis.png`: documentos KPI en MongoDB Atlas.
- `08_readme.png`: README documentado.
- `09_tag_github.png`: tag final en GitHub.

## 12. Problemas encontrados y soluciones

### 12.1. PowerShell no reconoce una ruta como comando

Problema:

```text
El termino 'C:\Users\...' no se reconoce como nombre de un cmdlet
```

Solucion:

Usar `cd` para entrar en la carpeta:

```powershell
cd "C:\Users\farqu\OneDrive\Desktop\proyecto_kafka"
```

### 12.2. Docker no estaba arrancado

Problema:

```text
failed to connect to the Docker API
```

Solucion:

Abrir Docker Desktop y esperar a que el motor de Docker estuviera activo.

### 12.3. Error de autenticacion en MongoDB Atlas

Problema:

```text
bad auth : authentication failed
```

Solucion:

Revisar la cadena `MONGO_URI` y sustituir correctamente `<db_password>` por la contrasena real, sin dejar los simbolos `<` y `>`.

### 12.4. Capturas guardadas fuera del repositorio

Problema:

Las capturas se guardaron en la carpeta de Windows `Imagenes/Screenshots`, pero `docs/evidencias.md` las buscaba en `docs/img`.

Solucion:

Copiar las capturas a `docs/img` con los nombres esperados.

## 13. Comandos de entrega

Guardar cambios:

```powershell
git add .
git commit -m "Implement kafka monitoring pipeline"
git push origin main
```

Crear tag:

```powershell
git tag v1.0-entrega
git push origin v1.0-entrega
```

Si se anade una evidencia despues del tag, actualizarlo:

```powershell
git tag -f v1.0-entrega
git push origin -f v1.0-entrega
```

## 14. Estado final

Estado final del repositorio:

```text
main subido a GitHub
tag v1.0-entrega subido a GitHub
docs/evidencias.md completo
docs/img con capturas 01 a 09
README.md documentado
```

URL del repositorio:

```text
https://github.com/david2526IA/kafka-monitoring-lab
```

URL de tags:

```text
https://github.com/david2526IA/kafka-monitoring-lab/tags
```

## 15. Que entregar

Para la entrega se debe proporcionar:

1. URL del repositorio de GitHub:

```text
https://github.com/david2526IA/kafka-monitoring-lab
```

2. Confirmacion de que existe el tag:

```text
v1.0-entrega
```

3. El repositorio debe contener:

- Productor en `producer/productor_metrics.py`.
- Consumidor en `consumer/consumidor_metrics.py`.
- Docker Compose en `docker/docker-compose.yml`.
- Dependencias en `requirements.txt`.
- README en `README.md`.
- Evidencias en `docs/evidencias.md`.
- Capturas en `docs/img`.
- Memoria y manual en `docs/memoria_manual_proyecto.md`.
- PDF en `docs/memoria_manual_proyecto.pdf`.

No se debe entregar ni subir el archivo `.env`.

## 16. Checklist final

- [x] Fork creado.
- [x] Proyecto clonado.
- [x] Docker Compose corregido.
- [x] Kafka y Zookeeper arrancan.
- [x] Topic `system-metrics-topic` creado.
- [x] Productor implementado.
- [x] Consumidor implementado.
- [x] MongoDB Atlas configurado.
- [x] RAW insertado en `system_metrics_raw`.
- [x] KPIs insertados en `system_metrics_kpis`.
- [x] README documentado.
- [x] Evidencias 01 a 09 guardadas.
- [x] Commit subido a `main`.
- [x] Tag `v1.0-entrega` subido.
- [x] Memoria y manual generados.
