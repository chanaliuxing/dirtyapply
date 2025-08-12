# Apply-Copilot Development Roadmap

**Project**: Job-Driven Resume Rewriter & Auto-Apply Agent  
**Target**: Working monorepo with Chrome MV3, FastAPI, and Local Companion  
**Goal**: ✅ READY: run `make up && make e2e`

---

## Phase 1: Foundation & Infrastructure (Week 1)

### 1.1 Project Structure & Tooling
- [ ] Create monorepo structure (`apps/`, `packages/`, `infra/`)
- [ ] Setup `pnpm` workspace configuration
- [ ] Create `Makefile` with all required commands
- [ ] Setup `docker-compose.yml` (Postgres, MinIO, API services)
- [ ] **Configure comprehensive `.env.example`** with all required/optional variables and comments
- [ ] Setup GitHub Actions CI pipeline
- [ ] **Implement secret scanning** in CI to prevent hard-coded credentials

**Deliverables**: 
- Monorepo skeleton
- Working `make up` command
- Complete `.env.example` with documentation
- CI pipeline with security checks

### 1.2 Core Schemas & Types
- [ ] Define JSON schemas in `packages/core/`
- [ ] Implement Zod schemas (TypeScript) and Pydantic models (Python)
- [ ] Create JTR Input/Output schema contracts
- [ ] Define Action Plan schema with selectors/modes/deps/waits
- [ ] Build ATS synonym/abbreviation dictionary

**Deliverables**:
- Shared type definitions
- Schema validation
- ATS keyword mappings

---

## Phase 2: Backend API Foundation (Week 2)

### 2.1 FastAPI Backend Structure
- [ ] Setup FastAPI project structure in `apps/api/`
- [ ] **Implement centralized config module** with Pydantic settings and validation
- [ ] **Add startup validation** that fails fast on missing/invalid environment variables
- [ ] Implement database models (Jobs, Applications, Evidence, Runs, Snapshots)
- [ ] Create PostgreSQL migrations with Alembic
- [ ] **Setup structured logging with safe secret handling** (masked API keys, no full tokens)
- [ ] Implement basic auth/token system with environment-based secrets

**Deliverables**:
- Working FastAPI server on port 8000
- Centralized configuration with fail-fast validation
- Safe logging implementation
- Database migrations
- OpenAPI documentation

### 2.2 Mock LLM & Rule-Based Engine
- [ ] Implement rule-based JTR engine (offline mode)
- [ ] Create keyword matching and synonym replacement
- [ ] Build ATS optimization logic (placement weights, recency)
- [ ] Implement pluggable LLM interface (OpenAI/DeepSeek)
- [ ] Add confidence scoring and thresholds

**Deliverables**:
- Working JTR without external APIs
- LLM provider abstraction
- ATS compliance checks

---

## Phase 3: JTR Engine & RS Implementation (Week 3)

### 3.1 Reasoned Synthesis (RS) Engine
- [ ] Implement RS validation rules (employer/title/time constraints)
- [ ] Create evidence-based enhancement system
- [ ] Build risk assessment (low/med/high/critical levels)
- [ ] Add diff generation with RS metadata
- [ ] Implement metric range/approximation logic

**Deliverables**:
- RS-compliant resume modifications
- Risk assessment system
- Audit trail with evidence linking

### 3.2 Resume Artifact Generation
- [ ] Implement ATS-friendly DOCX generation (`python-docx`)
- [ ] Create PDF export with text layer (`weasyprint`/`reportlab`)
- [ ] Build filename standardization (`Firstname_Lastname_TargetRole_Company.pdf`)
- [ ] Setup MinIO integration with local fallback
- [ ] Add artifact versioning and storage

**Deliverables**:
- ATS-optimized document generation
- Artifact storage system
- Document download endpoints

---

## Phase 4: Action Planning & Field Detection (Week 4)

### 4.1 Action Planner
- [ ] Implement field mapping to Action Plans
- [ ] Create selector generation (CSS/XPath/Shadow DOM)
- [ ] Build multi-step flow planning (Workday-style wizards)
- [ ] Add `wait_for` conditions (URL changes, element appearance)
- [ ] Implement dependency tracking between fields

**Deliverables**:
- Action Plan generation from field maps
- Multi-step flow support
- Wait condition validation

### 4.2 Mock ATS Pages
- [ ] Create Greenhouse-style single page form
- [ ] Build Lever-style application form
- [ ] Implement Workday-style multi-step wizard
- [ ] Add realistic form elements (Shadow DOM, iframes)
- [ ] Include success markers ("Application submitted")

**Deliverables**:
- Three working mock ATS sites
- Realistic form complexity
- Success validation markers

---

## Phase 5: Chrome Extension Development (Week 5-6)

### 5.1 Extension Infrastructure
- [ ] Setup Chrome MV3 project with React + TypeScript + Vite
- [ ] Create manifest.json with required permissions
- [ ] Implement service worker with message handling
- [ ] Setup side panel React application
- [ ] Configure hot module replacement for development

**Deliverables**:
- Working Chrome extension scaffold
- React side panel
- Development workflow

### 5.2 Content Scripts & Page Analysis
- [ ] Implement JD extraction from job pages
- [ ] Create field detection (inputs/textareas/selects/radios/checkboxes)
- [ ] Handle Shadow DOM and iframe traversal
- [ ] Build element rectangle and coordinate calculation
- [ ] Add label/placeholder text association

**Deliverables**:
- Job description parsing
- Form field mapping
- Element coordinate system

### 5.3 Side Panel UI Components
- [ ] Build match score display with visual indicators
- [ ] Create must-have/preferred coverage matrix
- [ ] Implement tailored resume preview
- [ ] Add QA bundle display and editing
- [ ] Create diff viewer with RS badges and rollback

**Deliverables**:
- Complete side panel interface
- Resume preview and editing
- RS-aware diff visualization

---

## Phase 6: Local Companion Service (Week 7)

### 6.1 Local HTTP Server
- [ ] Setup FastAPI server on `127.0.0.1:8765`
- [ ] **Implement secure token-based authentication** (no hard-coded tokens)
- [ ] **Add config validation** for companion service with fail-fast startup
- [ ] Create endpoints: `/focus`, `/type`, `/click`, `/ocr_click`, `/screenshot`, `/scroll`
- [ ] **Add request logging with token masking** (log token prefixes only)
- [ ] Implement coordinate conversion (CSS→screen with DPR)

**Deliverables**:
- Local automation server with secure config
- Token-based auth with safe logging
- Coordinate conversion system
- Action logging with security compliance

### 6.2 Automation Implementation
- [ ] Integrate PyAutoGUI for mouse/keyboard control
- [ ] Setup Tesseract OCR for text recognition
- [ ] Implement screenshot capture with mss+Pillow
- [ ] Add OCR-based button detection with user confirmation
- [ ] Build scroll and window focus management

**Deliverables**:
- Mouse/keyboard automation
- OCR text recognition
- Screenshot capture system

---

## Phase 7: Integration & E2E Testing (Week 8)

### 7.1 Backend Integration
- [ ] Connect extension service worker to FastAPI backend
- [ ] Implement backend→companion orchestration
- [ ] Add form filling strategy execution
- [ ] Create submission guard with pre-flight validation
- [ ] Build snapshot system (pre/post state capture)

**Deliverables**:
- End-to-end data flow
- Form filling orchestration
- State management system

### 7.2 End-to-End Testing
- [ ] Setup Playwright test framework
- [ ] Create content script emulator for testing
- [ ] Build tests for each mock ATS flow
- [ ] Implement success marker validation
- [ ] Add screenshot comparison and artifact validation

**Deliverables**:
- Automated E2E test suite
- Mock ATS validation
- Regression testing framework

---

## Phase 8: CLI Tools & Documentation (Week 9)

### 8.1 Command Line Interface
- [ ] Implement `python -m api.cli jtr` command
- [ ] Create `python -m api.cli plan` command
- [ ] Add sample data generation tools
- [ ] Build resume/JD validation utilities
- [ ] Create debugging and diagnostic commands

**Deliverables**:
- Complete CLI toolset
- Sample data and validation
- Debug utilities

### 8.2 Documentation & Samples
- [ ] Create comprehensive README with quickstart
- [ ] Write `/docs/ARCHITECTURE.md`
- [ ] Document RS rules in `/docs/RS_RULES.md`
- [ ] Create ATS checklist in `/docs/ATS_CHECKLIST.md`
- [ ] Build test plan documentation
- [ ] Generate sample resume.json and jd.txt files

**Deliverables**:
- Complete documentation set
- Sample data for testing
- Architecture documentation

---

## Phase 9: Quality Assurance & Validation (Week 10)

### 9.1 Test Suite Completion
- [ ] Implement all unit tests (RS validation, ATS optimization, planner)
- [ ] Create integration tests (API endpoints, JTR pipeline)
- [ ] Build comprehensive E2E test coverage
- [ ] Add performance benchmarking
- [ ] Implement security validation tests

**Deliverables**:
- Complete test coverage
- Performance benchmarks
- Security validation

### 9.2 Guardrails & Compliance
- [ ] Validate RS guard prevents illegal modifications
- [ ] Ensure ATS guard checks keyword placement
- [ ] Test action plan guard for multi-step flows
- [ ] Verify E2E guard completes full application flows
- [ ] **Security audit**: Scan for hard-coded secrets, validate logging practices
- [ ] **Environment validation**: Test fail-fast behavior for missing/invalid vars
- [ ] Add compliance reporting and monitoring

**Deliverables**:
- All guardrails validated
- Security compliance verified
- Environment configuration validated
- Compliance monitoring
- Safety verification

---

## Phase 10: Final Integration & Polish (Week 11)

### 10.1 Production Readiness
- [ ] Optimize database queries and indexing
- [ ] Implement proper error handling and recovery
- [ ] Add monitoring and observability
- [ ] Setup logging aggregation and alerts
- [ ] Create deployment documentation

**Deliverables**:
- Production-ready system
- Monitoring and alerting
- Deployment guides

### 10.2 User Experience Polish
- [ ] Refine side panel UI/UX
- [ ] Add loading states and progress indicators
- [ ] Implement proper error messages and recovery
- [ ] Create onboarding and help documentation
- [ ] Add keyboard shortcuts and accessibility

**Deliverables**:
- Polished user interface
- Error handling and recovery
- User documentation

---

## Golden Rules Implementation Guide

### Environment Configuration Standards

#### Centralized Config Module Structure
```python
# apps/api/app/core/config.py
from pydantic import BaseSettings, Field, validator
import os
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # API Keys (never hard-coded)
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Service Configuration
    companion_token: str = Field(..., env="COMPANION_TOKEN")
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    
    # Feature Flags
    llm_provider: str = Field("none", env="LLM_PROVIDER")  # none|openai|deepseek
    
    @validator("openai_api_key")
    def validate_openai_key(cls, v):
        if v and not v.startswith('sk-'):
            raise ValueError("Invalid OpenAI API key format")
        return v
    
    @validator("companion_token")
    def validate_companion_token(cls, v):
        if len(v) < 32:
            raise ValueError("Companion token must be at least 32 characters")
        return v
    
    def __post_init__(self):
        # Fail fast validation
        if self.llm_provider in ["openai"] and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY required when LLM_PROVIDER=openai")

# Safe logging helper
def mask_secret(secret: str, show_chars: int = 8) -> str:
    if not secret or len(secret) <= show_chars:
        return "***"
    return f"{secret[:show_chars]}***"
```

#### .env.example Template
```bash
# Database Configuration (required)
DATABASE_URL=postgresql://user:password@localhost:5432/apply_copilot

# MinIO/S3 Storage (optional - fallback to local storage)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=apply-copilot

# AI Provider Configuration (optional - defaults to rule-based)
LLM_PROVIDER=none  # Options: none, openai, deepseek, deepseek-nvidia, anthropic
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_NVIDIA_API_KEY=nvapi-your-nvidia-api-key-here

# Service Configuration
API_HOST=0.0.0.0
API_PORT=8000
COMPANION_HOST=127.0.0.1
COMPANION_PORT=8765

# Security (required)
COMPANION_TOKEN=generate-random-32-char-minimum-token
SECRET_KEY=your-jwt-secret-key-for-sessions

# Feature Flags (optional)
ENABLE_MOCK_ATS=true
ENABLE_DEBUG_LOGGING=false
MAX_APPLICATIONS_PER_DAY=25

# Development Only (do not use in production)
DISABLE_AUTH=false  # Only for local testing
```

#### Security Implementation Checklist
- [ ] No secrets in code, tests, fixtures, or documentation
- [ ] Single config module with Pydantic validation  
- [ ] Startup fails fast on missing/invalid environment variables
- [ ] All logging masks sensitive values (API keys, tokens, passwords)
- [ ] .env.example documents all required and optional variables
- [ ] CI pipeline scans for accidentally committed secrets
- [ ] Production uses real environment variables (no .env file)

---

## Success Criteria & Acceptance Tests

### Critical Path Validation
- [ ] **RS Guard**: Unit tests fail on illegal resume modifications
- [ ] **ATS Guard**: Must keywords validated in ≥2 resume sections
- [ ] **Action Plan Guard**: Wait conditions required for Workday flows
- [ ] **E2E Guard**: Complete mock application flows with success markers

### Final Validation Commands
```bash
make up              # All services start successfully
make dev-companion   # Local companion starts on 8765
make test           # All unit/integration tests pass
make e2e            # Full E2E test suite passes
make package-ext    # Extension builds without errors
```

### Demo Flow Verification
1. Load extension into Chrome (Developer mode)
2. Navigate to `/mock-ats/greenhouse`
3. Open side panel and click "Analyze"
4. Verify match score and gap analysis
5. Click "Fill" and validate form population
6. Optionally click "Auto-Submit" (if whitelisted)
7. Assert "Application submitted" success marker

---

## Risk Mitigation & Dependencies

### High Risk Items
- **OCR Accuracy**: Tesseract reliability on various UI elements
- **Coordinate Precision**: ±3px tolerance across different screen setups
- **ATS Complexity**: Real-world form variations beyond mocks
- **Browser Compatibility**: Chrome extension API stability

### External Dependencies
- **Tesseract**: OCR engine installation and configuration
- **PostgreSQL**: Database setup and migrations
- **MinIO**: Object storage configuration
- **Chrome Extension APIs**: MV3 compatibility and permissions

### Mitigation Strategies
- Comprehensive mock ATS testing before real-world deployment
- Fallback strategies for OCR failures (user confirmation dialogs)
- Multiple coordinate calculation approaches
- Extensive browser testing across OS platforms

---

## Post-Launch Enhancements (Future Phases)

### Stretch Goals
- **Advanced Diff Viewer**: One-click rollback per bullet point
- **Dashboard Interface**: Application tracking and analytics
- **A/B Testing**: Multiple resume variants for optimization
- **Mobile Support**: Extension compatibility testing
- **Advanced OCR**: EasyOCR integration for better accuracy

### Scalability Considerations
- **Multi-tenant Support**: User isolation and data segregation
- **API Rate Limiting**: Prevent abuse and ensure fair usage
- **Caching Strategy**: Redis implementation for performance
- **Load Balancing**: Multiple companion instance support

---

**Target Completion**: 11 weeks from project start  
**Success Metric**: ✅ READY: run `make up && make e2e` passes all tests  
**Quality Gate**: All four guardrails (RS/ATS/ActionPlan/E2E) validated