#!/bin/bash

# Stop and remove containers
echo "Stopping and removing Kafka containers..."
docker-compose down

# Remove Kafka data
echo "Removing Kafka data..."
rm -rf ./kafka-data

# Start fresh
echo "Starting Kafka with a fresh environment..."
docker-compose up -d

echo "Done! Kafka should be starting with a fresh environment."
echo "Check logs with: docker-compose logs -f" 