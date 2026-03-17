#!/usr/bin/env python3
"""
delete_topic.py

Deletes a Kafka topic using kafka-python.

Usage:
    python delete_topic.py --brokers localhost:9092 --topic my_topic
    or set BROKER_LIST and TOPIC_NAME env vars.
"""

import os
import sys
import argparse
from kafka import KafkaAdminClient
from kafka.errors import KafkaError

def main():
    parser = argparse.ArgumentParser(description="Delete a Kafka topic.")
    parser.add_argument("--brokers", help="Comma‑separated broker list")
    parser.add_argument("--topic", help="Topic name to delete")
    args = parser.parse_args()

    brokers = args.brokers or os.getenv("BROKER_LIST")
    topic = args.topic or os.getenv("TOPIC_NAME")

    if not brokers or not topic:
        print("Error: broker list and topic name must be specified via CLI or env vars.", file=sys.stderr)
        sys.exit(1)

    broker_list = [b.strip() for b in brokers.split(",") if b.strip()]

    try:
        admin = KafkaAdminClient(bootstrap_servers=broker_list)
        admin.delete_topics([topic])
        print(f"Topic '{topic}' deleted successfully.")
    except KafkaError as e:
        print(f"Kafka error while deleting topic '{topic}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
