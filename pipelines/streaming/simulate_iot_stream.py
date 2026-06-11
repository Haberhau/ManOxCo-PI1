import argparse
import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

PLANTS = [
    {"name": "Madrid",    "max_daily": 4.0,  "efficiency": 0.745},
    {"name": "Barcelona", "max_daily": 4.1,  "efficiency": 0.733},
    {"name": "Zaragoza",  "max_daily": 3.5,  "efficiency": 0.865},
    {"name": "Alicante",  "max_daily": 3.4,  "efficiency": 0.880},
    {"name": "Gijon",     "max_daily": 3.0,  "efficiency": 0.900},
]

HOSPITALS = [
    {"name": "Doce De Octubre",  "city": "Madrid",    "plant": "Madrid",    "avg_cons": 0.027},
    {"name": "Gregorio Maranon", "city": "Madrid",    "plant": "Madrid",    "avg_cons": 0.028},
    {"name": "Infanta Sofia",    "city": "Madrid",    "plant": "Madrid",    "avg_cons": 0.026},
    {"name": "San Carlos",       "city": "Madrid",    "plant": "Madrid",    "avg_cons": 0.025},
    {"name": "Vall Hebron",      "city": "Barcelona", "plant": "Barcelona", "avg_cons": 0.031},
    {"name": "Clinic",           "city": "Barcelona", "plant": "Barcelona", "avg_cons": 0.029},
    {"name": "Miguel Servet",    "city": "Zaragoza",  "plant": "Zaragoza",  "avg_cons": 0.024},
    {"name": "General Alicante", "city": "Alicante",  "plant": "Alicante",  "avg_cons": 0.022},
]


def make_producer(broker: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=broker,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
    )


def production_reading(plant: dict) -> dict:
    noise = random.gauss(0, 0.05)
    effective_rate = plant["max_daily"] * plant["efficiency"] * (1 + noise) / 1440  # per-minute
    return {
        "event_time": datetime.utcnow().isoformat(),
        "plant": plant["name"],
        "production_rate_tons_per_min": round(max(0, effective_rate), 6),
        "sensor_ok": random.random() > 0.005,  # 0.5% sensor fault rate
    }


def consumption_reading(hospital: dict) -> dict:
    noise = random.gauss(0, 0.08)
    rate = hospital["avg_cons"] * (1 + noise) / 1440  # per-minute
    return {
        "event_time": datetime.utcnow().isoformat(),
        "hospital_name": hospital["name"],
        "hospital_city": hospital["city"],
        "plant": hospital["plant"],
        "consumption_tons_per_min": round(max(0, rate), 8),
    }


def run(broker: str, rate_seconds: int):
    producer = make_producer(broker)
    print(f"[STREAM] Producing to {broker}, interval={rate_seconds}s")

    while True:
        for plant in PLANTS:
            msg = production_reading(plant)
            producer.send(
                "manoxco.iot.production",
                key=plant["name"],
                value=msg,
            )

        for hospital in HOSPITALS:
            msg = consumption_reading(hospital)
            producer.send(
                "manoxco.iot.consumption",
                key=hospital["name"],
                value=msg,
            )

        producer.flush()
        print(f"[STREAM] {datetime.utcnow().isoformat()} - batch sent")
        time.sleep(rate_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate-seconds", type=int, default=60)
    parser.add_argument("--kafka-broker", default="localhost:9092")
    args = parser.parse_args()
    run(args.kafka_broker, args.rate_seconds)
