.PHONY: help run docker-build docker-run docker-stop clean venv install lint format test tree init

# Image tag
TAG ?= social-network-api:latest
REGISTRY ?= your-registry/social-network

help:
	@echo "Social Network Recommendation System - Available Commands:"
	@echo ""
	@echo "  make help           Show this help message"
	@echo "  make init           Initialize project (copy .env, create dirs)"
	@echo "  make venv           Create local virtualenv (.venv)"
	@echo "  make install        Install requirements into .venv"
	@echo "  make run            Run FastAPI locally on :8000"
	@echo "  make docker-build   Build Docker image (TAG=$(TAG))"
	@echo "  make docker-run     Start all services with docker-compose"
	@echo "  make docker-stop    Stop all services"
	@echo "  make test           Run pytest with coverage"
	@echo "  make lint           Run pylint on app/"
	@echo "  make format         Run black code formatter"
	@echo "  make clean          Remove caches and temp files"
	@echo "  make tree           Show project tree structure"
	@echo "  make seed-data      Run data ingestion script"
	@echo "  make logs           Show docker-compose logs"
	@echo "  make health         Check health of all services"
	@echo ""

init:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env from .env.example"; \
	else \
		echo ".env already exists"; \
	fi
	@mkdir -p nginx/ssl
	@echo "Project initialized"

venv:
	@if [ ! -d ".venv" ]; then \
		python3 -m venv .venv; \
		. .venv/bin/activate && pip install --upgrade pip; \
		echo "Created .venv"; \
	else \
		echo ".venv already exists"; \
	fi
	@echo "To activate: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)"

install: venv
	@. .venv/bin/activate && pip install -r requirements.txt
	@echo "Dependencies installed"

run:
	@if [ ! -f .env ]; then echo "Error: .env not found. Run 'make init' first."; exit 1; fi
	@. .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t $(TAG) .
	@echo "Image built: $(TAG)"

docker-push: docker-build
	docker tag $(TAG) $(REGISTRY):latest
	docker push $(REGISTRY):latest
	@echo "Image pushed to $(REGISTRY):latest"

docker-run:
	@if [ ! -f .env ]; then echo "Error: .env not found. Run 'make init' first."; exit 1; fi
	docker-compose up -d
	@echo ""
	@echo "Services started. Access points:"
	@echo "  - Neo4j Browser: http://localhost:7474"
	@echo "  - FastAPI Swagger: http://localhost:8000/docs"
	@echo "  - Nginx Proxy: http://localhost"
	@echo ""
	@echo "Run 'make logs' to view logs"

docker-stop:
	docker-compose down
	@echo "All services stopped"

docker-clean:
	docker-compose down -v
	@echo "All services stopped and volumes removed"

logs:
	docker-compose logs -f

health:
	@echo "Checking service health..."
	@echo ""
	@echo "Neo4j (bolt://localhost:7687):"
	@docker exec social-network-neo4j cypher-shell -u neo4j -p password123 "RETURN 'Neo4j is healthy' AS status" 2>/dev/null || echo "  ❌ Not responding"
	@echo ""
	@echo "FastAPI (http://localhost:8000/health):"
	@curl -s http://localhost:8000/health || echo "  ❌ Not responding"
	@echo ""
	@echo "Nginx (http://localhost/health):"
	@curl -s http://localhost/health || echo "  ❌ Not responding"
	@echo ""

seed-data:
	@if [ ! -f .env ]; then echo "Error: .env not found. Run 'make init' first."; exit 1; fi
	@. .venv/bin/activate && python scripts/seed_data.py
	@echo "Data seeding complete"

test:
	@. .venv/bin/activate && pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@. .venv/bin/activate && pylint app/ --rcfile=.pylintrc || true
	@echo ""
	@echo "Lint check complete"

format:
	@. .venv/bin/activate && black app/ tests/ scripts/ --line-length 120
	@echo "Code formatting complete"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned cache and temporary files"

tree:
	@if command -v tree >/dev/null 2>&1; then \
		tree -L 3 -I "node_modules|dist|.git|.venv|__pycache__|htmlcov|.pytest_cache|*.egg-info"; \
	else \
		find . -maxdepth 3 -type d -not -path '*/\.*' -not -path '*/__pycache__' -not -path '*/htmlcov' | sort; \
	fi
