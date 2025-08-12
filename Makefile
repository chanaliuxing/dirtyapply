# Apply-Copilot Development Makefile
# Usage: make <target>

.PHONY: help up down restart logs clean install test e2e lint format type-check
.PHONY: dev-api dev-companion dev-ext dev-mock-ats
.PHONY: build build-ext package-ext
.PHONY: seed migrate db-reset
.PHONY: security-check validate-env
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help: ## Show this help message
	@echo "$(CYAN)Apply-Copilot Development Commands$(RESET)"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(YELLOW)Quick Start:$(RESET)"
	@echo "  1. cp .env.example .env"
	@echo "  2. Edit .env with your configuration"
	@echo "  3. make install"
	@echo "  4. make up"
	@echo "  5. make dev-companion (in separate terminal)"
	@echo "  6. make e2e"

#==============================================================================
# ENVIRONMENT & VALIDATION
#==============================================================================

validate-env: ## Validate environment configuration
	@echo "$(CYAN)Validating environment configuration...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(RED)ERROR: .env file not found. Copy .env.example to .env$(RESET)"; \
		exit 1; \
	fi
	@cd apps/api && python -c "from app.core.config import validate_environment; validate_environment()"
	@echo "$(GREEN)✅ Environment validation passed$(RESET)"

security-check: ## Check for security issues and secrets
	@echo "$(CYAN)Running security checks...$(RESET)"
	@echo "Checking for hard-coded secrets..."
	@if grep -r "sk-[a-zA-Z0-9]" --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=node_modules apps/ packages/; then \
		echo "$(RED)❌ Hard-coded API keys detected!$(RESET)"; \
		exit 1; \
	fi
	@if grep -r "bearer.*[a-zA-Z0-9]" --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=node_modules apps/ packages/; then \
		echo "$(RED)❌ Hard-coded bearer tokens detected!$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ No hard-coded secrets found$(RESET)"

#==============================================================================
# INSTALLATION & SETUP
#==============================================================================

install: ## Install all dependencies
	@echo "$(CYAN)Installing dependencies...$(RESET)"
	@if ! command -v pnpm > /dev/null; then \
		echo "$(RED)ERROR: pnpm not found. Install with: npm install -g pnpm$(RESET)"; \
		exit 1; \
	fi
	@if ! command -v python3 > /dev/null; then \
		echo "$(RED)ERROR: python3 not found. Install Python 3.11+$(RESET)"; \
		exit 1; \
	fi
	pnpm install
	cd apps/api && pip install -r requirements.txt
	cd apps/companion && pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

#==============================================================================
# INFRASTRUCTURE & SERVICES
#==============================================================================

up: validate-env ## Start all infrastructure services
	@echo "$(CYAN)Starting infrastructure services...$(RESET)"
	docker-compose -f infra/docker-compose.yml up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@make migrate
	@echo "$(GREEN)✅ Infrastructure services started$(RESET)"
	@echo "Services running:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - MinIO: localhost:9000 (console: localhost:9001)"
	@echo "  - Redis: localhost:6379"

down: ## Stop all services
	@echo "$(CYAN)Stopping all services...$(RESET)"
	docker-compose -f infra/docker-compose.yml down
	@echo "$(GREEN)✅ All services stopped$(RESET)"

restart: down up ## Restart all services

logs: ## Show service logs
	docker-compose -f infra/docker-compose.yml logs -f

#==============================================================================
# DATABASE OPERATIONS
#==============================================================================

migrate: ## Run database migrations
	@echo "$(CYAN)Running database migrations...$(RESET)"
	cd apps/api && python -m alembic upgrade head
	@echo "$(GREEN)✅ Database migrations completed$(RESET)"

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all database data!$(RESET)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose -f infra/docker-compose.yml down -v
	docker-compose -f infra/docker-compose.yml up -d postgres
	@sleep 5
	@make migrate
	@echo "$(GREEN)✅ Database reset completed$(RESET)"

seed: ## Seed database with sample data
	@echo "$(CYAN)Seeding database with sample data...$(RESET)"
	cd apps/api && python -m app.cli seed
	@echo "$(GREEN)✅ Database seeded$(RESET)"

#==============================================================================
# DEVELOPMENT SERVERS
#==============================================================================

dev-api: validate-env ## Start API development server
	@echo "$(CYAN)Starting API development server...$(RESET)"
	cd apps/api && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-companion: validate-env ## Start companion service (requires GUI)
	@echo "$(CYAN)Starting companion service...$(RESET)"
	@echo "$(YELLOW)Note: This requires GUI access for automation$(RESET)"
	cd apps/companion && python main.py

dev-ext: ## Start extension development server
	@echo "$(CYAN)Starting extension development server...$(RESET)"
	cd apps/extension && pnpm run dev

dev-mock-ats: ## Start mock ATS development server
	@echo "$(CYAN)Starting mock ATS server...$(RESET)"
	cd apps/mock-ats && pnpm run dev

dev: ## Start all development servers (use separate terminals)
	@echo "$(CYAN)Development servers:$(RESET)"
	@echo "Run these commands in separate terminals:"
	@echo "  make dev-api"
	@echo "  make dev-companion"
	@echo "  make dev-ext" 
	@echo "  make dev-mock-ats"

#==============================================================================
# BUILDING & PACKAGING
#==============================================================================

build: ## Build all applications
	@echo "$(CYAN)Building all applications...$(RESET)"
	pnpm run build
	cd apps/api && python -m pip install --upgrade pip
	@echo "$(GREEN)✅ Build completed$(RESET)"

build-ext: ## Build Chrome extension
	@echo "$(CYAN)Building Chrome extension...$(RESET)"
	cd apps/extension && pnpm run build
	@echo "$(GREEN)✅ Extension built in apps/extension/dist$(RESET)"

package-ext: build-ext ## Package extension for Chrome Web Store
	@echo "$(CYAN)Packaging Chrome extension...$(RESET)"
	cd apps/extension && pnpm run package
	@echo "$(GREEN)✅ Extension packaged as extension.zip$(RESET)"

#==============================================================================
# TESTING (TDD METHODOLOGY)
#==============================================================================

test-unit: ## Run unit tests only (fast)
	@echo "$(CYAN)Running unit tests...$(RESET)"
	cd apps/api && python -m pytest --maxfail=1 -q -m "not integration and not e2e"
	cd apps/companion && python -m pytest --maxfail=1 -q -m "not integration and not e2e"
	@echo "$(GREEN)✅ Unit tests passed$(RESET)"

test-integration: up ## Run integration tests (requires services)
	@echo "$(CYAN)Running integration tests...$(RESET)"
	cd apps/api && python -m pytest --maxfail=1 -q -m "integration"
	cd apps/companion && python -m pytest --maxfail=1 -q -m "integration"
	@echo "$(GREEN)✅ Integration tests passed$(RESET)"

test-e2e: ## Run end-to-end tests with Playwright
	@echo "$(CYAN)Running end-to-end tests...$(RESET)"
	@echo "Installing Playwright browsers..."
	cd apps/e2e && pnpm install && npx playwright install --with-deps
	@echo "Running E2E tests..."
	cd apps/e2e && npx playwright test --reporter=list
	@echo "$(GREEN)✅ E2E tests passed$(RESET)"

test-e2e-headed: ## Run E2E tests with browser visible
	@echo "$(CYAN)Running E2E tests (headed mode)...$(RESET)"
	cd apps/e2e && npx playwright test --headed

test-e2e-debug: ## Run E2E tests in debug mode
	@echo "$(CYAN)Running E2E tests (debug mode)...$(RESET)"
	cd apps/e2e && npx playwright test --debug

test: security-check test-unit test-integration ## Run all tests (TDD workflow)
	@echo "$(GREEN)🎉 ✅ ALL TESTS PASSED - TDD WORKFLOW COMPLETE$(RESET)"

test-tdd: ## Run TDD workflow: unit -> integration -> e2e
	@echo "$(CYAN)Running complete TDD workflow...$(RESET)"
	@make test-unit
	@make test-integration  
	@make test-e2e
	@echo "$(GREEN)🎉 ✅ COMPLETE TDD WORKFLOW PASSED$(RESET)"

test-coverage: ## Run tests with coverage report
	@echo "$(CYAN)Running tests with coverage...$(RESET)"
	cd apps/api && python -m pytest --cov=app --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/$(RESET)"

test-watch: ## Run tests in watch mode (for development)
	@echo "$(CYAN)Running tests in watch mode...$(RESET)"
	cd apps/api && python -m pytest --maxfail=1 -q --looponfail

test-specific: ## Run specific test file (usage: make test-specific FILE=test_config.py)
	@echo "$(CYAN)Running specific test: $(FILE)$(RESET)"
	cd apps/api && python -m pytest --maxfail=1 -v $(FILE)

test-failed: ## Re-run only failed tests
	@echo "$(CYAN)Re-running failed tests...$(RESET)"
	cd apps/api && python -m pytest --maxfail=1 -q --lf

#==============================================================================
# CODE QUALITY
#==============================================================================

lint: ## Run linters
	@echo "$(CYAN)Running linters...$(RESET)"
	pnpm run lint
	cd apps/api && python -m ruff check .
	cd apps/companion && python -m ruff check .
	@echo "$(GREEN)✅ Linting passed$(RESET)"

format: ## Format code
	@echo "$(CYAN)Formatting code...$(RESET)"
	pnpm run --recursive format
	cd apps/api && python -m black .
	cd apps/companion && python -m black .
	@echo "$(GREEN)✅ Code formatted$(RESET)"

type-check: ## Run type checking
	@echo "$(CYAN)Running type checks...$(RESET)"
	pnpm run type-check
	cd apps/api && python -m mypy app/ || true
	@echo "$(GREEN)✅ Type checking completed$(RESET)"

#==============================================================================
# CLI TOOLS
#==============================================================================

jtr: ## Generate JTR output from CLI (usage: make jtr RESUME=path/to/resume.json JD=path/to/jd.txt)
	@echo "$(CYAN)Generating Job-Tailored Resume...$(RESET)"
	cd apps/api && python -m app.cli jtr --resume $(RESUME) --jd $(JD) --out ./output/

plan: ## Generate action plan from CLI (usage: make plan FIELDS=path/to/fields.json)
	@echo "$(CYAN)Generating action plan...$(RESET)"
	cd apps/api && python -m app.cli plan --fields $(FIELDS) --out ./output/

#==============================================================================
# CLEANUP
#==============================================================================

clean: ## Clean all build artifacts and caches
	@echo "$(CYAN)Cleaning build artifacts...$(RESET)"
	rm -rf apps/*/dist apps/*/build apps/*/.next
	rm -rf apps/*/node_modules
	rm -rf apps/*/__pycache__ apps/*/**/__pycache__
	rm -rf apps/*/.pytest_cache
	rm -rf *.log apps/*/*.log
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

clean-data: ## Clean all persistent data (WARNING: destroys data)
	@echo "$(RED)WARNING: This will destroy all persistent data!$(RESET)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose -f infra/docker-compose.yml down -v
	rm -rf .data/
	@echo "$(GREEN)✅ Data cleanup completed$(RESET)"

#==============================================================================
# PRODUCTION DEPLOYMENT
#==============================================================================

prod-check: security-check validate-env ## Pre-production validation
	@echo "$(CYAN)Running production readiness checks...$(RESET)"
	@if grep -q "DEBUG=true" .env; then \
		echo "$(RED)❌ DEBUG=true not allowed in production$(RESET)"; \
		exit 1; \
	fi
	@if grep -q "DISABLE_AUTH=true" .env; then \
		echo "$(RED)❌ DISABLE_AUTH=true not allowed in production$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Production checks passed$(RESET)"

#==============================================================================
# DOCUMENTATION
#==============================================================================

docs: ## Generate documentation
	@echo "$(CYAN)Generating documentation...$(RESET)"
	@echo "API documentation available at: http://localhost:8000/docs"
	@echo "Architecture docs: ./docs/ARCHITECTURE.md"
	@echo "RS Rules: ./docs/RS_RULES.md"
	@echo "ATS Checklist: ./docs/ATS_CHECKLIST.md"

#==============================================================================
# QUICK VALIDATION
#==============================================================================

ready: up dev-companion e2e ## Full validation - ensure system is ready
	@echo "$(GREEN)🎉 ✅ READY: Apply-Copilot is fully operational!$(RESET)"
	@echo ""
	@echo "$(CYAN)Next steps:$(RESET)"
	@echo "1. Load extension dist into Chrome (chrome://extensions/)"
	@echo "2. Open http://localhost:3000/mock-ats/greenhouse"
	@echo "3. Open side panel and click 'Analyze'"
	@echo "4. Click 'Fill' to test form automation"
	@echo "5. Optionally click 'Auto-Submit' if whitelisted"