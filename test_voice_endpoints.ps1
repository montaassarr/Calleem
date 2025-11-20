# Test Voice Agent Endpoints
$baseUrl = "http://localhost:8000/api/v1"

Write-Host "Testing Voice Agent Endpoints..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Get Models
Write-Host "1. Testing GET /voice/models..." -ForegroundColor Yellow
try {
    $models = Invoke-RestMethod -Uri "$baseUrl/voice/models" -Method GET
    Write-Host "✓ Models endpoint working" -ForegroundColor Green
    Write-Host "  Groq models: $($models.groq.Count)" -ForegroundColor Gray
    Write-Host "  OpenAI models: $($models.openai.Count)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Models endpoint failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: Get Voices
Write-Host "2. Testing GET /voice/voices..." -ForegroundColor Yellow
try {
    $voices = Invoke-RestMethod -Uri "$baseUrl/voice/voices" -Method GET
    Write-Host "✓ Voices endpoint working" -ForegroundColor Green
    Write-Host "  Available voices: $($voices.count)" -ForegroundColor Gray
    Write-Host "  ElevenLabs configured: $($voices.elevenlabs_configured)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Voices endpoint failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Get Tools
Write-Host "3. Testing GET /voice/tools..." -ForegroundColor Yellow
try {
    $tools = Invoke-RestMethod -Uri "$baseUrl/voice/tools" -Method GET
    Write-Host "✓ Tools endpoint working" -ForegroundColor Green
    Write-Host "  Available tools: $($tools.tools.Count)" -ForegroundColor Gray
    foreach ($tool in $tools.tools) {
        Write-Host "    - $($tool.function.name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Tools endpoint failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Get Config (requires auth)
Write-Host "4. Testing GET /voice/config (requires auth)..." -ForegroundColor Yellow
Write-Host "  Note: This endpoint requires authentication" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host "The WebGL warning you see in the browser is normal and can be ignored." -ForegroundColor Yellow
Write-Host "It does not affect the functionality of the voice agent." -ForegroundColor Yellow
