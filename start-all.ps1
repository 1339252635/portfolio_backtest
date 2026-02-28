# 投资组合回测系统 - 一键启动脚本
# 同时启动后端Flask服务和前端Vue开发服务器

# 设置UTF-8编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser,
    [switch]$Help
)

# 显示帮助信息
if ($Help) {
    Write-Host @"
投资组合回测系统 - 启动脚本

用法: .\start-all.ps1 [选项]

选项:
    -BackendOnly    仅启动后端服务
    -FrontendOnly   仅启动前端服务
    -NoBrowser      不自动打开浏览器
    -Help           显示帮助信息

示例:
    .\start-all.ps1              # 启动前后端所有服务
    .\start-all.ps1 -BackendOnly # 仅启动后端服务
    .\start-all.ps1 -FrontendOnly # 仅启动前端服务
    .\start-all.ps1 -NoBrowser   # 启动服务但不打开浏览器
"@ -ForegroundColor Cyan
    exit 0
}

# 设置窗口标题
$host.ui.RawUI.WindowTitle = "投资组合回测系统 - 服务管理器"

# 颜色定义
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"

# 项目路径
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPath = Join-Path $ProjectRoot "backend"
$FrontendPath = Join-Path $ProjectRoot "frontend"

# PID文件路径
$BackendPidFile = Join-Path $ProjectRoot ".backend.pid"
$FrontendPidFile = Join-Path $ProjectRoot ".frontend.pid"

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║          投资组合回测系统 - 服务启动管理器                   ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor $ColorInfo

# 检查并清理已存在的进程
function Stop-ExistingProcess {
    param($PidFile, $ServiceName)
    
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($pid) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "[$ServiceName] 检测到已运行的进程 (PID: $pid)，正在停止..." -ForegroundColor $ColorWarning
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Seconds 2
                }
            } catch {}
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
}

# 启动后端服务
function Start-BackendService {
    Write-Host "`n[后端服务] 正在启动 Flask 服务..." -ForegroundColor $ColorInfo
    
    # 检查后端目录
    if (-not (Test-Path $BackendPath)) {
        Write-Host "[后端服务] 错误: 找不到后端目录 $BackendPath" -ForegroundColor $ColorError
        return $false
    }
    
    # 检查 run.py 是否存在
    $runPyPath = Join-Path $BackendPath "run.py"
    if (-not (Test-Path $runPyPath)) {
        Write-Host "[后端服务] 错误: 找不到 run.py" -ForegroundColor $ColorError
        return $false
    }
    
    # 清理已存在的进程
    Stop-ExistingProcess -PidFile $BackendPidFile -ServiceName "后端服务"
    
    try {
        # 启动后端进程
        $backendProcess = Start-Process -FilePath "py" -ArgumentList "run.py" -WorkingDirectory $BackendPath -PassThru -WindowStyle Minimized
        
        if ($backendProcess) {
            $backendProcess.Id | Out-File $BackendPidFile
            Write-Host "[后端服务] ✓ 启动成功 (PID: $($backendProcess.Id))" -ForegroundColor $ColorSuccess
            Write-Host "[后端服务]   地址: http://localhost:5000" -ForegroundColor $ColorInfo
            return $true
        }
    } catch {
        Write-Host "[后端服务] ✗ 启动失败: $_" -ForegroundColor $ColorError
        return $false
    }
    
    return $false
}

# 启动前端服务
function Start-FrontendService {
    Write-Host "`n[前端服务] 正在启动 Vue 开发服务器..." -ForegroundColor $ColorInfo
    
    # 检查前端目录
    if (-not (Test-Path $FrontendPath)) {
        Write-Host "[前端服务] 错误: 找不到前端目录 $FrontendPath" -ForegroundColor $ColorError
        return $false
    }
    
    # 检查 package.json 是否存在
    $packageJsonPath = Join-Path $FrontendPath "package.json"
    if (-not (Test-Path $packageJsonPath)) {
        Write-Host "[前端服务] 错误: 找不到 package.json" -ForegroundColor $ColorError
        return $false
    }
    
    # 清理已存在的进程
    Stop-ExistingProcess -PidFile $FrontendPidFile -ServiceName "前端服务"
    
    try {
        # 启动前端进程
        $frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $FrontendPath -PassThru -WindowStyle Minimized
        
        if ($frontendProcess) {
            $frontendProcess.Id | Out-File $FrontendPidFile
            Write-Host "[前端服务] ✓ 启动成功 (PID: $($frontendProcess.Id))" -ForegroundColor $ColorSuccess
            Write-Host "[前端服务]   地址: http://localhost:3000" -ForegroundColor $ColorInfo
            return $true
        }
    } catch {
        Write-Host "[前端服务] ✗ 启动失败: $_" -ForegroundColor $ColorError
        return $false
    }
    
    return $false
}

# 主逻辑
$backendStarted = $false
$frontendStarted = $false

if ($BackendOnly) {
    $backendStarted = Start-BackendService
} elseif ($FrontendOnly) {
    $frontendStarted = Start-FrontendService
} else {
    $backendStarted = Start-BackendService
    
    # 等待后端启动
    if ($backendStarted) {
        Write-Host "`n等待后端服务初始化..." -ForegroundColor $ColorInfo
        Start-Sleep -Seconds 3
    }
    
    $frontendStarted = Start-FrontendService
}

# 显示总结
Write-Host "`n══════════════════════════════════════════════════════════════" -ForegroundColor $ColorInfo
Write-Host "启动总结:" -ForegroundColor $ColorInfo

if ($BackendOnly -or (-not $FrontendOnly)) {
    if ($backendStarted) {
        Write-Host "  • 后端服务: 运行中 (http://localhost:5000)" -ForegroundColor $ColorSuccess
    } else {
        Write-Host "  • 后端服务: 启动失败" -ForegroundColor $ColorError
    }
}

if ($FrontendOnly -or (-not $BackendOnly)) {
    if ($frontendStarted) {
        Write-Host "  • 前端服务: 运行中 (http://localhost:3000)" -ForegroundColor $ColorSuccess
    } else {
        Write-Host "  • 前端服务: 启动失败" -ForegroundColor $ColorError
    }
}

Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor $ColorInfo

# 提示如何停止服务
Write-Host "`n提示: 使用 .\stop-all.ps1 停止所有服务" -ForegroundColor $ColorWarning

# 如果全部启动成功，自动打开浏览器（除非指定了 -NoBrowser）
if (-not $NoBrowser) {
    if (($BackendOnly -and $backendStarted) -or 
        ($FrontendOnly -and $frontendStarted) -or 
        ((-not $BackendOnly -and -not $FrontendOnly) -and $backendStarted -and $frontendStarted)) {
        
        Write-Host "`n正在打开浏览器..." -ForegroundColor $ColorInfo
        Start-Sleep -Seconds 2
        
        if ($BackendOnly) {
            Start-Process "http://localhost:5000"
        } else {
            Start-Process "http://localhost:3000"
        }
    }
}
