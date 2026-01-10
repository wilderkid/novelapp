const { app, BrowserWindow, Menu } = require("electron");
const path = require("path");

// 保持对窗口对象的全局引用，如果不这样做，当JavaScript对象被垃圾回收时，窗口将自动关闭
let mainWindow;

function createWindow() {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false,
    },
    icon: path.join(__dirname, "assets/icon.png"),
  });

  // 加载应用的index.html
  mainWindow.loadURL("http://localhost:5173");

  // 打开开发者工具
  // mainWindow.webContents.openDevTools();

  // 当窗口关闭时触发
  mainWindow.on("closed", () => {
    // 取消引用window对象，如果你的应用支持多窗口的话，通常会把多个window对象存放在一个数组里面，与此同时，你应该删除相应的元素
    mainWindow = null;
  });
}

// 当Electron完成初始化并准备创建浏览器窗口时调用此方法
app.whenReady().then(() => {
  createWindow();

  // 在macOS上，当点击dock图标并且没有其他窗口打开时，通常在应用程序中重新创建一个窗口
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// 当所有窗口关闭时退出应用
app.on("window-all-closed", () => {
  // 在macOS上，应用程序及其菜单栏通常保持活动状态，直到用户使用Cmd + Q明确退出
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// 创建菜单
const template = [
  {
    label: "文件",
    submenu: [
      {
        label: "新建项目",
        accelerator: "CmdOrCtrl+N",
        click: () => {
          // 新建项目功能
        },
      },
      {
        label: "打开项目",
        accelerator: "CmdOrCtrl+O",
        click: () => {
          // 打开项目功能
        },
      },
      {
        label: "保存项目",
        accelerator: "CmdOrCtrl+S",
        click: () => {
          // 保存项目功能
        },
      },
      { type: "separator" },
      {
        label: "退出",
        accelerator: process.platform === "darwin" ? "Cmd+Q" : "Ctrl+Q",
        click: () => {
          app.quit();
        },
      },
    ],
  },
  {
    label: "编辑",
    submenu: [
      { label: "撤销", accelerator: "CmdOrCtrl+Z", role: "undo" },
      { label: "重做", accelerator: "Shift+CmdOrCtrl+Z", role: "redo" },
      { type: "separator" },
      { label: "剪切", accelerator: "CmdOrCtrl+X", role: "cut" },
      { label: "复制", accelerator: "CmdOrCtrl+C", role: "copy" },
      { label: "粘贴", accelerator: "CmdOrCtrl+V", role: "paste" },
    ],
  },
  {
    label: "AI助手",
    submenu: [
      {
        label: "打开AI助手",
        accelerator: "CmdOrCtrl+I",
        click: () => {
          // 打开AI助手功能
        },
      },
    ],
  },
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);
