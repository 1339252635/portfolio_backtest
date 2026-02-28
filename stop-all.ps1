# 投资组合回测系统 - 一键停止脚本
# 停止所有正在运行的后端和前端服务

# 设置UTF-8编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$Force,
    [switch]$Help
)

# 显示帮助信息
if ($Help) {
    Write-Host @"
投资组合回测系统 - 停止脚本

用法: .\stop-all.ps1 [选项]

选项:
    -BackendOnly    仅停止后端服务
    -FrontendOnly   仅停止前端服务
    -Force          强制停止（包括非脚本启动的进程）
    -Help           显示帮助信息

示例:
    .\stop-all.ps1              # 停止所有服务
    .\stop-all.ps1 -BackendOnly # 仅停止后端服务
    .\stop-all.ps1 -Force       # 强制停止所有相关进程
"@ -ForegroundColor Cyan
    exit 0
}

# 设置窗口标题
$host.ui.RawUI.WindowTitle = "投资组合回测系统 - 服务停止器"

# 颜色定义
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"

# 项目路径
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPidFile = Join-Path $ProjectRoot ".backend.pid"
$FrontendPidFile = Join-Path $ProjectRoot ".frontend.pid"

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║          投资组合回测系统 - 服务停止管理器                   ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor $ColorInfo

# 停止服务的函数
function Stop-ServiceByPidFile {
    param($PidFile, $ServiceName)
    
    $stopped = $false
    
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($pid) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "[$ServiceName] 正在停止进程 (PID: $pid)..." -ForegroundColor $ColorWarning
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Seconds 1
                    
                    # 确认进程已停止
                    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if (-not $process) {
                        Write-Host "[$ServiceName] ✓ 已停止" -ForegroundColor $ColorSuccess
                        $stopped = $true
                    } else {
                        Write-Host "[$ServiceName] ✗ 停止失败" -ForegroundColor $ColorError
                    }
                } else {
                    Write-Host "[$ServiceName] 进程已不存在" -ForegroundColor $ColorWarning
                    $stopped = $true
                }
            } catch {
                Write-Host "[$ServiceName] 停止时出错: $_" -ForegroundColor $ColorError
            }
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "[$ServiceName] 未找到运行记录" -ForegroundColor $ColorWarning
    }
    
    return $stopped
}

# 强制停止所有相关进程
function Stop-AllRelatedProcesses {
    Write-Host "`n[强制模式] 正在搜索并停止所有相关进程..." -ForegroundColor $ColorWarning
    
    $stoppedCount = 0
    
    # 停止 Python/Flask 进程
    $pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*run.py*" -or $_.CommandLine -like "*flask*"
    }
    
    foreach ($proc in $pythonProcesses) {
        try {
            Write-Host "  停止 Python 进程 (PID: $($proc.Id))..." -ForegroundColor $ColorInfo
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            $stoppedCount++
        } catch {}
    }
    
    # 停止 Node.js 进程
    $nodeProcesses = Get-Process -Name "node*" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*vite*" -or $_.CommandLine -like "*npm*"
    }
    
    foreach ($proc in $nodeProcesses) {
        try {
            Write-Host "  停止 Node.js 进程 (PID: $($proc.Id))..." -ForegroundColor $ColorInfo
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            $stoppedCount++
        } catch {}
    }
    
    if ($stoppedCount -gt 0) {
        Write-Host "`n✓ 已强制停止 $stoppedCount 个进程" -ForegroundColor $ColorSuccess
    } else {
        Write-Host "`n未找到相关进程" -ForegroundColor $ColorWarning
    }
}

# 主逻辑
$backendStopped = $false
$frontendStopped = $false

if ($Force) {
    # 强制模式：停止所有相关进程
    Stop-AllRelatedProcesses
    
    # 清理PID文件
    if (Test-Path $BackendPidFile) { Remove-Item $BackendPidFile -Force -ErrorAction SilentlyContinue }
    if (Test-Path $FrontendPidFile) { Remove-Item $FrontendPidFile -Force -ErrorAction SilentlyContinue }
} else {
    # 正常模式：根据参数停止服务
    if ($BackendOnly) {
        $backendStopped = Stop-ServiceByPidFile -PidFile $BackendPidFile -ServiceName "后端服务"
    } elseif ($FrontendOnly) {
        $frontendStopped = Stop-ServiceByPidFile -PidFile $FrontendPidFile -ServiceName "前端服务"
    } else {
        $backendStopped = Stop-ServiceByPidFile -PidFile $BackendPidFile -ServiceName "后端服务"
        $frontendStopped = Stop-ServiceByPidFile -PidFile $FrontendPidFile -ServiceName "前端服务"
    }
    
    # 显示总结
    Write-Host "`n══════════════════════════════════════════════════════════════" -ForegroundColor $ColorInfo
    Write-Host "停止总结:" -ForegroundColor $ColorInfo
    
    if ($BackendOnly -or (-not $FrontendOnly)) {
        if ($backendStopped) {
            Write-Host "  • 后端服务: 已停止" -ForegroundColor $ColorSuccess
        } else {
            Write-Host "  • 后端服务: 未运行或停止失败" -ForegroundColor $ColorWarning
        }
    }
    
    if ($FrontendOnly -or (-not $BackendOnly)) {
        if ($frontendStopped) {
            Write-Host "  • 前端服务: 已停止" -ForegroundColor $ColorSuccess
        } else {
            Write-Host "  • 前端服务: 未运行或停止失败" -ForegroundColor $ColorWarning
        }
    }
    
    Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor $ColorInfo
}

Write-Host "`n提示: 使用 .\start-all.ps1 重新启动服务" -ForegroundColor $ColorInfo
