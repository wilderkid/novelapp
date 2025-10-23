
<template>
  <div class="ueditor-plus-container">
    <div ref="editorContainer" :id="editorId" style="height:100%"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useEditorStore } from '../stores/editorStore' // 引入Store

const editorStore = useEditorStore() // 获取Store实例

// 定义props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  editorId: {
    type: String,
    default: 'editor'
  },
  height: {
    type: String,
    default: '100%'
  }
})

// 定义emits
const emit = defineEmits(['update:modelValue', 'ready'])

// 暴露方法给父组件
defineExpose({
  forceRefresh: () => {
    // 保存当前内容
    const currentContent = editor ? editor.getContent() : props.modelValue || '';
    
    // 销毁旧编辑器
    const savedContent = destroyEditor();
    
    // 重新初始化编辑器
    nextTick(() => {
      initEditor(savedContent || currentContent);
    });
  },
  setContent: (content) => {
    if (editor && editor.setContent) {
      try {
        editor.setContent(content);
      } catch (e) {
        console.error('设置编辑器内容失败', e);
      }
    }
  },
  getContent: () => {
    if (editor && editor.getContent) {
      try {
        return editor.getContent();
      } catch (e) {
        console.error('获取编辑器内容失败', e);
        return '';
      }
    }
    return '';
  }
})

// 编辑器实例
let editor = null

// 编辑器容器引用
const editorContainer = ref(null)

// 编辑器初始化状态
let isEditorInitializing = false
let isEditorReady = false

// 销毁编辑器
const destroyEditor = () => {
  if (editor) {
    try {
      // 检查编辑器是否已经初始化
      if (editor.container) {
        // 保存当前内容
        const content = editor.getContent();
        
        // 销毁编辑器
        editor.destroy();
        
        // 清空容器
        if (editorContainer.value) {
          editorContainer.value.innerHTML = '';
        }
        
        // 在容器中创建新的script标签
        if (editorContainer.value) {
          const script = document.createElement('script');
          script.id = props.editorId;
          script.type = 'text/plain';
          script.style.height = '100%';
          editorContainer.value.appendChild(script);
        }
        
        // 返回保存的内容，以便后续恢复
        return content;
      }
    } catch (e) {
      console.error('销毁编辑器时出错', e);
    }
    editor = null;
  }
  return '';
}

// 初始化编辑器
const initEditor = (initialContent = '') => {
  // 防止重复初始化
  if (isEditorInitializing) {
    return;
  }
  
  isEditorInitializing = true;
  
  // 清空容器
  if (editorContainer.value) {
    editorContainer.value.innerHTML = '';
  }
  
  // 动态加载UEditorPlus
  loadScript('/static/UEditorPlus/dist-min/ueditor.config.js', () => {
    // 设置全局语言 - 中文
    window.UEDITOR_CONFIG = window.UEDITOR_CONFIG || {};
    window.UEDITOR_CONFIG.lang = 'zh-cn';
    
    // 应用小说写作专用配置
    window.UEDITOR_CONFIG.toolbars = [
      [
        'undo', 'redo', '|',
        'bold', 'italic', 'underline', 'strikethrough', '|',
        'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|',
        'insertorderedlist', 'insertunorderedlist', '|',
        'fontfamily', 'fontsize', 'forecolor', 'backcolor', '|',
        'lineheight', 'indent', '|',
        'blockquote', 'horizontal', '|',
        'searchreplace', '|',
        'fullscreen', 'source'
      ]
    ];
    
    // 中文字体配置
    window.UEDITOR_CONFIG.fontfamily = [
      { label: '宋体', name: 'SimSun', val: '宋体,SimSun'},
      { label: '仿宋', name: 'FangSong', val: '仿宋,FangSong'},
      { label: '楷体', name: 'KaiTi', val: '楷体,KaiTi'},
      { label: '黑体', name: 'SimHei', val: '黑体,SimHei'},
      { label: '微软雅黑', name: 'Microsoft YaHei', val: '微软雅黑,Microsoft YaHei'}
    ];
    
    // 自动排版配置
    window.UEDITOR_CONFIG.autoTypeset = {
      mergeEmptyline: true,
      removeClass: true,
      removeEmptyline: false,
      textAlign: "justify",
      imageBlockLine: "center",
      pasteFilter: true,
      clearFontSize: false,
      clearFontFamily: false,
      removeEmptyNode: false,
      indent: true,
      indentValue: "2em",
      bdc2sb: false,
      tobdc: false
    };
    
    loadScript('/static/UEditorPlus/dist-min/ueditor.all.js', () => {
      // 编辑器准备就绪后创建实例
      try {
        editor = window.UE.getEditor(props.editorId, editorConfig);

        // 监听内容变化
        editor.addListener('contentChange', () => {
          emit('update:modelValue', editor.getContent());
        });

        // 设置初始内容
        if (initialContent || props.modelValue) {
          editor.ready(() => {
            try {
              editor.setContent(initialContent || props.modelValue);
            } catch (e) {
              console.error('设置编辑器内容失败', e);
            }
          });
        }

        // 编辑器准备就绪
        editor.ready(() => {
          isEditorReady = true;
          isEditorInitializing = false;
          editorStore.setActiveEditorInstance(editor); // 注册编辑器实例
          emit('ready', editor);
        });
      } catch (e) {
        console.error('创建编辑器失败', e);
        isEditorInitializing = false;
        createFallbackTextarea();
      }
    });
  });
}

// 动态加载脚本
const loadScript = (src, callback) => {
  const script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = src;
  
  // 处理加载成功
  script.onload = () => {
    callback();
  };
  
  // 处理加载失败
  script.onerror = () => {
    console.error(`加载脚本失败: ${src}`);
    isEditorInitializing = false;
    createFallbackTextarea();
  };
  
  document.head.appendChild(script);
}

// 编辑器配置
const editorConfig = {
  // 禁用后端服务
  serverUrl: '',
  UEDITOR_HOME_URL: '/static/UEditorPlus/dist-min/',
  UEDITOR_CORS_URL: '/static/UEditorPlus/dist-min/',
  // 禁用语言文件加载
  lang: 'en',
  langIsLoad: true,
  // 编辑器不自动被内容撑高
  autoHeightEnabled: false,
  // 初始容器高度
  initialFrameHeight: 680,
  // 初始容器宽度
  initialFrameWidth: '100%',
  // 关闭自动保存
  autoSaveEnable: false,
  // 启用自定义上传服务
  uploadServiceEnable: true,
  // 自定义上传函数
  uploadServiceUpload: function(type, file, callback, option) {
    // 这里可以实现自定义上传逻辑
    // 模拟上传进度
    let progress = 0;
    const timer = setInterval(() => {
      progress += 10;
      callback.progress(progress);

      if (progress >= 100) {
        clearInterval(timer);
        // 模拟上传成功
        callback.success({
          "state": "SUCCESS",
          "url": URL.createObjectURL(file),
          "title": file.name,
          "original": file.name
        });
      }
    }, 200);
  },
  
  // 其他优化配置
  enableContextMenu: true,
  elementPathEnabled: false,
  catchRemoteImageEnable: false,
  allowDivTransToP: true,
  rgb2Hex: true,
  pasteplain: false,
  selectall: true,
  cleardoc: true,
  // 禁用选择文字时出现的快捷菜单
  shortcutMenu: []
}

// 监听modelValue变化
watch(() => props.modelValue, (newValue) => {
  if (editor && editor.getContent && isEditorReady) {
    try {
      const currentContent = editor.getContent();
      if (currentContent !== newValue) {
        editor.setContent(newValue);
      }
    } catch (e) {
      console.error('设置编辑器内容失败', e);
    }
  }
})

// 组件挂载时初始化编辑器
onMounted(() => {
  initEditor(props.modelValue || '');
});

// 组件卸载时销毁编辑器
onBeforeUnmount(() => {
  // 如果当前编辑器是激活的实例，则清除它
  if (editorStore.activeEditorInstance === editor) {
    editorStore.clearActiveEditorInstance();
  }
  destroyEditor();
});

// 监听editorId变化，重新初始化编辑器
watch(() => props.editorId, (newId, oldId) => {
  // 只有当ID真正改变时才重新初始化
  if (newId !== oldId) {
    // 销毁旧编辑器
    destroyEditor();
    
    // 重新初始化编辑器
    nextTick(() => {
      initEditor(props.modelValue || '');
    });
  }
})

// 创建后备文本区域
const createFallbackTextarea = () => {
  try {
    const textarea = document.createElement('textarea');
    textarea.value = props.modelValue || '';
    textarea.style.width = '100%';
    textarea.style.height = '100%';
    textarea.style.border = '1px solid #ddd';
    textarea.style.outline = 'none';
    textarea.style.padding = '10px';
    textarea.style.resize = 'none';
    textarea.style.fontFamily = 'Arial, sans-serif';
    textarea.style.fontSize = '14px';
    
    // 监听内容变化
    textarea.addEventListener('input', () => {
      emit('update:modelValue', textarea.value);
    });
    
    // 添加到容器
    if (editorContainer.value) {
      editorContainer.value.appendChild(textarea);
    }
    
    // 触发ready事件
    emit('ready', { 
      type: 'fallback', 
      element: textarea,
      setContent: (content) => { textarea.value = content; },
      getContent: () => { return textarea.value; }
    });
  } catch (e) {
    console.error('创建后备文本区域失败', e);
  }
}
</script>

<style scoped>
.ueditor-plus-container {
  width: 100%;
  height: 100%;
}
</style>
