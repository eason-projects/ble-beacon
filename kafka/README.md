# Simple Kafka Setup with Docker Compose (KRaft Mode)

This directory contains a Docker Compose configuration for setting up a simple Kafka environment with the following components:

- Kafka broker (running in KRaft mode without Zookeeper)
- Kafka UI (web interface for managing Kafka)

## About KRaft Mode

This setup uses Kafka in KRaft (Kafka Raft) mode, which eliminates the dependency on Zookeeper. KRaft mode is the future of Kafka and will eventually replace Zookeeper as the metadata management solution.

## Prerequisites

- Docker and Docker Compose installed on your machine

## Getting Started

1. Start the Kafka environment:

```bash
docker-compose up -d
```

2. To verify that everything is running:

```bash
docker-compose ps
```

3. Access the Kafka UI at http://localhost:8080

## Connection Details

- Kafka Broker: 
  - Internal: kafka:9092
  - External: localhost:29092 (use this in your applications)

## Stopping the Environment

```bash
docker-compose down
```

## Data Persistence

Data is persisted in the following directory:
- `./kafka-data`: Kafka data

To completely reset the environment, remove this directory after stopping the containers:

```bash
docker-compose down
rm -rf ./kafka-data
```

## Troubleshooting

### Kafka UI Connection Issues

If you encounter an error like:
```
Error while creating AdminClient for Cluster local
```

This usually means that the Kafka UI is trying to connect to Kafka before Kafka is fully initialized. The current configuration includes:

1. A healthcheck for the Kafka service to ensure it's fully operational
2. A dependency configuration that makes Kafka UI wait for Kafka to be healthy

If you still encounter issues:
1. Try restarting the Kafka UI service: `docker-compose restart kafka-ui`
2. Check Kafka logs: `docker-compose logs kafka`
3. Ensure that the bootstrap server configuration is correct in both services

## Using Kafka

### Creating a Topic

```bash
docker-compose exec kafka kafka-topics --create --topic my-topic --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
```

### Listing Topics

```bash
docker-compose exec kafka kafka-topics --list --bootstrap-server kafka:9092
```

### Producing Messages

```bash
docker-compose exec kafka kafka-console-producer --topic my-topic --bootstrap-server kafka:9092
```

### Consuming Messages

```bash
docker-compose exec kafka kafka-console-consumer --topic my-topic --from-beginning --bootstrap-server kafka:9092
``` 