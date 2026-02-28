# Portfolio Backtest System - Management Script
# Unified tool for start, stop, restart, status check

param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "help")]
    [string]$Command = "help",

    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$Force,
    [switch]$NoBrowser
)

# Color definitions
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"

# Project paths
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPidFile = Join-Path $ProjectRoot ".backend.pid"
$FrontendPidFile = Join-Path $ProjectRoot ".frontend.pid"

# Show logo
function Show-Logo {
    Write-Host "========================================" -ForegroundColor $ColorInfo
    Write-Host "  Portfolio Backtest - Manager Tool     " -ForegroundColor $ColorInfo
    Write-Host "========================================" -ForegroundColor $ColorInfo
}

# Show help
function Show-Help {
    Show-Logo
    Write-Host ""
    Write-Host "Usage: .\manage.ps1 <command> [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor White
    Write-Host "    start     Start services" -ForegroundColor White
    Write-Host "    stop      Stop services" -ForegroundColor White
    Write-Host "    restart   Restart services" -ForegroundColor White
    Write-Host "    status    Check service status" -ForegroundColor White
    Write-Host "    logs      View service logs" -ForegroundColor White
    Write-Host "    help      Show help" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "    -BackendOnly   Only operate backend service" -ForegroundColor White
    Write-Host "    -FrontendOnly  Only operate frontend service" -ForegroundColor White
    Write-Host "    -Force         Force stop (for stop command)" -ForegroundColor White
    Write-Host "    -NoBrowser     Do not open browser on start" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "    .\manage.ps1 start          # Start all services" -ForegroundColor White
    Write-Host "    .\manage.ps1 start -BackendOnly    # Start backend only" -ForegroundColor White
    Write-Host "    .\manage.ps1 stop           # Stop all services" -ForegroundColor White
    Write-Host "    .\manage.ps1 stop -Force    # Force stop all" -ForegroundColor White
    Write-Host "    .\manage.ps1 restart        # Restart all services" -ForegroundColor White
    Write-Host "    .\manage.ps1 status         # Check status" -ForegroundColor White
    Write-Host ""
    Write-Host "Shortcuts:" -ForegroundColor White
    Write-Host "    .\start-all.ps1    # Same as: .\manage.ps1 start" -ForegroundColor White
    Write-Host "    .\stop-all.ps1     # Same as: .\manage.ps1 stop" -ForegroundColor White
}

# Get service status
function Get-ServiceStatus {
    $backendRunning = $false
    $frontendRunning = $false
    $backendPid = $null
    $frontendPid = $null

    if (Test-Path $BackendPidFile) {
        $backendPid = Get-Content $BackendPidFile -ErrorAction SilentlyContinue
        if ($backendPid) {
            $backendProcess = Get-Process -Id $backendPid -ErrorAction SilentlyContinue
            $backendRunning = ($null -ne $backendProcess)
        }
    }

    if (Test-Path $FrontendPidFile) {
        $frontendPid = Get-Content $FrontendPidFile -ErrorAction SilentlyContinue
        if ($frontendPid) {
            $frontendProcess = Get-Process -Id $frontendPid -ErrorAction SilentlyContinue
            $frontendRunning = ($null -ne $frontendProcess)
        }
    }

    return @{
        BackendRunning = $backendRunning
        FrontendRunning = $frontendRunning
        BackendPid = $backendPid
        FrontendPid = $frontendPid
    }
}

# Show service status
function Show-Status {
    Show-Logo
    Write-Host ""
    Write-Host "Service Status:" -ForegroundColor $ColorInfo
    Write-Host ""

    $status = Get-ServiceStatus

    if ($status.BackendRunning) {
        Write-Host "  [OK] Backend: Running" -ForegroundColor $ColorSuccess
        Write-Host "       PID: $($status.BackendPid)" -ForegroundColor White
        Write-Host "       URL: http://localhost:5000" -ForegroundColor White
    } else {
        Write-Host "  [STOPPED] Backend: Not running" -ForegroundColor $ColorError
    }

    Write-Host ""

    if ($status.FrontendRunning) {
        Write-Host "  [OK] Frontend: Running" -ForegroundColor $ColorSuccess
        Write-Host "       PID: $($status.FrontendPid)" -ForegroundColor White
        Write-Host "       URL: http://localhost:3000" -ForegroundColor White
    } else {
        Write-Host "  [STOPPED] Frontend: Not running" -ForegroundColor $ColorError
    }

    Write-Host ""

    if ($status.BackendRunning -and $status.FrontendRunning) {
        Write-Host "All services are running normally" -ForegroundColor $ColorSuccess
    } elseif ($status.BackendRunning -or $status.FrontendRunning) {
        Write-Host "Some services are not running" -ForegroundColor $ColorWarning
    } else {
        Write-Host "All services are stopped" -ForegroundColor $ColorError
    }
}

# Start services
function Start-Services {
    param($SkipBrowser = $false)

    Show-Logo

    $params = @()
    if ($BackendOnly) { $params += "-BackendOnly" }
    if ($FrontendOnly) { $params += "-FrontendOnly" }
    if ($SkipBrowser -or $NoBrowser) { $params += "-NoBrowser" }

    $scriptPath = Join-Path $ProjectRoot "start-all.ps1"
    if (Test-Path $scriptPath) {
        & $scriptPath @params
    } else {
        Write-Host "Error: start-all.ps1 not found" -ForegroundColor $ColorError
    }
}

# Stop services
function Stop-Services {
    Show-Logo

    $params = @()
    if ($BackendOnly) { $params += "-BackendOnly" }
    if ($FrontendOnly) { $params += "-FrontendOnly" }
    if ($Force) { $params += "-Force" }

    $scriptPath = Join-Path $ProjectRoot "stop-all.ps1"
    if (Test-Path $scriptPath) {
        & $scriptPath @params
    } else {
        Write-Host "Error: stop-all.ps1 not found" -ForegroundColor $ColorError
    }
}

# Restart services
function Restart-Services {
    Show-Logo
    Write-Host ""
    Write-Host "Restarting services..." -ForegroundColor $ColorInfo
    Write-Host ""

    $stopParams = @()
    if ($BackendOnly) { $stopParams += "-BackendOnly" }
    if ($FrontendOnly) { $stopParams += "-FrontendOnly" }

    $stopScript = Join-Path $ProjectRoot "stop-all.ps1"
    if (Test-Path $stopScript) {
        & $stopScript @stopParams
    }

    Start-Sleep -Seconds 2

    Write-Host ""

    $startParams = @()
    if ($BackendOnly) { $startParams += "-BackendOnly" }
    if ($FrontendOnly) { $startParams += "-FrontendOnly" }
    if ($NoBrowser) { $startParams += "-NoBrowser" }

    $startScript = Join-Path $ProjectRoot "start-all.ps1"
    if (Test-Path $startScript) {
        & $startScript @startParams
    }
}

# Show logs
function Show-Logs {
    Show-Logo
    Write-Host ""
    Write-Host "Log viewing feature is under development..." -ForegroundColor $ColorWarning
    Write-Host ""
    Write-Host "You can manually view logs with:" -ForegroundColor $ColorInfo
    Write-Host "  Get-Content .\backend\logs\*.log -Tail 50 -Wait" -ForegroundColor White
}

# Main logic
switch ($Command.ToLower()) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" { Restart-Services }
    "status" { Show-Status }
    "logs" { Show-Logs }
    default { Show-Help }
}

Write-Host ""
