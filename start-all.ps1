# Portfolio Backtest System - Start Script
# Start both backend Flask and frontend Vue services

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser,
    [switch]$Help
)

# Show help
if ($Help) {
    Write-Host "Portfolio Backtest System - Start Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\start-all.ps1 [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "    -BackendOnly    Start only backend service" -ForegroundColor White
    Write-Host "    -FrontendOnly   Start only frontend service" -ForegroundColor White
    Write-Host "    -NoBrowser      Do not open browser" -ForegroundColor White
    Write-Host "    -Help           Show help" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "    .\start-all.ps1              # Start all services" -ForegroundColor White
    Write-Host "    .\start-all.ps1 -BackendOnly # Start backend only" -ForegroundColor White
    Write-Host "    .\start-all.ps1 -NoBrowser   # Start without opening browser" -ForegroundColor White
    exit 0
}

# Set window title
$host.ui.RawUI.WindowTitle = "Portfolio Backtest - Service Manager"

# Color definitions
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"

# Project paths
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPath = Join-Path $ProjectRoot "backend"
$FrontendPath = Join-Path $ProjectRoot "frontend"

# PID file paths
$BackendPidFile = Join-Path $ProjectRoot ".backend.pid"
$FrontendPidFile = Join-Path $ProjectRoot ".frontend.pid"

Write-Host "========================================" -ForegroundColor $ColorInfo
Write-Host "  Portfolio Backtest - Service Starter  " -ForegroundColor $ColorInfo
Write-Host "========================================" -ForegroundColor $ColorInfo

# Function to stop existing process
function Stop-ExistingProcess {
    param($PidFile, $ServiceName)
    
    if (Test-Path $PidFile) {
        $processId = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($processId) {
            try {
                $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "[$ServiceName] Stopping existing process (PID: $processId)..." -ForegroundColor $ColorWarning
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Seconds 2
                }
            } catch {}
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
}

# Start backend service
function Start-BackendService {
    Write-Host ""
    Write-Host "[Backend] Starting Flask service..." -ForegroundColor $ColorInfo
    
    if (-not (Test-Path $BackendPath)) {
        Write-Host "[Backend] Error: Backend directory not found" -ForegroundColor $ColorError
        return $false
    }
    
    $runPyPath = Join-Path $BackendPath "run.py"
    if (-not (Test-Path $runPyPath)) {
        Write-Host "[Backend] Error: run.py not found" -ForegroundColor $ColorError
        return $false
    }
    
    Stop-ExistingProcess -PidFile $BackendPidFile -ServiceName "Backend"
    
    try {
        $backendProcess = Start-Process -FilePath "py" -ArgumentList "run.py" -WorkingDirectory $BackendPath -PassThru -WindowStyle Minimized
        
        if ($backendProcess) {
            $backendProcess.Id | Out-File $BackendPidFile
            Write-Host "[Backend] OK Started (PID: $($backendProcess.Id))" -ForegroundColor $ColorSuccess
            Write-Host "[Backend] URL: http://localhost:5000" -ForegroundColor $ColorInfo
            return $true
        }
    } catch {
        Write-Host "[Backend] Failed to start: $_" -ForegroundColor $ColorError
        return $false
    }
    
    return $false
}

# Start frontend service
function Start-FrontendService {
    Write-Host ""
    Write-Host "[Frontend] Starting Vue dev server..." -ForegroundColor $ColorInfo
    
    if (-not (Test-Path $FrontendPath)) {
        Write-Host "[Frontend] Error: Frontend directory not found" -ForegroundColor $ColorError
        return $false
    }
    
    $packageJsonPath = Join-Path $FrontendPath "package.json"
    if (-not (Test-Path $packageJsonPath)) {
        Write-Host "[Frontend] Error: package.json not found" -ForegroundColor $ColorError
        return $false
    }
    
    Stop-ExistingProcess -PidFile $FrontendPidFile -ServiceName "Frontend"
    
    try {
        # Try to find npm
        $npmPaths = @(
            "C:\Program Files\nodejs\npm.cmd",
            "C:\Program Files (x86)\nodejs\npm.cmd",
            (Join-Path $env:ProgramFiles "nodejs\npm.cmd"),
            (Join-Path ${env:ProgramFiles(x86)} "nodejs\npm.cmd")
        )
        
        $npmCmd = $null
        foreach ($path in $npmPaths) {
            if (Test-Path $path) {
                $npmCmd = $path
                break
            }
        }
        
        if (-not $npmCmd) {
            $cmd = Get-Command "npm" -ErrorAction SilentlyContinue
            if ($cmd) {
                $npmCmd = $cmd.Source
            } else {
                $cmd = Get-Command "npm.cmd" -ErrorAction SilentlyContinue
                if ($cmd) {
                    $npmCmd = $cmd.Source
                }
            }
        }
        
        if (-not $npmCmd) {
            Write-Host "[Frontend] Error: npm not found. Please install Node.js" -ForegroundColor $ColorError
            Write-Host "[Frontend] Searched paths: $($npmPaths -join ', ')" -ForegroundColor $ColorWarning
            return $false
        }
        
        Write-Host "[Frontend] Using npm: $npmCmd" -ForegroundColor $ColorInfo
        
        # Start npm run dev - it will spawn node processes
        $process = Start-Process -FilePath $npmCmd -ArgumentList "run", "dev" -WorkingDirectory $FrontendPath -PassThru -WindowStyle Minimized
        
        if ($process) {
            # Wait for vite to start
            Start-Sleep -Seconds 5
            
            # Try to find the node process by checking port 3000
            $maxRetries = 10
            $retry = 0
            $found = $false
            
            while ($retry -lt $maxRetries -and -not $found) {
                Start-Sleep -Seconds 1
                
                # Check if port 3000 is listening
                $portCheck = netstat -ano | findstr ":3000" | findstr "LISTENING"
                if ($portCheck) {
                    # Port is open, service is running
                    $found = $true
                    break
                }
                $retry++
            }
            
            if ($found) {
                # Find any node process to use as PID (for stopping later)
                $nodeProcess = Get-Process -Name "node" -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($nodeProcess) {
                    $nodeProcess.Id | Out-File $FrontendPidFile
                    Write-Host "[Frontend] OK Started (PID: $($nodeProcess.Id))" -ForegroundColor $ColorSuccess
                } else {
                    # Fallback - use the npm process ID
                    $process.Id | Out-File $FrontendPidFile
                    Write-Host "[Frontend] OK Started (PID: $($process.Id))" -ForegroundColor $ColorSuccess
                }
                Write-Host "[Frontend] URL: http://localhost:3000" -ForegroundColor $ColorInfo
                return $true
            } else {
                Write-Host "[Frontend] Warning: Port 3000 not responding" -ForegroundColor $ColorWarning
                $process.Id | Out-File $FrontendPidFile
                Write-Host "[Frontend] OK Started (PID: $($process.Id))" -ForegroundColor $ColorSuccess
                Write-Host "[Frontend] URL: http://localhost:3000" -ForegroundColor $ColorInfo
                return $true
            }
        }
    } catch {
        Write-Host "[Frontend] Failed to start: $_" -ForegroundColor $ColorError
        return $false
    }
    
    return $false
}

# Main logic
$backendStarted = $false
$frontendStarted = $false

if ($BackendOnly) {
    $backendStarted = Start-BackendService
} elseif ($FrontendOnly) {
    $frontendStarted = Start-FrontendService
} else {
    $backendStarted = Start-BackendService
    
    if ($backendStarted) {
        Write-Host ""
        Write-Host "Waiting for backend initialization..." -ForegroundColor $ColorInfo
        Start-Sleep -Seconds 3
    }
    
    $frontendStarted = Start-FrontendService
}

# Show summary
Write-Host ""
Write-Host "========================================" -ForegroundColor $ColorInfo
Write-Host "Startup Summary:" -ForegroundColor $ColorInfo

if ($BackendOnly -or (-not $FrontendOnly)) {
    if ($backendStarted) {
        Write-Host "  - Backend: Running (http://localhost:5000)" -ForegroundColor $ColorSuccess
    } else {
        Write-Host "  - Backend: Failed to start" -ForegroundColor $ColorError
    }
}

if ($FrontendOnly -or (-not $BackendOnly)) {
    if ($frontendStarted) {
        Write-Host "  - Frontend: Running (http://localhost:3000)" -ForegroundColor $ColorSuccess
    } else {
        Write-Host "  - Frontend: Failed to start" -ForegroundColor $ColorError
    }
}

Write-Host "========================================" -ForegroundColor $ColorInfo

Write-Host ""
Write-Host "Tip: Use .\stop-all.ps1 to stop all services" -ForegroundColor $ColorWarning

# Open browser if not disabled
if (-not $NoBrowser) {
    if (($BackendOnly -and $backendStarted) -or 
        ($FrontendOnly -and $frontendStarted) -or 
        ((-not $BackendOnly -and -not $FrontendOnly) -and $backendStarted -and $frontendStarted)) {
        
        Write-Host ""
        Write-Host "Opening browser..." -ForegroundColor $ColorInfo
        Start-Sleep -Seconds 2
        
        if ($BackendOnly) {
            $url = "http://localhost:5000"
            Start-Process $url
        } else {
            $url = "http://localhost:3000"
            Start-Process $url
        }
    }
}
