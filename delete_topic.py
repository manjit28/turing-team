#!/usr/bin/env python3
"""
delete_topic.py - Delete a Kafka topic using kafka-python.
"""

import os
import argparse
import sys
from kafka import KafkaAdminClient
from kafka.errors import KafkaError


def main():
    parser = argparse.ArgumentParser(description="Delete a Kafka topic.")
    parser.add_argument("--brokers", help="Comma‑separated broker list, e.g. localhost:9092")
    parser.add_argument("--topic", help="Topic name to delete")
    args = parser.parse_args()

    brokers = args.brokers or os.getenv("BROKER_LIST")
    topic = args.topic or os.getenv("TOPIC_NAME")

    if not brokers or not topic:
        print("Error: broker list and topic must be provided via arguments or env vars.", file=sys.stderr)
        sys.exit(1)

    bootstrap_servers = [b.strip() for b in brokers.split(",") if b.strip()]

    try:
        admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        admin.delete_topics([topic])
        print(f"Topic '{topic}' deleted successfully.")
    except KafkaError as e:
        print(f"KafkaError: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
