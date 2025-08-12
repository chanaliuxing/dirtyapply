# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Testing Playbook (IMPORTANT)

### Test Types & Commands
- **Unit Tests**: `python -m pytest --maxfail=1 -q`
- **Integration Tests**: `docker compose up -d && pytest -q -m "int"`
- **E2E Tests (Web)**: `npx playwright test --reporter=list`
- **All Tests**: `npm run test`

### TDD Workflow (MANDATORY)
1. **Write/refresh tests FIRST** (Test-Driven Development)
2. **Run tests and confirm failures** before writing any code
3. **Implement minimal fix** to make tests pass
4. **Re-run tests** to verify success
5. **Repeat until ALL tests pass** - DO NOT relax test requirements

### Critical Testing Rules
- ✅ **Always start with failing tests** - confirms test validity
- ✅ **Run tests after every change** - catch regressions immediately
- ✅ **Use `--maxfail=1`** - stop on first failure for faster feedback
- ✅ **Write assertions BEFORE implementation** - forces clear requirements
- ❌ **NEVER skip tests** - all functionality must be tested
- ❌ **NEVER relax passing tests** - maintain quality standards

### Acceptance Criteria in Tests
Encode real-world success criteria:
- Form fields filled with correct data
- API responses return expected status codes
- Confirmation pages display success messages
- Screenshots match expected UI states
- Database changes persist correctly

## Project Overview - Apply-Copilot

**Apply-Copilot** is a Job-Driven Resume Rewriter & Auto-Apply Agent system implementing the "职位→简历重写（JTR）+ ATS 优化 + 自动填表/提交" specification with **Reasoned Synthesis (RS)** capabilities.

### Architecture (Monorepo Structure)
```
apply-copilot/
  apps/
    extension/           # Chrome MV3 + React + TypeScript + Side Panel
    api/                 # FastAPI backend (JTR, Planner, Artifacts)
    companion/           # Local HTTP server + PyAutoGUI + OCR
    mock-ats/            # Static server for Greenhouse/Lever/Workday mocks
    e2e/                 # Playwright tests
  packages/
    core/                # Shared schemas (Zod/Pydantic), ATS dictionary
  infra/
    docker-compose.yml   # Postgres, MinIO services
```

## Key Commands

### Development Setup
```bash
# Start infrastructure and API
make up

# Start local companion (needs GUI access)
make dev-companion

# Start extension development server
make dev-ext

# Run all tests
make test

# Run end-to-end tests
make e2e

# Build extension package
make package-ext
```

### CLI Tools
```bash
# Generate tailored resume from CLI
python -m api.cli jtr --resume samples/resume.json --jd samples/jd.txt --out out/

# Generate action plan from fields
python -m api.cli plan --fields samples/fields.json --out out/
```

### Service Ports
- **API Backend**: `8000`
- **Local Companion**: `8765` (127.0.0.1 only)
- **Web UI**: `5173`
- **Mock ATS**: Various ports

## Technology Stack

### Frontend (Extension)
- **Chrome MV3** with React + TypeScript + Vite
- **Side Panel**: Match scores, resume preview, diff viewer with RS badges
- **Content Scripts**: JD extraction, field detection, Shadow DOM handling
- **Service Worker**: Domain whitelist, backend orchestration

### Backend (API)
- **FastAPI** with Python 3.11
- **JTR Engine**: Job-Driven Resume Tailoring with RS compliance
- **Action Planner**: Generate field-filling strategies per ATS site
- **Artifacts**: ATS-optimized DOCX/PDF generation
- **Mock LLM**: Rule-based offline mode, pluggable OpenAI/DeepSeek/DeepSeek-NVIDIA/Anthropic

### Local Companion
- **HTTP Server**: `127.0.0.1:8765` with token auth
- **PyAutoGUI**: Mouse/keyboard automation
- **Tesseract OCR**: Text recognition for UI elements
- **Screen Coordination**: CSS→screen coordinate conversion

### Database & Storage
- **PostgreSQL 14**: Primary data storage
- **MinIO**: Artifact storage (fallback to local disk)
- **Redis**: Optional caching

## Core Concepts

### JTR (Job-Driven Tailoring)
- **Input Schema**: resume_profile_id, evidence_vault, job details, user_profile
- **Output Schema**: match_score, tailored_resume, qa_bundle, diff_report, action_plan
- **ATS Optimization**: keyword alignment, placement weighting, recency boost

### RS (Reasoned Synthesis) Rules
**ALLOWED** within original employer + job title + time window:
- Reasonable completion of achievements with evidence backing
- Metric ranges/approximations (~15-20%)
- Skill emphasis based on job requirements

**FORBIDDEN**:
- Adding new employers/titles/degrees/certifications
- Changing dates or locations
- Claiming sole leadership without basis
- Fabricating exact metrics without evidence

### Action Plan Strategy (Fill Order)
1. **DOM first**: `value` + `input/change` events including React/Vue/AntD
2. **Keys/Mouse**: Via Local Companion with coordinate conversion
3. **OCR**: Locate buttons with confirmation dialogs
4. **Playwright**: Fallback for mock-ats testing

## Testing Strategy

### Unit Tests
- RS validator rejects illegal changes, accepts legal RS with ranges
- ATS optimizer ensures Must keywords appear in ≥2 sections
- Action planner validity for mock JDs

### Integration Tests
- FastAPI endpoints return valid schemas
- JTR pipeline produces compliant outputs
- Action plans work against mock ATS pages

### E2E Tests (Playwright)
- Full application flow against mock Greenhouse/Lever/Workday
- Content script emulation with backend + companion
- Assert "Application submitted" success markers

## Safety & Compliance

### Built-in Guardrails
- **RS Guard**: Unit tests fail on illegal resume modifications
- **ATS Guard**: Must keywords validated in ≥2 sections
- **Action Plan Guard**: Wait conditions required for multi-step flows
- **E2E Guard**: Complete application flow validation

### Security Constraints
- Domain whitelist enforcement
- Human confirmation required for submissions
- Local companion token authentication
- Evidence-based modifications only

## Golden Rules (Must Implement)

### Security & Configuration
- **No Hard-coded Secrets**: Never embed tokens, API keys, or credentials in code, tests, fixtures, or documentation
- **Single Config Module**: Use centralized configuration management, no scattered environment conditionals across the app
- **12-Factor Config**: `.env` for local/dev only; production uses real environment variables
- **Safe Logging**: Never log full secret values; log key names or masked values only (`API_KEY=sk-***abc123`)
- **Fail Fast**: Startup validation fails immediately if required environment variables are missing/invalid
- **Complete .env.example**: Ship with all required/optional keys documented with comments

### Environment Variable Management
```python
# ✅ GOOD - Single config module
class Settings:
    database_url: str = Field(..., env="DATABASE_URL")
    api_key: str = Field(..., env="OPENAI_API_KEY")
    
    def __post_init__(self):
        if not self.api_key.startswith('sk-'):
            raise ValueError("Invalid API key format")

# ✅ GOOD - Safe logging  
logger.info(f"Loaded config for API_KEY={self.api_key[:8]}***")

# ❌ BAD - Hard-coded secrets
api_key = "sk-1234567890abcdef"

# ❌ BAD - Scattered conditionals
if os.getenv("NODE_ENV") == "production":
    # configuration logic scattered everywhere
```

## Development Notes

- **Offline Capable**: Rule-based mode works without LLM APIs
- **Pluggable LLM**: Support OpenAI/DeepSeek via environment config
- **Coordinate Precision**: ±3px tolerance for screen automation
- **Mock ATS Testing**: Realistic form patterns for validation
- **TypeScript Strict**: ESLint+Prettier for frontend
- **Python Quality**: black+ruff+mypy for backend
- **Config Validation**: Pydantic settings with startup validation
- **Secret Management**: Environment-based with safe logging practices

## Quick Validation Checklist
```bash
make up              # Start services (validates all env vars)
make dev-companion   # Start local companion  
make e2e             # Run full test suite
# Load extension dist into Chrome
# Open /mock-ats/greenhouse
# Open side panel → Analyze → Fill → (Auto-Submit if whitelisted)
```