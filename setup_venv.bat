@echo off
echo 正在为后端创建虚拟环境...

cd backend

echo 1. 创建虚拟环境...
python -m venv venv

echo 2. 激活虚拟环境...
call venv\Scripts\activate.bat

echo 3. 升级pip...
python -m pip install --upgrade pip

echo 4. 安装项目依赖...
pip install -r requirements.txt

echo 虚拟环境设置完成!
echo 现在可以使用 'backend\venv\Scripts\activate.bat' 来激活虚拟环境
echo 或者使用 'backend\venv\Scripts\python.exe' 直接使用虚拟环境中的Python

cd ..
pause
