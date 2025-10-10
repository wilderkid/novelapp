
/**
 * UEditorPlus 配置文件 - 小说写作专用版本
 * 针对小说写作场景优化，移除了不必要的复杂功能
 */
window.UEDITOR_CONFIG = {
  // 为编辑器实例添加一个路径，不能使用相对路径
  UEDITOR_HOME_URL: '/static/UEditorPlus/',
  // 服务器统一请求接口路径
  serverUrl: '/api/ueditor',
  
  // 工具栏配置 - 针对小说写作场景优化
  toolbars: [
    [
      // 基础操作组
      'undo', 'redo', '|',
      // 文本格式化组
      'bold', 'italic', 'underline', 'strikethrough', '|',
      // 段落格式组
      'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|',
      // 列表组
      'insertorderedlist', 'insertunorderedlist', '|',
      // 字体组
      'fontfamily', 'fontsize', 'forecolor', 'backcolor', '|',
      // 行距和缩进组
      'lineheight', 'indent', '|',
      // 特殊格式组
      'blockquote', 'horizontal', '|',
      // 查找替换组
      'searchreplace', '|',
      // 全屏和源码组
      'fullscreen', 'source'
    ]
  ],
  
  // 小说写作场景专用配置
  // 启用自动排版，适合小说格式
  autoTypeset: {
    mergeEmptyline: true,        // 合并空行
    removeClass: true,           // 去掉冗余的class
    removeEmptyline: false,      // 去掉空行（小说需要空行分段）
    textAlign: "justify",        // 两端对齐（小说常用）
    imageBlockLine: "center",    // 图片居中
    pasteFilter: true,           // 过滤粘贴内容
    clearFontSize: false,        // 保留字体大小
    clearFontFamily: false,      // 保留字体
    removeEmptyNode: false,      // 保留空节点
    indent: true,                // 行首缩进
    indentValue: "2em",          // 缩进2字符（小说标准）
    bdc2sb: false,
    tobdc: false
  },
  
  // 自定义样式，适合小说章节
  customstyle: [
    {
      tag: 'h1',
      name: 'tc',
      style: 'font-size:32px;font-weight:bold;text-align:center;margin:16px 0;'
    },
    {
      tag: 'h2',
      name: 'chapter',
      style: 'font-size:24px;font-weight:bold;text-align:center;margin:20px 0;'
    },
    {
      tag: 'h3',
      name: 'section',
      style: 'font-size:18px;font-weight:bold;text-align:left;margin:16px 0;'
    },
    {
      tag: 'p',
      name: 'body',
      style: 'font-size:16px;line-height:1.8;text-indent:2em;margin:8px 0;'
    }
  ],
  
  // 字体配置，适合中文小说
  fontfamily: [
    { label: '宋体', name: 'SimSun', val: '宋体,SimSun'},
    { label: '仿宋', name: 'FangSong', val: '仿宋,FangSong'},
    { label: '楷体', name: 'KaiTi', val: '楷体,KaiTi'},
    { label: '黑体', name: 'SimHei', val: '黑体,SimHei'},
    { label: '微软雅黑', name: 'Microsoft YaHei', val: '微软雅黑,Microsoft YaHei'},
    { label: 'Arial', name: 'Arial', val: 'arial,helvetica,sans-serif'},
    { label: 'Times New Roman', name: 'Times New Roman', val: 'times new roman,times'}
  ],
  
  // 字号配置
  fontsize: [10, 12, 14, 16, 18, 20, 24, 28, 32, 36],
  
  // 段落格式配置
  paragraph: {
    'p': '',
    'h1': '标题 1',
    'h2': '标题 2',
    'h3': '标题 3',
    'h4': '标题 4',
    'h5': '标题 5'
  },
  
  // 行间距配置
  lineheight: ['1', '1.2', '1.5', '1.8', '2', '2.5', '3'],
  
  // 快捷菜单配置（右键菜单）
  shortcutMenu: [
    "fontfamily", // 字体
    "fontsize",   // 字号
    "bold",       // 加粗
    "italic",     // 斜体
    "underline",  // 下划线
    "forecolor",  // 字体颜色
    "backcolor",  // 背景色
    "justifyleft", // 居左
    "justifycenter", // 居中
    "justifyright", // 居右
    "insertorderedlist", // 有序列表
    "insertunorderedlist", // 无序列表
    "lineheight", // 行间距
    "link",       // 超链接
    "unlink"      // 取消链接
  ],
  
  // 字数统计配置
  wordCount: true,
  maximumWords: 100000,  // 最大字数10万（适合长篇小说）
  
  // 自动保存配置
  autoSaveEnable: true,
  autoSaveKey: 'novel_chapter_content',
  autoSaveInterval: 30000, // 30秒自动保存一次
  
  // 编辑器尺寸配置
  initialFrameHeight: 600,  // 初始高度600px
  initialFrameWidth: '100%', // 宽度100%
  autoHeightEnabled: true,   // 启用自动高度
  
  // 其他配置
  enableContextMenu: true,   // 启用右键菜单
  elementPathEnabled: false, // 禁用元素路径（减少干扰）
  catchRemoteImageEnable: false, // 禁用远程图片抓取
  allowDivTransToP: true,    // 允许div转p标签
  rgb2Hex: true,             // RGB转十六进制
  pasteplain: false,         // 不强制纯文本粘贴
  selectall: true,           // 启用全选功能
  cleardoc: true             // 启用清空文档功能
};
