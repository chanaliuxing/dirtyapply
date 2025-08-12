# Apply-Copilot Testing Strategy

Comprehensive testing implementation following Test-Driven Development (TDD) methodology with AI-driven automation.

## 🎯 Testing Philosophy

Apply-Copilot implements a **strict TDD workflow** with the following principles:

1. **Write tests FIRST** - Never write code without tests
2. **Confirm test failures** - Ensure tests are valid before fixing
3. **Minimal fixes** - Make smallest change to pass tests
4. **No test relaxation** - Never modify tests to make code pass
5. **Fast feedback** - Use `--maxfail=1` for immediate failure feedback

## 🏗️ Test Architecture

### Test Pyramid Structure

```
       E2E Tests (Few, Slow, High Value)
           /\
          /  \
         /    \
    Integration Tests (Some, Medium Speed)
        /      \
       /        \
   Unit Tests (Many, Fast, Focused)
```

### Test Categories

| Type | Speed | Scope | Purpose |
|------|-------|--------|---------|
| **Unit** | ⚡ Fast | Single function/class | Logic validation |
| **Integration** | 🚀 Medium | Service interactions | API contracts |
| **E2E** | 🐌 Slow | Full system | User workflows |

## 📋 Test Commands

### Basic Commands
```bash
# Run all tests (TDD workflow)
make test

# Run test pyramid sequentially
make test-tdd

# Run specific test types
make test-unit           # Fast unit tests only
make test-integration    # Integration tests (requires services)
make test-e2e           # End-to-end with Playwright

# Development workflow
make test-watch         # Watch mode for development
make test-coverage      # Generate coverage reports
make test-failed        # Re-run only failed tests
```

### Advanced Commands
```bash
# Run specific test file
make test-specific FILE=test_config.py

# Run with browser visible
make test-e2e-headed

# Debug E2E tests
make test-e2e-debug

# AI-driven test automation
bin/ai-test.sh
```

## 🧪 Unit Tests

**Location**: `apps/api/tests/`, `apps/companion/tests/`
**Framework**: pytest with strict configuration

### Key Features
- **Golden Rules Validation**: Tests configuration security
- **Secret Masking**: Validates safe logging practices
- **Fail-Fast**: `--maxfail=1` stops on first failure
- **Coverage Requirements**: Minimum 80% coverage enforced

### Example Test Structure
```python
class TestConfigValidation:
    """Test configuration with Golden Rules compliance"""
    
    def test_api_key_validation_invalid(self):
        """Test invalid API key fails validation"""
        with pytest.raises(ValidationError, match="Invalid API key format"):
            Settings(openai_api_key="invalid-key")
    
    def test_safe_logging_masks_secrets(self):
        """Test startup logging masks sensitive information"""
        # Test implementation ensures secrets are masked
        assert "sk-1234567***" in logged_output
        assert "1234567890abcdef" not in logged_output
```

### Critical Test Areas
- ✅ Configuration validation (Golden Rules)
- ✅ Secret masking in logging
- ✅ API key format validation
- ✅ Security constraint enforcement
- ✅ LLM provider integration
- ✅ Database connection handling

## 🔗 Integration Tests

**Location**: `apps/api/tests/test_api_integration.py`
**Framework**: FastAPI TestClient + httpx AsyncClient

### Key Features
- **Service Integration**: Tests API endpoints with real HTTP
- **Database Interactions**: Validates data persistence
- **Error Handling**: Ensures graceful failure modes
- **Authentication**: Tests security middleware

### Example Integration Test
```python
@pytest.mark.integration
def test_jtr_endpoint_with_llm_provider(self, client):
    """Test JTR endpoint with actual LLM integration"""
    response = client.post("/api/jtr", json={
        "job_description": "Data Scientist role...",
        "resume_profile": {"skills": ["Python", "ML"]}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["match_score"] > 0
    assert "analysis" in data
```

### Integration Test Coverage
- ✅ API endpoint responses
- ✅ Database operations
- ✅ LLM provider integration
- ✅ Authentication flows
- ✅ Error handling
- ✅ CORS configuration

## 🌐 End-to-End Tests

**Location**: `apps/e2e/tests/`
**Framework**: Playwright with TypeScript

### Key Features
- **Real Browser Testing**: Chromium, Firefox, WebKit support
- **Visual Regression**: Screenshot comparison
- **Mobile Testing**: Responsive design validation
- **Performance Measurement**: Form completion timing

### E2E Test Structure
```typescript
test('should complete full application flow', async ({ page }) => {
  // Navigate to mock ATS
  await page.goto('/mock-ats/greenhouse');
  
  // Fill application form
  await page.fill('input[name="firstName"]', 'Alex');
  await page.fill('input[name="email"]', 'alex@email.com');
  
  // Submit and verify success
  await page.click('button[type="submit"]');
  await expect(page.getByText(/application submitted/i)).toBeVisible();
});
```

### E2E Test Scenarios
- ✅ **Greenhouse ATS**: Single-page application flow
- ✅ **Lever ATS**: Multi-step form wizard
- ✅ **Workday ATS**: Complex navigation patterns
- ✅ **Form Validation**: Required field enforcement
- ✅ **Error Handling**: Network failure scenarios
- ✅ **Performance**: Form completion timing

## 🤖 AI-Driven Testing

**Script**: `bin/ai-test.sh`
**Integration**: Claude Code with TDD methodology

### AI Testing Workflow
1. **Automated Test Execution**: Runs complete test suite
2. **Failure Analysis**: AI analyzes test failures
3. **Targeted Fixes**: Makes minimal code changes
4. **Validation**: Re-runs tests to confirm fixes
5. **Iteration**: Repeats until "ALL GREEN" status

### AI Testing Features
- **TDD Compliance**: Follows CLAUDE.md testing rules
- **Fail-Fast Behavior**: Stops on first failure
- **Minimal Changes**: Makes targeted fixes only
- **Iteration Limits**: Maximum 5 iterations
- **Full Logging**: Comprehensive test execution logs

### Running AI Tests
```bash
# Local AI testing
bin/ai-test.sh

# CI/CD Integration
# Automatically runs on pull requests
# Uses ANTHROPIC_API_KEY from GitHub secrets
```

## 📊 Test Configuration

### pytest.ini Configuration
```ini
[tool:pytest]
addopts = 
    --strict-markers
    --maxfail=1
    --cov=apps/api/app
    --cov-fail-under=80

markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (require services)
    e2e: End-to-end tests (full system)
    security: Security-related tests
```

### Playwright Configuration
```typescript
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  }
});
```

## 🚀 CI/CD Integration

### GitHub Actions Workflow
**File**: `.github/workflows/ai-e2e.yml`

#### Workflow Steps
1. **Foundation Tests**: Unit + Integration tests
2. **E2E Tests**: Playwright browser testing
3. **AI Validation**: Claude Code automation
4. **Quality Gate**: Security scanning + summary

#### Test Matrix
- **OS**: Ubuntu Latest
- **Python**: 3.11
- **Node**: 20
- **Browsers**: Chromium, Firefox, WebKit

### Quality Gates
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All E2E tests pass
- ✅ No hard-coded secrets detected
- ✅ Minimum 80% code coverage
- ✅ AI validation successful

## 🔍 Test Data & Fixtures

### Sample Data
- **Resume**: `samples/resume.json` - Complete user profile
- **Job Description**: `samples/jd.txt` - Data Scientist role
- **Mock ATS Pages**: Realistic form structures

### Test Environment
```bash
# Test-specific environment variables
DATABASE_URL=sqlite:///test.db
COMPANION_TOKEN=test-token-1234567890123456789012345678901234
SECRET_KEY=test-secret-key-1234567890123456789012345678901234
LLM_PROVIDER=none
DEBUG=true
```

## 📈 Test Metrics & Reporting

### Coverage Requirements
- **Minimum**: 80% overall coverage
- **Critical Paths**: 95% coverage for security functions
- **New Code**: 90% coverage requirement

### Performance Benchmarks
- **Unit Tests**: < 0.1s per test
- **Integration Tests**: < 2s per test
- **E2E Tests**: < 30s per scenario
- **Form Fill Speed**: < 2s automation target

### Reporting
- **Coverage**: HTML reports in `htmlcov/`
- **E2E Results**: Playwright HTML reports
- **AI Logs**: Timestamped execution logs
- **Screenshots**: Failure state captures

## 🛡️ Security Testing

### Secret Scanning
```bash
# Automated secret detection
grep -r "sk-[a-zA-Z0-9]" --include="*.py" apps/
grep -r "nvapi-[a-zA-Z0-9]" --include="*.js" apps/
```

### Security Test Cases
- ✅ No hard-coded API keys
- ✅ Proper token masking in logs
- ✅ Local-only companion service
- ✅ Environment validation
- ✅ Production security constraints

## 🎯 Best Practices

### TDD Workflow
1. **Red**: Write failing test first
2. **Green**: Make minimal change to pass
3. **Refactor**: Improve code while keeping tests green
4. **Repeat**: Continue for each new feature

### Test Organization
- **Descriptive Names**: Test names explain what is being tested
- **Single Responsibility**: One assertion per test when possible
- **Setup/Teardown**: Use fixtures for test data
- **Independence**: Tests can run in any order

### Common Patterns
```python
# Good: Descriptive test name
def test_openai_api_key_validation_fails_for_invalid_format(self):
    """Test OpenAI API key validation rejects invalid format"""

# Good: Clear assertion with helpful message
assert response.status_code == 200, f"Expected 200, got {response.status_code}"

# Good: Proper test categorization
@pytest.mark.integration
@pytest.mark.slow
def test_database_connection_with_real_postgres(self):
```

## 🚨 Troubleshooting

### Common Issues

**Tests hang or timeout**
```bash
# Use shorter timeout for debugging
pytest --timeout=30 test_file.py
```

**E2E tests fail locally**
```bash
# Install browsers
cd apps/e2e && npx playwright install --with-deps

# Run in headed mode to see what's happening
make test-e2e-headed
```

**AI testing not working**
```bash
# Check Claude Code installation
npm list -g @anthropic-ai/claude-code

# Verify API key is set
echo $ANTHROPIC_API_KEY

# Check permissions
chmod +x bin/ai-test.sh
```

### Debug Commands
```bash
# Verbose test output
pytest -v -s test_file.py

# Debug specific test
pytest --pdb test_file.py::test_function

# E2E debugging
cd apps/e2e && npx playwright test --debug

# Show coverage gaps
pytest --cov-report=html && open htmlcov/index.html
```

## 🎉 Success Metrics

The Apply-Copilot testing strategy is successful when:

- ✅ **TDD Workflow**: All features developed test-first
- ✅ **Fast Feedback**: Test failures detected within seconds
- ✅ **High Confidence**: Comprehensive test coverage
- ✅ **AI Integration**: Automated test maintenance
- ✅ **Quality Gates**: No production issues from untested code
- ✅ **Developer Experience**: Tests help rather than hinder development

---

**Remember**: Tests are not just verification—they're specification, documentation, and safety net all in one. Following TDD methodology ensures Apply-Copilot maintains the highest quality standards while enabling rapid, confident development.