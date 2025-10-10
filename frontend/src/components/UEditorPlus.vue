<template>
  <div class="ueditor-plus-container">
    <vue-ueditor-wrap
      v-model="content"
      :editor-id="editorId"
      :config="editorConfig"
      :editorDependencies="['dist-min/ueditor.config.js','dist-min/ueditor.all.js']"
      style="height:100%;"
      @ready="onEditorReady"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

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

// 内容
const content = ref(props.modelValue)

// 编辑器配置
const editorConfig = ref({
  // 后端服务地址
  serverUrl: '/api/ueditor',
  UEDITOR_HOME_URL: '/static/UEditorPlus/dist-min/',
  UEDITOR_CORS_URL: '/static/UEditorPlus/dist-min/',
  // 编辑器不自动被内容撑高
  autoHeightEnabled: false,
  // 初始容器高度
  initialFrameHeight: 400,
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
  // 工具栏配置
  toolbars: [
    [
      'fullscreen', 'source', '|', 'undo', 'redo', '|',
      'bold', 'italic', 'underline', 'fontborder', 'strikethrough', 'superscript', 'subscript', 'removeformat', 'formatmatch', 'autotypeset', 'blockquote', 'pasteplain', '|',
      'forecolor', 'backcolor', 'insertorderedlist', 'insertunorderedlist', 'selectall', 'cleardoc', '|',
      'rowspacingtop', 'rowspacingbottom', 'lineheight', '|',
      'customstyle', 'paragraph', 'fontfamily', 'fontsize', '|',
      'directionalityltr', 'directionalityrtl', 'indent', '|',
      'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|',
      'touppercase', 'tolowercase', '|',
      'link', 'unlink', 'anchor', '|',
      'imagenone', 'imageleft', 'imageright', 'imagecenter', '|',
      'simpleupload', 'insertimage', 'emotion', 'scrawl', 'insertvideo', 'attachment', '|',
      'inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols', '|',
      'print', 'preview', 'searchreplace', 'help'
    ]
  ]
})

// 监听modelValue变化
watch(() => props.modelValue, (newValue) => {
  content.value = newValue;
})

// 监听content变化
watch(content, (newValue) => {
  emit('update:modelValue', newValue);
})

// 编辑器准备就绪
const onEditorReady = (editor) => {
  emit('ready', editor);
}
</script>

<style scoped>
.ueditor-plus-container {
  height: 100%;
  width: 100%;
}
</style>
