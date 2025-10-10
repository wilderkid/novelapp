Write-Host "正在安装 StoryForge (故事熔炉) 环境依赖..." -ForegroundColor Green

Write-Host "1. 安装前端依赖..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

Write-Host "2. 安装后端依赖..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt
Set-Location ..

Write-Host "3. 创建静态资源目录..." -ForegroundColor Yellow
if (!(Test-Path "backend\static\uploads")) {
    New-Item -ItemType Directory -Path "backend\static\uploads"
}

Write-Host "4. 创建环境变量文件..." -ForegroundColor Yellow
if (!(Test-Path "backend\.env")) {
    Write-Host "正在创建 .env 文件..." -ForegroundColor Cyan
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "请修改 backend\.env 文件中的数据库连接信息和AI API配置" -ForegroundColor Cyan
}

Write-Host "安装完成!" -ForegroundColor Green
Write-Host "请确保已安装 PostgreSQL 数据库，并执行 database\init.sql 初始化数据库" -ForegroundColor Cyan
Write-Host "然后运行 .\start.ps1 启动应用" -ForegroundColor Cyan

Read-Host "按 Enter 键退出"
