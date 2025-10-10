Write-Host "正在启动 StoryForge (故事熔炉)..." -ForegroundColor Green

Write-Host "1. 启动后端服务..." -ForegroundColor Yellow
Set-Location backend
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "激活虚拟环境..." -ForegroundColor Cyan
    Start-Process cmd -ArgumentList "/k", "call venv\Scripts\activate.bat && python main.py"
}
else {
    Write-Host "警告: 未找到虚拟环境，使用系统Python" -ForegroundColor Red
    Write-Host "建议先运行 setup_venv.bat 创建虚拟环境" -ForegroundColor Yellow
    Start-Process cmd -ArgumentList "/k", "python main.py"
}
Set-Location ..

Write-Host "2. 等待后端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "3. 启动前端应用..." -ForegroundColor Yellow
Set-Location frontend
Start-Process cmd -ArgumentList "/k", "npm run dev"
Set-Location ..

Write-Host "StoryForge 已启动完成!" -ForegroundColor Green
Write-Host "前端应用地址: http://localhost:5173" -ForegroundColor Cyan
Write-Host "后端API地址: http://localhost:9009" -ForegroundColor Cyan
Write-Host "API文档地址: http://localhost:9009/docs" -ForegroundColor Cyan

Read-Host "按 Enter 键退出"
