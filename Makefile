.PHONY: up down logs shell-backend setup help

help:
	@echo "Available commands:"
	@echo "  make setup         - Run initial setup script"
	@echo "  make up            - Start all services (detached)"
	@echo "  make down          - Stop all services"
	@echo "  make logs          - View logs of all services"
	@echo "  make shell-backend - Open a shell inside the backend container"
	@echo "  make clean         - Remove containers, networks, and volumes"

setup:
	./setup.sh

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

shell-backend:
	docker compose exec backend bash

clean:
	docker compose down -v
