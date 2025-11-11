<template>
  <div class="settings-container">
    <h2>项目设置</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane name="basic">
        <template #label>
          <el-icon><InfoFilled /></el-icon>
          基本信息
        </template>
        <el-form :model="projectInfo" label-width="120px" class="settings-form">
          <el-form-item label="项目名称">
            <el-input v-model="projectInfo.title" />
          </el-form-item>
          <el-form-item label="项目类型">
            <el-select v-model="projectInfo.genre" placeholder="请选择项目类型">
              <el-option label="奇幻" value="fantasy" />
              <el-option label="科幻" value="scifi" />
              <el-option label="悬疑" value="mystery" />
              <el-option label="言情" value="romance" />
              <el-option label="历史" value="history" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="项目简介">
            <el-input
              v-model="projectInfo.description"
              type="textarea"
              :rows="4"
              placeholder="请输入项目简介"
            />
          </el-form-item>
          <el-form-item label="作者">
            <el-input v-model="projectInfo.author" />
          </el-form-item>
          <el-form-item label="预计字数">
            <el-input-number v-model="projectInfo.expectedWords" :min="1000" :step="10000" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveProjectInfo">保存基本信息</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane name="ai">
        <template #label>
          <el-icon><Cpu /></el-icon>
          AI设置
        </template>
        <el-form :model="aiSettings" label-width="120px" class="settings-form">
          <el-form-item label="API地址">
            <el-input v-model="aiSettings.apiUrl" placeholder="请输入AI API地址" />
          </el-form-item>
          <el-form-item label="API密钥">
            <el-input v-model="aiSettings.apiKey" type="password" placeholder="请输入API密钥" />
          </el-form-item>
          <el-form-item label="模型">
            <el-select v-model="aiSettings.model" placeholder="请选择AI模型">
              <el-option label="GPT-3.5" value="gpt-3.5-turbo" />
              <el-option label="GPT-4" value="gpt-4" />
              <el-option label="Claude" value="claude" />
              <el-option label="其他模型" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="温度">
            <el-slider v-model="aiSettings.temperature" :min="0" :max="1" :step="0.1" show-input />
          </el-form-item>
          <el-form-item label="最大令牌数">
            <el-input-number v-model="aiSettings.maxTokens" :min="100" :max="4000" :step="100" />
          </el-form-item>
          <el-form-item label="系统提示词">
            <el-input
              v-model="aiSettings.systemPrompt"
              type="textarea"
              :rows="6"
              placeholder="请输入系统提示词，用于设定AI的角色和行为"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="testAIConnection">测试连接</el-button>
            <el-button type="success" @click="saveAISettings">保存AI设置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane name="editor">
        <template #label>
          <el-icon><EditPen /></el-icon>
          编辑器设置
        </template>
        <el-form :model="editorSettings" label-width="120px" class="settings-form">
          <el-form-item label="字体大小">
            <el-input-number v-model="editorSettings.fontSize" :min="12" :max="24" />
          </el-form-item>
          <el-form-item label="字体">
            <el-select v-model="editorSettings.fontFamily" placeholder="请选择字体">
              <el-option label="微软雅黑" value="Microsoft YaHei" />
              <el-option label="宋体" value="SimSun" />
              <el-option label="黑体" value="SimHei" />
              <el-option label="楷体" value="KaiTi" />
            </el-select>
          </el-form-item>
          <el-form-item label="行间距">
            <el-input-number v-model="editorSettings.lineHeight" :min="1" :max="3" :step="0.1" />
          </el-form-item>
          <el-form-item label="自动保存">
            <el-switch v-model="editorSettings.autoSave" />
          </el-form-item>
          <el-form-item label="自动保存间隔(秒)" v-if="editorSettings.autoSave">
            <el-input-number v-model="editorSettings.autoSaveInterval" :min="10" :max="300" />
          </el-form-item>
          <el-form-item label="显示字数统计">
            <el-switch v-model="editorSettings.showWordCount" />
          </el-form-item>
          <el-form-item label="显示章节导航">
            <el-switch v-model="editorSettings.showChapterNav" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveEditorSettings">保存编辑器设置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane name="export">
        <template #label>
          <el-icon><Download /></el-icon>
          导出设置
        </template>
        <el-form :model="exportSettings" label-width="120px" class="settings-form">
          <el-form-item label="默认导出格式">
            <el-radio-group v-model="exportSettings.defaultFormat">
              <el-radio label="docx">Word文档(.docx)</el-radio>
              <el-radio label="pdf">PDF文档(.pdf)</el-radio>
              <el-radio label="txt">纯文本(.txt)</el-radio>
              <el-radio label="md">Markdown(.md)</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="包含章节标题">
            <el-switch v-model="exportSettings.includeChapterTitles" />
          </el-form-item>
          <el-form-item label="包含角色列表">
            <el-switch v-model="exportSettings.includeCharacterList" />
          </el-form-item>
          <el-form-item label="包含世界观设定">
            <el-switch v-model="exportSettings.includeWorldSettings" />
          </el-form-item>
          <el-form-item label="页眉设置">
            <el-input v-model="exportSettings.header" placeholder="请输入页眉内容" />
          </el-form-item>
          <el-form-item label="页脚设置">
            <el-input v-model="exportSettings.footer" placeholder="请输入页脚内容" />
          </el-form-item>
          <el-form-item label="PDF页面大小" v-if="exportSettings.defaultFormat === 'pdf'">
            <el-select v-model="exportSettings.pdfPageSize">
              <el-option label="A4" value="A4" />
              <el-option label="A5" value="A5" />
              <el-option label="Letter" value="Letter" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveExportSettings">保存导出设置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane name="system">
        <template #label>
          <el-icon><Setting /></el-icon>
          系统设置
        </template>
        <el-form :model="systemSettings" label-width="120px" class="settings-form">
          <el-form-item label="HTTP代理">
            <el-input
              v-model="systemSettings.proxyUrl"
              placeholder="例如: http://127.0.0.1:7890"
            >
              <template #prepend>
                <el-select v-model="systemSettings.proxyProtocol" style="width: 100px">
                  <el-option label="http://" value="http://" />
                  <el-option label="https://" value="https://" />
                  <el-option label="socks5://" value="socks5://" />
                </el-select>
              </template>
            </el-input>
            <div class="form-item-help">
              设置后，所有对外部AI服务的请求将通过此代理进行。留空则不使用代理。
            </div>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveSystemSettings">保存系统设置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Cpu, EditPen, Download, Setting } from '@element-plus/icons-vue'
import { useSystemStore } from '@/stores/systemStore'

const systemStore = useSystemStore();

// 当前选中的标签页
const activeTab = ref('basic')

// 项目基本信息
const projectInfo = reactive({
  title: '未命名项目',
  genre: 'fantasy',
  description: '',
  author: '',
  expectedWords: 100000
})

// AI设置
const aiSettings = reactive({
  apiUrl: 'https://api.openai.com/v1',
  apiKey: '',
  model: 'gpt-3.5-turbo',
  temperature: 0.7,
  maxTokens: 1000,
  systemPrompt: '你是一个专业的小说写作助手，擅长创作引人入胜的故事情节和生动的人物形象。'
})

// 编辑器设置
const editorSettings = reactive({
  fontSize: 16,
  fontFamily: 'Microsoft YaHei',
  lineHeight: 1.6,
  autoSave: true,
  autoSaveInterval: 30,
  showWordCount: true,
  showChapterNav: true
})

// 导出设置
const exportSettings = reactive({
  defaultFormat: 'docx',
  includeChapterTitles: true,
  includeCharacterList: false,
  includeWorldSettings: false,
  header: '',
  footer: '',
  pdfPageSize: 'A4'
})

// 系统设置
const systemSettings = reactive({
  proxyProtocol: 'http://',
  proxyUrl: ''
})

onMounted(() => {
  // 从 store 加载设置
  const fullProxyUrl = systemStore.settings.proxyUrl || '';
  if (fullProxyUrl) {
    // 拆分协议和地址
    const protocolMatch = fullProxyUrl.match(/^(https?:\/\/|socks5:\/\/)/);
    if (protocolMatch) {
      systemSettings.proxyProtocol = protocolMatch[1];
      systemSettings.proxyUrl = fullProxyUrl.substring(protocolMatch[1].length);
    } else {
      systemSettings.proxyUrl = fullProxyUrl;
    }
  }
});


// 保存项目基本信息
const saveProjectInfo = () => {
  // 在实际应用中，这里会保存到后端
  ElMessage.success('项目基本信息已保存')
}

// 测试AI连接
const testAIConnection = () => {
  if (!aiSettings.apiUrl || !aiSettings.apiKey) {
    ElMessage.warning('请先填写API地址和密钥')
    return
  }

  // 在实际应用中，这里会调用API测试连接
  ElMessage.loading('正在测试连接...')

  setTimeout(() => {
    ElMessage.success('AI连接测试成功')
  }, 1500)
}

// 保存AI设置
const saveAISettings = () => {
  // 在实际应用中，这里会保存到后端
  ElMessage.success('AI设置已保存')
}

// 保存编辑器设置
const saveEditorSettings = () => {
  // 在实际应用中，这里会保存到后端或本地存储
  ElMessage.success('编辑器设置已保存')
}

// 保存导出设置
const saveExportSettings = () => {
  // 在实际应用中，这里会保存到后端或本地存储
  ElMessage.success('导出设置已保存')
}

// 保存系统设置
const saveSystemSettings = () => {
  // 组合协议和地址
  const fullProxyUrl = systemSettings.proxyUrl
    ? systemSettings.proxyProtocol + systemSettings.proxyUrl
    : '';
  
  systemStore.updateSettings({
    proxyUrl: fullProxyUrl
  });
  ElMessage.success('系统设置已保存');
}
</script>

<style scoped>
.form-item-help {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  margin-top: 4px;
}

.settings-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.settings-container h2 {
  margin-bottom: 20px;
  color: #303133;
  font-weight: 600;
}

.settings-form {
  max-width: 800px;
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

/* 标签页样式优化 */
:deep(.el-tabs__header) {
  margin-bottom: 25px;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 10px;
  }
  
  .settings-form {
    padding: 15px;
  }
}
</style>
