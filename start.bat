@echo off
echo 正在启动 StoryForge (故事熔炉)...

echo 1. 初始化数据库...
cd backend
if exist venv\Scriptsctivate.bat (
    echo 激活虚拟环境...
    call venv\Scriptsctivate.bat
    python init_db.py
) else (
    echo 警告: 未找到虚拟环境，使用系统Python
    echo 建议先运行 setup_venv.bat 创建虚拟环境
    python init_db.py
)

echo 2. 启动后端服务...
if exist venv\Scriptsctivate.bat (
    echo 激活虚拟环境...
    call venv\Scriptsctivate.bat
    start cmd /k "call venv\Scriptsctivate.bat && python main.py"
) else (
    echo 警告: 未找到虚拟环境，使用系统Python
    echo 建议先运行 setup_venv.bat 创建虚拟环境
    start cmd /k "python main.py"
)
cd ..

echo 3. 等待后端服务启动...
timeout /t 5 /nobreak > NUL

echo 4. 启动前端应用...
cd frontend
start cmd /k "npm run dev"
cd ..

echo StoryForge 已启动完成!
echo 前端应用地址: http://localhost:5173
echo 后端API地址: http://localhost:9009
echo API文档地址: http://localhost:9009/docs

pause
