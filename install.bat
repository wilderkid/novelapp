@echo off
echo 正在安装 StoryForge (故事熔炉) 环境依赖...

echo 1. 安装前端依赖...
cd frontend
call npm install
cd ..

echo 2. 创建后端虚拟环境...
cd backend
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
    echo 升级pip...
    python -m pip install --upgrade pip
    echo 安装后端依赖...
    pip install -r requirements.txt
) else (
    echo 虚拟环境已存在，激活并更新依赖...
    call venv\Scripts\activate.bat
    echo 升级pip...
    python -m pip install --upgrade pip
    echo 更新后端依赖...
    pip install -r requirements.txt
)
cd ..

echo 3. 创建静态资源目录...
if not exist "backend\static\uploads" mkdir "backend\static\uploads"

echo 4. 创建环境变量文件...
if not exist "backend\.env" (
    echo 正在创建 .env 文件...
    copy "backend\.env.example" "backend\.env"
    echo 请修改 backend\.env 文件中的数据库连接信息和AI API配置
)

echo 安装完成!
echo 请确保已安装 PostgreSQL 数据库，并执行 database\init.sql 初始化数据库
echo 然后运行 start.bat 启动应用

pause
