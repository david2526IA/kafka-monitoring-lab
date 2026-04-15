import json
import os
from datetime import datetime, timezone
from statistics import mean

import certifi
from dotenv import load_dotenv
from kafka import KafkaConsumer
from pymongo import MongoClient


NUMERIC_FIELDS = [
    "cpu_percent",
    "memory_percent",
    "disk_io_mbps",
    "network_mbps",
]


def get_int_env(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        print(f"[consumer] Invalid value for {name}. Using {default}.")
        return default


def required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def create_kafka_consumer(bootstrap_servers, topic, group_id):
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )


def create_mongo_collections():
    mongo_uri = required_env("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME", "kafka_monitoring_lab")
    raw_collection_name = os.getenv("MONGO_RAW_COLLECTION", "system_metrics_raw")
    kpi_collection_name = os.getenv("MONGO_KPI_COLLECTION", "system_metrics_kpis")

    client = MongoClient(
        mongo_uri,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000,
    )
    client.admin.command("ping")

    db = client[db_name]
    return (
        client,
        db[raw_collection_name],
        db[kpi_collection_name],
    )


def build_kpi_document(window, window_number):
    return {
        "window_number": window_number,
        "message_count": len(window),
        "window_started_at": window[0].get("timestamp"),
        "window_ended_at": window[-1].get("timestamp"),
        "calculated_at": datetime.now(timezone.utc).isoformat(),
        "servers": sorted({metric.get("server_id") for metric in window}),
        "avg_cpu_percent": round(mean(metric["cpu_percent"] for metric in window), 2),
        "avg_memory_percent": round(
            mean(metric["memory_percent"] for metric in window), 2
        ),
        "avg_disk_io_mbps": round(mean(metric["disk_io_mbps"] for metric in window), 2),
        "avg_network_mbps": round(mean(metric["network_mbps"] for metric in window), 2),
        "max_cpu_percent": max(metric["cpu_percent"] for metric in window),
        "max_memory_percent": max(metric["memory_percent"] for metric in window),
        "total_errors": sum(metric["error_count"] for metric in window),
    }


def main():
    load_dotenv()

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
    topic = os.getenv("KAFKA_TOPIC", "system-metrics-topic")
    group_id = os.getenv("KAFKA_GROUP_ID", "david2526_monitoring_group")
    window_size = get_int_env("KPI_WINDOW_SIZE", 20)

    print(f"[consumer] Kafka bootstrap servers: {bootstrap_servers}")
    print(f"[consumer] Topic: {topic}")
    print(f"[consumer] Group id: {group_id}")
    print(f"[consumer] KPI window size: {window_size}")

    mongo_client, raw_collection, kpi_collection = create_mongo_collections()
    print("[consumer] Connected to MongoDB Atlas.")

    consumer = create_kafka_consumer(bootstrap_servers, topic, group_id)
    window = []
    window_number = 0

    try:
        for message in consumer:
            metric = message.value
            raw_document = dict(metric)
            raw_document["kafka_topic"] = message.topic
            raw_document["kafka_partition"] = message.partition
            raw_document["kafka_offset"] = message.offset
            raw_document["ingested_at"] = datetime.now(timezone.utc).isoformat()

            raw_result = raw_collection.insert_one(raw_document)
            window.append(metric)

            print(
                "[consumer] Message received and inserted "
                f"server={metric.get('server_id')} "
                f"raw_id={raw_result.inserted_id} "
                f"window_count={len(window)}/{window_size}"
            )

            if len(window) == window_size:
                window_number += 1
                kpi_document = build_kpi_document(window, window_number)
                kpi_result = kpi_collection.insert_one(kpi_document)
                print(
                    "[consumer] KPI window completed "
                    f"message_count={kpi_document['message_count']} "
                    f"kpi_id={kpi_result.inserted_id}"
                )
                window.clear()
    except KeyboardInterrupt:
        print("\n[consumer] Stopped by user.")
    finally:
        consumer.close()
        mongo_client.close()


if __name__ == "__main__":
    main()
