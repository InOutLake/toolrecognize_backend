ENV_FILE ?= local.env
COMPOSE_FILE ?= docker-compose.local.yml
TESTS_DIR ?= /app/src/tests

.PHONY: start-services stop-services run-tests run-tests-full

start-services:
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d --remove-orphans postgres rabbitmq minio migrate
	@echo "Waiting for services to be healthy..."
	@sleep 10
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d adminer
	@echo "Services started successfully!"

stop-services:
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) down -v
	@echo "All services stopped."

run-tests:
	@echo "Running tests in api container..."
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) run --rm -e TEST=1 -e PYTHONPATH=/app/src api uv run python -m pytest $(TESTS_DIR) -v

run-tests-full: start-services
	@echo "Starting services and running tests..."
	@sleep 10
	+$(MAKE) run-tests
	+$(MAKE) stop-services

test: run-tests-full

start-all:
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d
	@echo "All services started including API."

stop-api:
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) stop api
	@echo "API container stopped."

logs:
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) logs -f

logs-api:
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) logs -f api

clean: stop-services
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) down -v --remove-orphans
	docker system prune -f
	@echo "Cleaned up all containers and unused resources."
