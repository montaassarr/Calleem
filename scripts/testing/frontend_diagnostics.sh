#!/bin/bash
# Frontend diagnostics script for Next.js workspace

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend_next"
LOG_DIR="$PROJECT_ROOT/logs/diagnostics"
STATUS_FILE="$LOG_DIR/frontend_$(date +"%Y%m%d_%H%M%S").log"

mkdir -p "$LOG_DIR"

declare -a FAILURES=()

echo "════════════════════════════════════════════════════════" | tee -a "$STATUS_FILE"
echo "  🧪 Frontend Diagnostics" | tee -a "$STATUS_FILE"
echo "════════════════════════════════════════════════════════" | tee -a "$STATUS_FILE"
echo "Project root: $PROJECT_ROOT" | tee -a "$STATUS_FILE"

diag_step() {
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

# 1. Dependency consistency check
verify_lockfile() {
    cd "$FRONTEND_DIR"
    npm ls --depth=0 >/dev/null
}

diag_step "Verify dependencies" verify_lockfile

# 2. ESLint
run_lint() {
    cd "$FRONTEND_DIR"
    npm run lint
}

diag_step "ESLint" run_lint

# 3. Type-checked build
run_build() {
    cd "$FRONTEND_DIR"
    NEXT_TELEMETRY_DISABLED=1 npm run build
}

diag_step "Next.js build" run_build

# 4. Playwright smoke listing (validates config loads)
playwright_smoke() {
    cd "$FRONTEND_DIR"
    # Listing ensures Playwright loads config without running full suite
    npx playwright test --list >/dev/null
}

diag_step "Playwright smoke" playwright_smoke

if [ ${#FAILURES[@]} -eq 0 ]; then
    echo "\n🎉 Frontend diagnostics complete. No failures detected." | tee -a "$STATUS_FILE"
    exit 0
else
    echo "\n⚠️  Frontend diagnostics completed with failures:" | tee -a "$STATUS_FILE"
    for failure in "${FAILURES[@]}"; do
        echo "   - $failure" | tee -a "$STATUS_FILE"
    done
    echo "Detailed log: $STATUS_FILE"
    exit 1
fi
