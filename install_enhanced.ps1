# AI Receptionist - Enhanced Setup Script
# Installs new AI frameworks and dependencies

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  AI Receptionist - Enhanced Setup" -ForegroundColor Cyan
Write-Host "  Installing advanced AI reasoning engine..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path ".\backend\requirements.txt")) {
    Write-Host "ERROR: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = & python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher" -ForegroundColor Red
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Navigate to backend
Set-Location backend

# Check if virtual environment exists
if (-not (Test-Path "..\venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv ..\venv
    Write-Host "Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ..\venv\Scripts\Activate.ps1
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host ""

# Install/upgrade requirements
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan
pip install -r requirements.txt --upgrade
Write-Host ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  Installation Complete!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "New AI frameworks installed:" -ForegroundColor Cyan
    Write-Host "  ✓ CrewAI - Multi-agent orchestration" -ForegroundColor Green
    Write-Host "  ✓ LangChain - Memory and retrieval" -ForegroundColor Green
    Write-Host "  ✓ LiteLLM - Multi-model support" -ForegroundColor Green
    Write-Host "  ✓ Instructor - Structured outputs" -ForegroundColor Green
    Write-Host "  ✓ OpenAI - Additional model support" -ForegroundColor Green
    Write-Host ""
    Write-Host "Enhanced features:" -ForegroundColor Cyan
    Write-Host "  ✓ AI Brain reasoning engine" -ForegroundColor Green
    Write-Host "  ✓ Dynamic configuration system" -ForegroundColor Green
    Write-Host "  ✓ MongoDB-based memory" -ForegroundColor Green
    Write-Host "  ✓ Multi-tenant architecture ready" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Ensure MongoDB is running" -ForegroundColor White
    Write-Host "  2. Update .env with your API keys" -ForegroundColor White
    Write-Host "  3. Run: python -m uvicorn main:app --reload" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host "  Installation Failed!" -ForegroundColor Red
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
    exit 1
}

# Return to project root
Set-Location ..
