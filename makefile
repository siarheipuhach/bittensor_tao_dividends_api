# Makefile for running tests inside Docker container

.PHONY: up down build logs shell test

# Start services
up:
	docker compose up -d

# Stop services
down:
	docker compose down

# Build Docker images
build:
	docker compose build

# View logs
logs:
	docker compose logs -f

# Open a shell inside the API container
shell:
	docker compose exec api /bin/bash

# Run tests inside the API container
test:
	docker compose up -d
	docker compose exec api pytest --disable-warnings -v
