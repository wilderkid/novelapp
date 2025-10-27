# StoryForge (故事熔炉)

<div align="center">
  <strong>一款集成 AI 助手的桌面端智能小说创作工具</strong>
</div>

<p align="center">
  <img alt="Language" src="https://img.shields.io/badge/language-Python%20%7C%20Vue.js-blue?style=flat-square" />
  <img alt="Backend" src="https://img.shields.io/badge/backend-FastAPI-green?style=flat-square" />
  <img alt="Frontend" src="https://img.shields.io/badge/frontend-Vue.js%20%7C%20Element%20Plus-brightgreen?style=flat-square" />
  <img alt="Desktop" src="https://img.shields.io/badge/desktop-Electron-lightgrey?style=flat-square" />
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blueviolet.svg?style=flat-square" />
</p>

---

**StoryForge (故事熔炉)** 是一款专为小说家和创作者设计的桌面应用程序，旨在将人工智能（AI）的强大能力融入写作流程。它提供了一个结构化的环境来管理小说项目、章节和世界观设定，同时集成了强大的 AI 助手，帮助您激发灵感、生成内容、润色文字，从而极大地提升创作效率和体验。

## ✨ 核心功能

- **📚 多项目管理**: 同时管理多个小说项目，每个项目都有独立的资源和设定。
- **📝 章节式写作**: 以卷、章、节的结构组织您的故事，支持富文本编辑。
- **🤖 AI 创作助手**: 
    - **智能续写**: 在您卡文时提供思路和下文建议。
    - **润色和改写**: 优化您的文字，提供多种风格和语气的修改方案。
    - **创意生成**: 帮助您构思角色、情节、对话和场景。
- **🌍 世界观设定**: 结构化地管理您的角色、地点、物品和自定义设定，方便随时查阅。
- **✒️ 富文本编辑器**: 内置强大的 `UEditorPlus` 编辑器，支持丰富的格式和多媒体内容。
- **💻 桌面端应用**: 基于 Electron 构建，提供跨平台的稳定本地体验。

## 🛠️ 技术栈

- **后端**: FastAPI, SQLAlchemy, PostgreSQL
- **前端**: Vue.js 3, Pinia, Element Plus, Vite
- **桌面端**: Electron
- **核心编辑器**: UEditorPlus

## 🚀 安装与启动

<details>
<summary><strong>点击展开详细的安装与启动指南</strong></summary>

### StoryForge (故事熔炉) 启动指南

本指南旨在帮助开发者，特别是初次接触本项目的新手，顺利完成 StoryForge 项目的本地环境搭建和启动。

#### 目录
- [1. 环境准备](#1-环境准备)
- [2. 安装步骤](#2-安装步骤)
  - [2.1. 自动化安装 (推荐)](#21-自动化安装-推荐)
  - [2.2. 手动安装 (适用于解决问题)](#22-手动安装-适用于解决问题)
- [3. 启动应用](#3-启动应用)
  - [3.1. 使用脚本启动](#31-使用脚本启动)
  - [3.2. 手动启动](#32-手动启动)
- [4. 访问应用](#4-访问应用)
- [5. 常见问题 (FAQ)](#5-常见问题-faq)

---

#### 1. 环境准备

在开始之前，请确保您的电脑上已经安装了以下软件。

| 软件 | 版本建议 | 安装验证 |
| :--- | :--- | :--- |
| **Python** | 3.8 或更高 | `python --version` |
| **Node.js** | 14.0 或更高 | `node --version` 和 `npm --version` |
| **PostgreSQL** | 任意稳定版本 | 确保服务正在运行 |

**重要提示:**
- 请确保 `python`, `node`, `npm` 命令已被添加到系统的环境变量中，可以在命令行/终端中直接运行。
- 如果命令未找到，请先搜索如何将它们添加到系统环境变量。

---

#### 2. 安装步骤

##### 2.1. 自动化安装 (推荐)

项目根目录提供了 `install.bat` (适用于 Windows CMD) 和 `install.ps1` (适用于 PowerShell) 脚本，可以一键完成大部分安装工作。

**操作:**
- **对于 CMD 用户:** 直接双击 `install.bat` 或在命令行中运行 `install.bat`。
- **对于 PowerShell 用户:** 右键以管理员身份运行 PowerShell，然后执行 `.\install.ps1`。

**该脚本会自动完成以下工作:**
1.  安装前端所有 `npm` 依赖。
2.  在 `backend` 目录下创建 Python 虚拟环境 (`venv`)。
3.  激活虚拟环境并安装所有 `pip` 依赖。
4.  在 `backend` 目录下，从 `.env.example` 复制生成 `.env` 文件，用于存放环境变量。

**自动化安装后，您仍需手动完成 [数据库配置](#224-配置数据库)。**

##### 2.2. 手动安装 (适用于解决问题)

如果自动化脚本执行失败，或者您想更深入地了解项目结构，请遵循以下步骤手动安装。

###### 2.2.1. 克隆或下载项目

将项目代码克隆或下载到您的本地电脑。

###### 2.2.2. 安装后端依赖

后端使用 Python 虚拟环境以避免与系统环境产生冲突。

```bash
# 1. 进入后端目录
cd backend

# 2. 创建一个名为 venv 的虚拟环境
python -m venv venv

# 3. 激活虚拟环境
#    - Windows CMD:
call venv\Scripts\activate.bat
#    - Windows PowerShell:
#      (如果提示执行策略问题，请先以管理员身份运行 Set-ExecutionPolicy RemoteSigned -Scope CurrentUser)
.\venv\Scripts\Activate.ps1

# 4. (可选但推荐) 升级 pip
python -m pip install --upgrade pip

# 5. 安装所有 Python 依赖
pip install -r requirements.txt
```

###### 2.2.3. 安装前端依赖

```bash
# 1. (新开一个命令行窗口) 进入前端目录
cd frontend

# 2. 安装所有 npm 依赖
#    如果因网络问题安装缓慢或失败，可以尝试配置淘宝镜像源:
#    npm config set registry https://registry.npmmirror.com
npm install
```

###### 2.2.4. 配置数据库

1.  **启动 PostgreSQL 服务**。
2.  **创建数据库**: 创建一个名为 `storyforge` 的新数据库。
3.  **初始化表结构**: 使用 `psql` 工具连接到 `storyforge` 数据库，并执行 `database/init.sql` 脚本。
    ```bash
    # 示例: psql -U postgres -d storyforge -f ..\database\init.sql
    ```

###### 2.2.5. 配置环境变量

1.  进入 `backend` 目录，复制 `.env.example` 文件并重命名为 `.env`。
2.  打开 `.env` 文件，根据您的本地环境修改数据库连接信息和 AI API 密钥。

---

#### 3. 启动应用

##### 3.1. 使用脚本启动

项目根目录提供了 `start.bat` 和 `start.ps1` 脚本，可以一键启动前后端服务。

##### 3.2. 手动启动

- **启动后端**: 进入 `backend` 目录，激活虚拟环境 (`call venv\Scripts\activate.bat`)，然后运行 `python main.py`。
- **启动前端**: (新开一个命令行窗口) 进入 `frontend` 目录，运行 `npm run dev`。

---

#### 4. 访问应用

- **前端应用地址**: [http://localhost:5173](http://localhost:5173)
- **后端API地址**: [http://localhost:9009](http://localhost:9009)
- **API文档地址 (Swagger UI)**: [http://localhost:9009/docs](http://localhost:9009/docs)

---

#### 5. 常见问题 (FAQ)

**Q: 命令行提示 `python` 或 `node` 不是内部或外部命令?**
**A:** 这是因为 Python 或 Node.js 没有被正确添加到系统的环境变量 `Path` 中。

**Q: `npm install` 或 `pip install` 很慢或失败?**
**A:** 这通常是网络问题。可以为 `npm` 和 `pip` 配置国内镜像源来解决。

**Q: 数据库连接失败?**
**A:** 请确保 PostgreSQL 服务正在运行，并且 `backend/.env` 文件中的数据库连接信息正确无误。

</details>

## 📄 许可证

该项目采用 [MIT License](LICENSE) 授权。

## 🙌 贡献

我们欢迎任何形式的贡献！如果您有好的想法或发现了问题，请随时提出 Issue 或提交 Pull Request。

## 🙏 致谢

- 感谢所有为本项目提供支持的开源社区和工具。