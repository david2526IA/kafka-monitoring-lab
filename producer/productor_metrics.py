import json
import os
import random
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from kafka import KafkaProducer


SERVERS = ["web01", "web02", "db01", "app01", "cache01"]


def get_int_env(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        print(f"[producer] Invalid value for {name}. Using {default}.")
        return default


def build_metric():
    return {
        "server_id": random.choice(SERVERS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": round(random.uniform(5.0, 95.0), 2),
        "memory_percent": round(random.uniform(10.0, 92.0), 2),
        "disk_io_mbps": round(random.uniform(1.0, 250.0), 2),
        "network_mbps": round(random.uniform(0.5, 500.0), 2),
        "error_count": random.choice([0, 0, 0, 0, 1, 1, 2, 3, 5]),
    }


def create_producer(bootstrap_servers):
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        acks="all",
        retries=5,
    )


def main():
    load_dotenv()

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
    topic = os.getenv("KAFKA_TOPIC", "system-metrics-topic")
    interval_seconds = get_int_env("PRODUCER_INTERVAL_SECONDS", 5)

    print(f"[producer] Kafka bootstrap servers: {bootstrap_servers}")
    print(f"[producer] Topic: {topic}")
    print(f"[producer] Interval seconds: {interval_seconds}")

    producer = create_producer(bootstrap_servers)

    try:
        while True:
            metric = build_metric()
            result = producer.send(topic, value=metric)
            metadata = result.get(timeout=10)
            print(
                "[producer] Message sent "
                f"server={metric['server_id']} "
                f"partition={metadata.partition} "
                f"offset={metadata.offset} "
                f"payload={metric}"
            )
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n[producer] Stopped by user.")
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()
