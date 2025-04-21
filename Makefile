# Variables
COMPOSE_CMD = docker compose
APP_SERVICE = api
DB_SERVICE = db
TEST_DB_SERVICE = db-test

format:
	./fix_imports.sh
	isort main.py && black main.py

run:
	$(COMPOSE_CMD) down --remove-orphans && $(COMPOSE_CMD) up -d --build

shutdown:
	$(COMPOSE_CMD) down

test:
	$(COMPOSE_CMD) exec $(APP_SERVICE) pytest tests/ -xvs

enter-app:
	$(COMPOSE_CMD) exec $(APP_SERVICE) bash

enter-db:
	$(COMPOSE_CMD) exec $(DB_SERVICE) bash

enter-test-db:
	$(COMPOSE_CMD) exec $(TEST_DB_SERVICE) bash

migrate-db:
	$(COMPOSE_CMD) exec $(APP_SERVICE) alembic upgrade head

clean:
	docker system prune -af

.PHONY: format run shutdown test enter-app enter-db enter-test-db migrate-db init-env clean # Declare targets as phony
