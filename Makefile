# Variables
COMPOSE_CMD = docker compose
APP_SERVICE = api
DB_SERVICE = db
TEST_DB_SERVICE = db-test

# Start services
run:
	$(COMPOSE_CMD) up -d --build

# Stop services
down:
	$(COMPOSE_CMD) down

# Restart services
restart:
	$(COMPOSE_CMD) restart

# Show logs
logs:
	$(COMPOSE_CMD) logs -f $(APP_SERVICE)

# Testing
test:
	$(COMPOSE_CMD) exec $(APP_SERVICE) pytest tests/ -xvs

# Shell access
enter-app:
	$(COMPOSE_CMD) exec $(APP_SERVICE) bash

enter-db:
	$(COMPOSE_CMD) exec $(DB_SERVICE) bash

enter-test-db:
	$(COMPOSE_CMD) exec $(TEST_DB_SERVICE) bash

# Database migrations
migrate-db:
	$(COMPOSE_CMD) exec $(APP_SERVICE) alembic upgrade head

# Format code
format:
	$(COMPOSE_CMD) exec $(APP_SERVICE) ./fix_imports.sh
	$(COMPOSE_CMD) exec $(APP_SERVICE) isort main.py && black main.py

# Cleaning (be careful!)
clean:
	docker system prune -f

# Generate secret key
generate-secret:
	$(COMPOSE_CMD) exec $(APP_SERVICE) python app/generate_secret_key.py

.PHONY: run down restart logs test enter-app enter-db enter-test-db migrate-db format clean generate-secret