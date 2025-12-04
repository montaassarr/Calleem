#!/bin/bash
# Comprehensive backend diagnostics runner
# Executes health checks, linting, and targeted tests with structured output

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="$PROJECT_ROOT/logs/diagnostics"
STATUS_FILE="$LOG_DIR/backend_$(date +"%Y%m%d_%H%M%S").log"

mkdir -p "$LOG_DIR"

declare -a FAILURES=()

echo "════════════════════════════════════════════════════════" | tee -a "$STATUS_FILE"
echo "  🩺 Backend Diagnostics" | tee -a "$STATUS_FILE"
echo "════════════════════════════════════════════════════════" | tee -a "$STATUS_FILE"
echo "Project root: $PROJECT_ROOT" | tee -a "$STATUS_FILE"

diagnose_step() {
    local name="$1"
    shift
    echo "\n▶️  $name" | tee -a "$STATUS_FILE"
    if "$@" >>"$STATUS_FILE" 2>&1; then
        echo "✅ $name" | tee -a "$STATUS_FILE"
    else
        echo "❌ $name" | tee -a "$STATUS_FILE"
        FAILURES+=("$name")
    fi
}

# 1. Health endpoint check
health_check() {
    curl --fail --silent http://localhost:8000/health >/dev/null
}

diagnose_step "Health endpoint" health_check

# 2. MongoDB connectivity test
mongodb_check() {
    cd "$BACKEND_DIR"
    python - <<'PY'
from database.mongo_config import connect_to_mongo, close_mongo_connection
import asyncio

async def main():
    await connect_to_mongo()
    await close_mongo_connection()

asyncio.run(main())
PY
}

diagnose_step "MongoDB connectivity" mongodb_check

# 3. Static analysis (ruff)
run_ruff() {
    cd "$BACKEND_DIR"
    if [ -f "ruff.toml" ] || [ -f ".ruff.toml" ]; then
        if command -v ruff >/dev/null 2>&1; then
            ruff check .
        else
            echo "Ruff not installed, skipping"
        fi
    else
        echo "Skipping ruff (config not found)"
    fi
}

diagnose_step "Ruff lint" run_ruff

# 4. Unit tests (fast failure)
run_unit_tests() {
    cd "$PROJECT_ROOT"
    pytest tests/unit -q
}

diagnose_step "Unit tests" run_unit_tests

# 5. Integration smoke test (selected file)
run_smoke_test() {
    cd "$PROJECT_ROOT"
    pytest tests/integration/test_auth.py -q
}

diagnose_step "Auth integration test" run_smoke_test

# Summary
if [ ${#FAILURES[@]} -eq 0 ]; then
    echo "\n🎉 Backend diagnostics complete. No failures detected." | tee -a "$STATUS_FILE"
    exit 0
else
    echo "\n⚠️  Backend diagnostics completed with failures:" | tee -a "$STATUS_FILE"
    for failure in "${FAILURES[@]}"; do
        echo "   - $failure" | tee -a "$STATUS_FILE"
    done
    echo "Detailed log: $STATUS_FILE"
    exit 1
fi
