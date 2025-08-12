#!/bin/bash
# Apply-Copilot AI Test Harness
# Self-running test automation with Claude Code
# Follows TDD methodology with fail-fast behavior

set -euo pipefail

# Colors for output
CYAN='\033[36m'
GREEN='\033[32m'
RED='\033[31m'
YELLOW='\033[33m'
RESET='\033[0m'

# Configuration
MAX_ITERATIONS=5
TEST_TIMEOUT=300
LOG_FILE="ai-test-$(date +%Y%m%d-%H%M%S).log"

echo -e "${CYAN}🤖 Apply-Copilot AI Test Harness${RESET}"
echo "Log file: ${LOG_FILE}"
echo "Max iterations: ${MAX_ITERATIONS}"
echo "Test timeout: ${TEST_TIMEOUT}s"
echo ""

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "${LOG_FILE}"
}

# Function to run Claude Code with test prompt
run_claude_tests() {
    local iteration=$1
    
    log "🔄 Iteration ${iteration}/${MAX_ITERATIONS}: Running Claude Code test automation"
    
    # Main test prompt following CLAUDE.md methodology
    claude -p "
You are working on Apply-Copilot, a Job-Driven Resume Rewriter & Auto-Apply Agent.

CRITICAL INSTRUCTIONS (from CLAUDE.md):
1. Follow TDD methodology STRICTLY
2. Write/refresh tests FIRST before any code changes
3. Run tests and confirm failures before implementing fixes
4. Use --maxfail=1 for fast feedback
5. NEVER relax test requirements

TASK: Run the complete test suite following this exact sequence:

1. UNIT TESTS:
   - Run: python -m pytest --maxfail=1 -q -m \"not integration and not e2e\"
   - If failures: analyze, fix with minimal changes, re-run
   - Must pass before proceeding

2. INTEGRATION TESTS:
   - Ensure services running: make up
   - Run: python -m pytest --maxfail=1 -q -m \"integration\"
   - If failures: analyze, fix with minimal changes, re-run
   - Must pass before proceeding

3. E2E TESTS:
   - Run: npx playwright test --reporter=list
   - If failures: analyze, fix with minimal changes, re-run
   - Must pass before proceeding

REQUIREMENTS:
- Fix ALL test failures before proceeding to next test type
- Use EDIT tool to make minimal, targeted fixes
- Run tests after each change to verify fixes
- Document what you fixed in each iteration
- When ALL tests pass, output exactly: 'ALL GREEN'

FORBIDDEN:
- DO NOT skip or ignore failing tests
- DO NOT modify test assertions to make them pass
- DO NOT proceed to next test type with failures
- DO NOT make large, sweeping changes

Start with unit tests and work your way through the test pyramid.
" \
    --output-format stream-json \
    --verbose \
    2>&1 | tee -a "${LOG_FILE}"
    
    return ${PIPESTATUS[0]}
}

# Function to check if tests are all green
check_all_green() {
    if grep -q "ALL GREEN" "${LOG_FILE}"; then
        return 0
    else
        return 1
    fi
}

# Function to run final validation
final_validation() {
    log "🎯 Running final validation..."
    
    # Quick test run to confirm everything is working
    make test-unit && make test-integration && make test-e2e
    
    if [ $? -eq 0 ]; then
        log "✅ Final validation PASSED"
        return 0
    else
        log "❌ Final validation FAILED"
        return 1
    fi
}

# Main execution loop
main() {
    log "🚀 Starting AI test automation"
    
    # Validate environment
    if [ ! -f "CLAUDE.md" ]; then
        log "❌ CLAUDE.md not found - run from repository root"
        exit 1
    fi
    
    if [ ! -f "Makefile" ]; then
        log "❌ Makefile not found - run from repository root"
        exit 1
    fi
    
    # Ensure dependencies are installed
    log "📦 Installing dependencies..."
    make install >> "${LOG_FILE}" 2>&1 || {
        log "❌ Failed to install dependencies"
        exit 1
    }
    
    # Start services
    log "🔧 Starting services..."
    make up >> "${LOG_FILE}" 2>&1 || {
        log "❌ Failed to start services"
        exit 1
    }
    
    # Main test loop
    for i in $(seq 1 ${MAX_ITERATIONS}); do
        log "🔄 Starting iteration ${i}/${MAX_ITERATIONS}"
        
        # Run Claude Code with timeout
        timeout ${TEST_TIMEOUT} run_claude_tests ${i} || {
            local exit_code=$?
            if [ ${exit_code} -eq 124 ]; then
                log "⏰ Timeout after ${TEST_TIMEOUT}s in iteration ${i}"
            else
                log "❌ Claude Code failed in iteration ${i} (exit code: ${exit_code})"
            fi
            continue
        }
        
        # Check if all tests are green
        if check_all_green; then
            log "🎉 SUCCESS: All tests are GREEN after ${i} iterations!"
            
            # Run final validation
            if final_validation; then
                log "✅ COMPLETE: AI test automation successful"
                echo ""
                echo -e "${GREEN}🎉 ✅ ALL GREEN - AI TEST AUTOMATION SUCCESSFUL${RESET}"
                echo "Iterations used: ${i}/${MAX_ITERATIONS}"
                echo "Log file: ${LOG_FILE}"
                exit 0
            else
                log "❌ Final validation failed despite green status"
                exit 1
            fi
        else
            log "⚠️  Tests not all green yet after iteration ${i}"
        fi
    done
    
    # If we get here, we've exhausted all iterations
    log "❌ FAILED: Maximum iterations (${MAX_ITERATIONS}) reached without success"
    echo ""
    echo -e "${RED}❌ FAILED: Could not achieve ALL GREEN status${RESET}"
    echo "Iterations used: ${MAX_ITERATIONS}/${MAX_ITERATIONS}"
    echo "Log file: ${LOG_FILE}"
    echo ""
    echo "Manual intervention required. Check the log for details:"
    echo "  tail -f ${LOG_FILE}"
    exit 1
}

# Cleanup function
cleanup() {
    log "🧹 Cleaning up..."
    # Stop services
    make down >> "${LOG_FILE}" 2>&1 || true
}

# Set up signal handlers
trap cleanup EXIT
trap 'log "🚫 Interrupted by user"; exit 130' INT TERM

# Run main function
main "$@"