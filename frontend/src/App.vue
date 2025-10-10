
<template>
  <el-container class="app-container">
    <el-container>
      <el-aside width="200px" class="sidebar">
        <el-menu
          default-active="1"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="1">
            <el-icon><Reading /></el-icon>
            <span>小说管理</span>
          </el-menu-item>
          <el-menu-item index="2">
            <el-icon><Document /></el-icon>
            <span>章节管理</span>
          </el-menu-item>
          <el-menu-item index="3">
            <el-icon><User /></el-icon>
            <span>角色设定</span>
          </el-menu-item>
          <el-menu-item index="4">
            <el-icon><Location /></el-icon>
            <span>世界观</span>
          </el-menu-item>
          <el-menu-item index="5">
            <el-icon><Setting /></el-icon>
            <span>项目设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main-content">
        <router-view />
      </el-main>
      <el-aside width="300px" class="ai-assistant" v-if="showAIAssistant">
        <div class="assistant-header">
          <h3>AI助手</h3>
          <el-button type="text" @click="toggleAIAssistant">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <div class="assistant-content">
          <el-input
            v-model="aiPrompt"
            type="textarea"
            :rows="4"
            placeholder="输入提示词，使用{{变量名}}引用数据"
          />
          <div class="variable-tips">
            <el-tag type="info" size="small" v-for="(tip, index) in variableTips" :key="index">
              {{ tip }}
            </el-tag>
          </div>
          <el-button type="primary" class="send-btn" @click="sendToAI">
            发送
          </el-button>
          <div class="ai-result" v-if="aiResult">
            <h4>AI生成结果</h4>
            <div class="result-content">{{ aiResult }}</div>
            <div class="result-actions">
              <el-button type="primary" size="small" @click="acceptAIResult">
                采纳
              </el-button>
              <el-button size="small" @click="rejectAIResult">
                忽略
              </el-button>
            </div>
          </div>
        </div>
      </el-aside>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, User, Location, Setting, Close, MagicStick, Reading } from '@element-plus/icons-vue'

const router = useRouter()
const showAIAssistant = ref(false)
const aiPrompt = ref('')
const aiResult = ref('')

// 示例变量提示
const variableTips = ref([
  '{{project.title}}',
  '{{character.主角.details.personality}}',
  '{{world.霍格沃茨.description}}',
  '{{selection}}'
])

const toggleAIAssistant = () => {
  showAIAssistant.value = !showAIAssistant.value
}

const handleMenuSelect = (index) => {
  switch (index) {
    case '1':
      router.push('/novels')
      break
    case '2':
      router.push('/chapters')
      break
    case '3':
      router.push('/characters')
      break
    case '4':
      router.push('/world')
      break
    case '5':
      router.push('/settings')
      break
  }
}

const sendToAI = () => {
  if (!aiPrompt.value.trim()) {
    ElMessage.warning('请输入提示词')
    return
  }

  // 模拟AI响应
  setTimeout(() => {
    aiResult.value = '这是AI生成的内容示例，实际应用中会连接到真实的AI服务。'
  }, 1000)
}

const acceptAIResult = () => {
  // 在实际应用中，这里会将结果插入到编辑器中
  ElMessage.success('已采纳AI生成的内容')
  aiResult.value = ''
}

const rejectAIResult = () => {
  aiResult.value = ''
  ElMessage.info('已忽略AI生成的内容')
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #e6e6e6;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.ai-assistant {
  background-color: #f9f9f9;
  border-left: 1px solid #e6e6e6;
  padding: 15px;
  display: flex;
  flex-direction: column;
}

.assistant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.assistant-header h3 {
  margin: 0;
}

.variable-tips {
  margin: 10px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.send-btn {
  width: 100%;
  margin-bottom: 15px;
}

.ai-result {
  border-top: 1px solid #e6e6e6;
  padding-top: 15px;
}

.ai-result h4 {
  margin: 0 0 10px 0;
}

.result-content {
  background-color: white;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
  min-height: 100px;
  max-height: 200px;
  overflow-y: auto;
}

.result-actions {
  display: flex;
  gap: 10px;
}
</style>
