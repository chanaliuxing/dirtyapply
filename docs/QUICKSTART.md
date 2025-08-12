# Apply-Copilot Quick Start Guide

Get your Job-Driven Resume Rewriter & Auto-Apply Agent running in minutes!

## 🚀 Prerequisites

- **Python 3.11+** installed and accessible via `python` command
- **Node.js 20+** with `pnpm` package manager (`npm install -g pnpm`)
- **Docker & Docker Compose** for infrastructure services
- **Chrome Browser** for extension testing
- **Tesseract OCR** for automation features (optional but recommended)

## ⚡ Quick Setup (5 Minutes)

### 1. Clone and Setup Environment

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd apply-copilot

# Copy environment template and configure
cp .env.example .env

# Edit .env with your configuration
# REQUIRED: Set COMPANION_TOKEN and SECRET_KEY to secure random values
# OPTIONAL: Add API keys for LLM providers (OpenAI, Anthropic, DeepSeek)
```

### 2. Install Dependencies

```bash
# Install all dependencies
make install
```

### 3. Start Infrastructure

```bash
# Start PostgreSQL, MinIO, and Redis
make up

# This will:
# - Start Docker containers
# - Run database migrations
# - Create MinIO buckets
# - Validate environment configuration
```

### 4. Start Development Services

Open **3 separate terminals** and run:

**Terminal 1 - API Backend:**
```bash
make dev-api
```

**Terminal 2 - Local Companion:**
```bash
make dev-companion
```

**Terminal 3 - Mock ATS (for testing):**
```bash
make dev-mock-ats
```

### 5. Verify Installation

```bash
# Run full end-to-end validation
make ready

# This will:
# - Start all services
# - Run comprehensive tests
# - Validate system integration
# - Show next steps for Chrome extension
```

## 🧪 Test the System

### Option A: Command Line Interface

```bash
# Generate a tailored resume from sample data
make jtr RESUME=samples/resume.json JD=samples/jd.txt

# Generate an action plan for form filling
make plan FIELDS=samples/fields.json
```

### Option B: Chrome Extension (Coming Soon)

1. Build the extension: `make build-ext`
2. Load `apps/extension/dist` in Chrome (chrome://extensions/)
3. Open mock ATS page: http://localhost:3000/mock-ats/greenhouse
4. Use the side panel to analyze jobs and fill forms

## 📊 Service Endpoints

Once running, you can access:

- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Companion Health**: http://localhost:8765/health
- **Mock ATS Pages**: http://localhost:3000/mock-ats/
- **MinIO Console**: http://localhost:9001 (admin/password from .env)

## 🔧 Configuration

### Required Environment Variables

```bash
# Security (REQUIRED - generate secure random tokens)
COMPANION_TOKEN=your-secure-32-char-minimum-companion-token
SECRET_KEY=your-secure-32-char-minimum-secret-key

# Database (REQUIRED)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/apply_copilot
```

### Optional AI Configuration

```bash
# AI Provider (optional - defaults to rule-based mode)
LLM_PROVIDER=none  # Options: none, openai, anthropic, deepseek, deepseek-nvidia

# API Keys (only needed if using AI providers)
OPENAI_API_KEY=sk-your-openai-api-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
DEEPSEEK_API_KEY=your-deepseek-key
DEEPSEEK_NVIDIA_API_KEY=nvapi-your-nvidia-key  # For DeepSeek R1 via NVIDIA
```

## 🛡️ Security Features

Apply-Copilot implements strict security controls:

### ✅ Built-in Safeguards
- **No Hard-coded Secrets**: All credentials from environment variables
- **Fail-Fast Validation**: Startup fails immediately on configuration errors
- **Safe Logging**: API keys and tokens are automatically masked in logs
- **Local-Only Companion**: Automation service restricted to 127.0.0.1
- **Token Authentication**: All service communication secured

### ✅ RS (Reasoned Synthesis) Compliance
- **Evidence-Based Only**: All resume enhancements backed by evidence
- **Employer/Time Constraints**: No modification outside original context
- **Risk Assessment**: Every change evaluated for safety level
- **Audit Trail**: Complete tracking of all AI modifications

## 📝 Common Commands

```bash
# Development
make dev            # Show all development server commands
make install        # Install all dependencies
make up             # Start infrastructure services
make down           # Stop all services

# Testing & Quality
make test           # Run all unit/integration tests
make e2e            # Run end-to-end tests with Playwright
make lint           # Run code linters
make format         # Format all code
make security-check # Scan for hard-coded secrets

# Building
make build          # Build all applications
make package-ext    # Package Chrome extension

# Database
make migrate        # Run database migrations
make seed           # Seed with sample data
make db-reset       # Reset database (DESTROYS DATA)

# Utilities
make clean          # Clean build artifacts
make logs           # Show service logs
make ready          # Full system validation
```

## 🚨 Troubleshooting

### Environment Issues
```bash
# Validate configuration
make validate-env

# Check for hard-coded secrets
make security-check
```

### Service Issues
```bash
# Check service health
curl http://localhost:8000/health    # API
curl http://localhost:8765/health    # Companion

# View logs
make logs

# Restart everything
make restart
```

### Database Issues
```bash
# Reset database (WARNING: destroys data)
make db-reset

# Check migrations
cd apps/api && python -m alembic current
```

## 🎯 Next Steps

Once everything is running:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test CLI Tools**: Try `make jtr RESUME=samples/resume.json JD=samples/jd.txt`
3. **Build Extension**: Run `make build-ext` and load in Chrome
4. **Read Documentation**: Check `docs/` folder for detailed guides
5. **Run Tests**: Execute `make e2e` for full system validation

## 📚 Additional Resources

- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **RS Rules**: [docs/RS_RULES.md](docs/RS_RULES.md)
- **ATS Optimization**: [docs/ATS_CHECKLIST.md](docs/ATS_CHECKLIST.md)
- **Test Plan**: [docs/TESTPLAN.md](docs/TESTPLAN.md)
- **Roadmap**: [ROADMAP.md](ROADMAP.md)

---

## ✅ Success Validation

If everything is working correctly, you should see:

```bash
$ make ready
✅ Environment validation passed
✅ Infrastructure services started
✅ Database migrations completed  
✅ All services healthy
✅ E2E tests passed
🎉 ✅ READY: Apply-Copilot is fully operational!
```

**Built with ❤️ for job seekers who value efficiency and ethics.**