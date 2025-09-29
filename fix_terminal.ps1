# PowerShell Backend Terminal Fix Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BACKEND TERMINAL FIX (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Change to backend directory
$BackendPath = "c:\Users\Admin\CascadeProjects\india-medical-insurance-dashboard\backend"
Set-Location $BackendPath
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Green

# Kill existing Python processes
Write-Host "Killing existing Python processes..." -ForegroundColor Yellow
try {
    Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "Python processes terminated" -ForegroundColor Green
} catch {
    Write-Host "No Python processes to kill" -ForegroundColor Yellow
}

# Kill processes on specific ports
Write-Host "Freeing up ports 8000 and 8001..." -ForegroundColor Yellow
$ports = @(8000, 8001)
foreach ($port in $ports) {
    try {
        $connections = netstat -ano | Select-String ":$port "
        foreach ($connection in $connections) {
            $pid = ($connection -split '\s+')[-1]
            if ($pid -match '^\d+$') {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {
        # Ignore errors
    }
}

Start-Sleep -Seconds 2

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found in PATH!" -ForegroundColor Red
    exit 1
}

# Setup virtual environment
Write-Host "Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\activate.ps1") {
    Write-Host "Virtual environment exists, activating..." -ForegroundColor Green
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "Creating new virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & ".venv\Scripts\Activate.ps1"
}

# Install dependencies
Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Error installing dependencies: $_" -ForegroundColor Red
}

# Check environment file
if (Test-Path ".env") {
    Write-Host "Environment file (.env) found" -ForegroundColor Green
} else {
    Write-Host "Warning: .env file not found" -ForegroundColor Yellow
}

# Start the server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting FastAPI backend server..." -ForegroundColor Cyan
Write-Host "Server URL: http://localhost:8001" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8001/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

try {
    python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
}

Write-Host "Server stopped. Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
