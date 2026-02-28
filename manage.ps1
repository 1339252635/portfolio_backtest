# 投资组合回测系统 - 统一管理脚本
# 整合启动、停止、状态查看等功能

# 设置UTF-8编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "help")]
    [string]$Command = "help",

    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$Force,
    [switch]$NoBrowser
)

# 颜色定义
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"

# 项目路径
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPidFile = Join-Path $ProjectRoot ".backend.pid"
$FrontendPidFile = Join-Path $ProjectRoot ".frontend.pid"

# 显示Logo
function Show-Logo {
    Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     📊 投资组合回测系统 - 服务管理工具                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor $ColorInfo
}

# 显示帮助信息
function Show-Help {
    Show-Logo
    Write-Host @"
用法: .\manage.ps1 <命令> [选项]

命令:
    start     启动服务
    stop      停止服务
    restart   重启服务
    status    查看服务状态
    logs      查看服务日志
    help      显示帮助信息

选项:
    -BackendOnly   仅操作后端服务
    -FrontendOnly  仅操作前端服务
    -Force         强制停止（用于stop命令）
    -NoBrowser     启动时不自动打开浏览器

示例:
    .\manage.ps1 start                    # 启动所有服务
    .\manage.ps1 start -BackendOnly       # 仅启动后端服务
    .\manage.ps1 stop                     # 停止所有服务
    .\manage.ps1 stop -Force              # 强制停止所有服务
    .\manage.ps1 restart                  # 重启所有服务
    .\manage.ps1 status                   # 查看服务状态

快捷方式:
    .\start-all.ps1    # 等同于 .\manage.ps1 start
    .\stop-all.ps1     # 等同于 .\manage.ps1 stop
"@ -ForegroundColor White
}

# 获取服务状态
function Get-ServiceStatus {
    $backendRunning = $false
    $frontendRunning = $false
    $backendPid = $null
    $frontendPid = $null

    # 检查后端服务
    if (Test-Path $BackendPidFile) {
        $backendPid = Get-Content $BackendPidFile -ErrorAction SilentlyContinue
        if ($backendPid) {
            $backendProcess = Get-Process -Id $backendPid -ErrorAction SilentlyContinue
            $backendRunning = ($null -ne $backendProcess)
        }
    }

    # 检查前端服务
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

# 显示服务状态
function Show-Status {
    Show-Logo
    Write-Host "服务状态:`n" -ForegroundColor $ColorInfo

    $status = Get-ServiceStatus

    # 后端状态
    if ($status.BackendRunning) {
        Write-Host "  🟢 后端服务: 运行中" -ForegroundColor $ColorSuccess
        Write-Host "     PID: $($status.BackendPid)" -ForegroundColor White
        Write-Host "     地址: http://localhost:5000" -ForegroundColor White
    } else {
        Write-Host "  🔴 后端服务: 已停止" -ForegroundColor $ColorError
    }

    Write-Host ""

    # 前端状态
    if ($status.FrontendRunning) {
        Write-Host "  🟢 前端服务: 运行中" -ForegroundColor $ColorSuccess
        Write-Host "     PID: $($status.FrontendPid)" -ForegroundColor White
        Write-Host "     地址: http://localhost:3000" -ForegroundColor White
    } else {
        Write-Host "  🔴 前端服务: 已停止" -ForegroundColor $ColorError
    }

    Write-Host ""

    # 总体状态
    if ($status.BackendRunning -and $status.FrontendRunning) {
        Write-Host "✓ 所有服务运行正常" -ForegroundColor $ColorSuccess
    } elseif ($status.BackendRunning -or $status.FrontendRunning) {
        Write-Host "⚠ 部分服务未运行" -ForegroundColor $ColorWarning
    } else {
        Write-Host "✗ 所有服务已停止" -ForegroundColor $ColorError
    }
}

# 启动服务
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
        Write-Host "错误: 找不到启动脚本 start-all.ps1" -ForegroundColor $ColorError
    }
}

# 停止服务
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
        Write-Host "错误: 找不到停止脚本 stop-all.ps1" -ForegroundColor $ColorError
    }
}

# 重启服务
function Restart-Services {
    Show-Logo
    Write-Host "正在重启服务...`n" -ForegroundColor $ColorInfo

    # 先停止
    $stopParams = @()
    if ($BackendOnly) { $stopParams += "-BackendOnly" }
    if ($FrontendOnly) { $stopParams += "-FrontendOnly" }

    $stopScript = Join-Path $ProjectRoot "stop-all.ps1"
    if (Test-Path $stopScript) {
        & $stopScript @stopParams
    }

    Start-Sleep -Seconds 2

    Write-Host "`n" -NoNewline

    # 再启动
    $startParams = @()
    if ($BackendOnly) { $startParams += "-BackendOnly" }
    if ($FrontendOnly) { $startParams += "-FrontendOnly" }
    if ($NoBrowser) { $startParams += "-NoBrowser" }

    $startScript = Join-Path $ProjectRoot "start-all.ps1"
    if (Test-Path $startScript) {
        & $startScript @startParams
    }
}

# 查看日志
function Show-Logs {
    Show-Logo
    Write-Host "日志查看功能开发中..." -ForegroundColor $ColorWarning
    Write-Host "`n您可以使用以下命令手动查看日志:" -ForegroundColor $ColorInfo
    Write-Host "  Get-Content .\backend\logs\*.log -Tail 50 -Wait" -ForegroundColor White
}

# 主逻辑
switch ($Command.ToLower()) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" { Restart-Services }
    "status" { Show-Status }
    "logs" { Show-Logs }
    default { Show-Help }
}

Write-Host ""
