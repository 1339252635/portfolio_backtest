# Portfolio Backtest System - Stop Script
# Stop all running backend and frontend services

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$Force,
    [switch]$Help
)

# Show help
if ($Help) {
    Write-Host "Portfolio Backtest System - Stop Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\stop-all.ps1 [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "    -BackendOnly    Stop only backend service" -ForegroundColor White
    Write-Host "    -FrontendOnly   Stop only frontend service" -ForegroundColor White
    Write-Host "    -Force          Force stop (including non-script processes)" -ForegroundColor White
    Write-Host "    -Help           Show help" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "    .\stop-all.ps1              # Stop all services" -ForegroundColor White
    Write-Host "    .\stop-all.ps1 -BackendOnly # Stop backend only" -ForegroundColor White
    Write-Host "    .\stop-all.ps1 -Force       # Force stop all related processes" -ForegroundColor White
    exit 0
}

# Set window title
$host.ui.RawUI.WindowTitle = "Portfolio Backtest - Service Stopper"

# Color definitions
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"

# Project paths
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPidFile = Join-Path $ProjectRoot ".backend.pid"
$FrontendPidFile = Join-Path $ProjectRoot ".frontend.pid"

Write-Host "========================================" -ForegroundColor $ColorInfo
Write-Host "  Portfolio Backtest - Service Stopper  " -ForegroundColor $ColorInfo
Write-Host "========================================" -ForegroundColor $ColorInfo

# Function to stop service by PID file
function Stop-ServiceByPidFile {
    param($PidFile, $ServiceName)
    
    $stopped = $false
    
    if (Test-Path $PidFile) {
        $processId = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($processId) {
            try {
                $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "[$ServiceName] Stopping process (PID: $processId)..." -ForegroundColor $ColorWarning
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Seconds 1
                    
                    # Verify process stopped
                    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                    if (-not $process) {
                        Write-Host "[$ServiceName] OK Stopped" -ForegroundColor $ColorSuccess
                        $stopped = $true
                    } else {
                        Write-Host "[$ServiceName] Failed to stop" -ForegroundColor $ColorError
                    }
                } else {
                    Write-Host "[$ServiceName] Process not running" -ForegroundColor $ColorWarning
                    $stopped = $true
                }
            } catch {
                Write-Host "[$ServiceName] Error stopping: $_" -ForegroundColor $ColorError
            }
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "[$ServiceName] No running record found" -ForegroundColor $ColorWarning
    }
    
    return $stopped
}

# Force stop all related processes
function Stop-AllRelatedProcesses {
    Write-Host ""
    Write-Host "[Force Mode] Searching and stopping all related processes..." -ForegroundColor $ColorWarning
    
    $stoppedCount = 0
    
    # Stop Python/Flask processes
    $pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*run.py*" -or $_.CommandLine -like "*flask*"
    }
    
    foreach ($proc in $pythonProcesses) {
        try {
            Write-Host "  Stopping Python process (PID: $($proc.Id))..." -ForegroundColor $ColorInfo
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            $stoppedCount++
        } catch {}
    }
    
    # Stop Node.js processes
    $nodeProcesses = Get-Process -Name "node*" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*vite*" -or $_.CommandLine -like "*npm*"
    }
    
    foreach ($proc in $nodeProcesses) {
        try {
            Write-Host "  Stopping Node.js process (PID: $($proc.Id))..." -ForegroundColor $ColorInfo
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            $stoppedCount++
        } catch {}
    }
    
    if ($stoppedCount -gt 0) {
        Write-Host ""
        Write-Host "OK Stopped $stoppedCount processes" -ForegroundColor $ColorSuccess
    } else {
        Write-Host ""
        Write-Host "No related processes found" -ForegroundColor $ColorWarning
    }
}

# Main logic
$backendStopped = $false
$frontendStopped = $false

if ($Force) {
    # Force mode: stop all related processes
    Stop-AllRelatedProcesses
    
    # Clean up PID files
    if (Test-Path $BackendPidFile) { Remove-Item $BackendPidFile -Force -ErrorAction SilentlyContinue }
    if (Test-Path $FrontendPidFile) { Remove-Item $FrontendPidFile -Force -ErrorAction SilentlyContinue }
} else {
    # Normal mode: stop services by parameter
    if ($BackendOnly) {
        $backendStopped = Stop-ServiceByPidFile -PidFile $BackendPidFile -ServiceName "Backend"
    } elseif ($FrontendOnly) {
        $frontendStopped = Stop-ServiceByPidFile -PidFile $FrontendPidFile -ServiceName "Frontend"
    } else {
        $backendStopped = Stop-ServiceByPidFile -PidFile $BackendPidFile -ServiceName "Backend"
        $frontendStopped = Stop-ServiceByPidFile -PidFile $FrontendPidFile -ServiceName "Frontend"
    }
    
    # Show summary
    Write-Host ""
    Write-Host "========================================" -ForegroundColor $ColorInfo
    Write-Host "Stop Summary:" -ForegroundColor $ColorInfo
    
    if ($BackendOnly -or (-not $FrontendOnly)) {
        if ($backendStopped) {
            Write-Host "  - Backend: Stopped" -ForegroundColor $ColorSuccess
        } else {
            Write-Host "  - Backend: Not running or failed to stop" -ForegroundColor $ColorWarning
        }
    }
    
    if ($FrontendOnly -or (-not $BackendOnly)) {
        if ($frontendStopped) {
            Write-Host "  - Frontend: Stopped" -ForegroundColor $ColorSuccess
        } else {
            Write-Host "  - Frontend: Not running or failed to stop" -ForegroundColor $ColorWarning
        }
    }
    
    Write-Host "========================================" -ForegroundColor $ColorInfo
}

Write-Host ""
Write-Host "Tip: Use .\start-all.ps1 to restart services" -ForegroundColor $ColorInfo
