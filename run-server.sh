#!/bin/bash

check_success() {
    if [ $? -ne 0 ]; then
        echo "Error occurred: $1"
        exit 1
    fi
}

GANACHE_ACCOUNTS_FILE="./docker-config/ganache-data/ganache-accounts.json"


echo "Starting Docker Compose..."
cd ./docker-config
docker-compose up -d

python3 server.py
check_success "Failed to start server.py."

echo "All processes completed successfully."
