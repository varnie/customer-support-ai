DOCKER-COMPOSE-FILE=./docker-compose.yml
NOW := $(shell date +%Y-%m-%d_%H%M%S)
BACKUP_DIR=backups
BACKUP_FILE=$(BACKUP_DIR)/backup_$(NOW).sql

up:
	docker compose -f ${DOCKER-COMPOSE-FILE} up -d

down:
	@docker compose -f ${DOCKER-COMPOSE-FILE} stop

build: down
	@docker compose -f ${DOCKER-COMPOSE-FILE} build --no-cache --force-rm

db-migrate:
	@read -p "Enter migration comment: " comment; \
	docker compose exec web alembic revision --autogenerate -m "$$comment"

db-upgrade:
	@docker compose exec web alembic upgrade head

psql:
	@docker compose exec db psql -U user supportdb


submit-ticket:
	curl -X POST http://localhost:8000/ticket \
	-H "Content-Type: application/json" \
	-d "{\"subject\": \"Cannot access my account\", \"body\": \"I've been trying to log in for the past hour but keep getting an 'invalid credentials' error.\", \"customer_email\": \"user@example.com\"}"

list-tickets:
	curl -X GET http://localhost:8000/tickets

process-tickets:
	curl -X POST http://localhost:8000/process

test:
	@echo "Running Pytest"
	@docker compose exec web sh -c "PYTHONPATH=/app pytest"
