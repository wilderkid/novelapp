<template>
  <el-aside width="350px" class="creative-assistant-sidebar" v-if="creativeAssistantVisible">
    <div class="assistant-container">
      <div class="assistant-header">
        <h3>创作助手</h3>
        <el-button type="text" @click="toggleCollapse">
          <el-icon><Right /></el-icon>
        </el-button>
      </div>
      <div class="assistant-content">
        <div class="chat-history">
          <div v-for="(message, index) in messages" :key="index" class="message" :class="message.role">
            <p v-html="formatMessage(message.content)"></p>
          </div>
        </div>
        <div class="chat-input">
          <div class="input-controls">
            <!-- 提示词选择器 -->
            <div class="control-item">
              <el-dropdown trigger="click" @command="selectPromptTemplate">
                <el-button :icon="ChatDotRound" circle />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="">无提示词</el-dropdown-item>
                    <el-dropdown-item 
                      v-for="item in promptTemplates" 
                      :key="item.id" 
                      :command="item.id"
                      :class="{ 'is-active': selectedPromptTemplateId === item.id }">
                      {{ item.name }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <span class="control-label" v-if="selectedPromptTemplateId">
                {{ getPromptTemplateName(selectedPromptTemplateId) }}
              </span>
            </div>

            <!-- AI模型选择器 -->
            <div class="control-item">
              <el-dropdown trigger="click" @command="selectAiModel">
                <el-button :icon="Setting" circle />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="">默认模型</el-dropdown-item>
                    <el-dropdown-item 
                      v-for="item in aiModels" 
                      :key="item.id" 
                      :command="item.id"
                      :class="{ 'is-active': selectedAiModelId === item.id }">
                      {{ item.name }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <span class="control-label" v-if="selectedAiModelId">
                {{ getAiModelName(selectedAiModelId) }}
              </span>
            </div>
          </div>
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="4"
            placeholder="请输入提示词..."
            @keydown.enter.prevent="sendMessage"
          />
          <div class="input-actions">
            <el-button type="primary" @click="sendMessage" :loading="isLoading">发送</el-button>
            <el-button 
              @click="insertIntoEditor" 
              :disabled="!activeEditorInstance || !lastAiResponse"
              title="将最后一条AI回复插入编辑器">
              写入编辑器
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </el-aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useEditorStore } from '../stores/editorStore';
import { useProjectStore } from '../stores/projectStore'; // 引入项目Store
import { ElMessage } from 'element-plus';
import axios from 'axios';
import { Right, ChatDotRound, Setting } from '@element-plus/icons-vue';
import MarkdownIt from 'markdown-it';

const editorStore = useEditorStore();
const projectStore = useProjectStore(); // 获取项目Store实例
const userInput = ref('');
const messages = ref([]);
const isLoading = ref(false);

const promptTemplates = ref([]);
const aiModels = ref([]);
const selectedPromptTemplateId = ref(null);
const selectedAiModelId = ref(null);

const activeEditorInstance = computed(() => editorStore.activeEditorInstance);
const creativeAssistantVisible = computed(() => editorStore.creativeAssistantVisible);
const currentProject = computed(() => projectStore.currentProject);

const lastAiResponse = computed(() => {
  const aiMessages = messages.value.filter(m => m.role === 'assistant');
  return aiMessages.length > 0 ? aiMessages[aiMessages.length - 1].content : null;
});

const md = new MarkdownIt();

const formatMessage = (content) => {
  return md.render(content);
};

const toggleCollapse = () => {
  editorStore.toggleCreativeAssistant();
};

const fetchPromptTemplates = async () => {
  try {
    const response = await axios.get(`http://localhost:9009/api/prompt-templates`);
    promptTemplates.value = response.data;
  } catch (error) {
    console.error('Failed to fetch prompt templates:', error);
    ElMessage.error('加载提示模板失败');
  }
};

const fetchAiModels = async () => {
  try {
    const response = await axios.get(`http://localhost:9009/api/ai-models`);
    aiModels.value = response.data;
  } catch (error) {
    console.error('Failed to fetch AI models:', error);
    ElMessage.error('加载AI模型失败');
  }
};

onMounted(() => {
  fetchPromptTemplates();
  fetchAiModels();
});

const selectPromptTemplate = (templateId) => {
  selectedPromptTemplateId.value = templateId;
};

const selectAiModel = (modelId) => {
  selectedAiModelId.value = modelId;
};

const getPromptTemplateName = (templateId) => {
  const template = promptTemplates.value.find(t => t.id === templateId);
  return template ? template.name : '';
};

const getAiModelName = (modelId) => {
  const model = aiModels.value.find(m => m.id === modelId);
  return model ? model.name : '';
};

const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  const currentInput = userInput.value;
  const history = messages.value.slice();

  // 检查是否需要项目上下文
  const selectedTemplate = promptTemplates.value.find(t => t.id === selectedPromptTemplateId.value);
  const templateContent = selectedTemplate ? selectedTemplate.content : '';
  const fullContentToCheck = currentInput + templateContent; // 检查用户输入和模板内容

  if (fullContentToCheck.includes('{{') && !currentProject.value) {
    ElMessage.warning('您似乎使用了变量，请先在“小说管理”中选择一个项目以正确渲染它们。');
    return;
  }

  if (isLoading.value) return;

  messages.value.push({ role: 'user', content: currentInput });
  userInput.value = '';
  isLoading.value = true;

  let processedUserInput = currentInput;

  // 如果用户输入包含变量且有项目上下文，则先进行渲染
  if (currentInput.includes('{{') && currentProject.value) {
    try {
      const renderPayload = {
        content: currentInput,
        project_id: currentProject.value.id,
      };
      const response = await axios.post('http://localhost:9009/api/prompts/render', renderPayload);
      processedUserInput = response.data.rendered_content;
      console.log('[CreativeAssistant DEBUG] User input rendered to:', processedUserInput);
    } catch (error) {
      console.error('Failed to render user input:', error);
      ElMessage.error('渲染用户输入中的变量失败。');
      messages.value.pop(); // 移除已添加的用户消息
      userInput.value = currentInput; // 恢复用户输入
      isLoading.value = false;
      return;
    }
  }

  try {
    const payload = {
      message: processedUserInput, // 使用渲染后的用户输入
      history: history,
      prompt_template_id: selectedPromptTemplateId.value,
      ai_model_id: selectedAiModelId.value,
      project_id: currentProject.value ? currentProject.value.id : null // 附加项目ID
    };

    console.log('[CreativeAssistant DEBUG] Sending payload:', payload);

    const response = await axios.post('http://localhost:9009/api/chat', payload);
    
    const aiMessage = { role: 'assistant', content: response.data.reply };
    messages.value.push(aiMessage);

  } catch (error) {
    console.error('AI请求失败:', error);
    ElMessage.error('AI响应出错了，请稍后再试。');
    messages.value.pop();
    userInput.value = currentInput;
  } finally {
    isLoading.value = false;
  }
};

const insertIntoEditor = () => {
  if (!lastAiResponse.value) {
    ElMessage.warning('没有可供写入的AI内容');
    return;
  }
  const result = editorStore.insertContent(lastAiResponse.value);
  if (result.success) {
    ElMessage.success('内容已成功写入编辑器');
  } else {
    ElMessage.error(result.message);
  }
};

</script>

<style scoped>
/* 样式保持不变 */
.creative-assistant-sidebar {
  background-color: #f9fafb;
  border-left: 1px solid #e4e7ed;
  transition: width 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.assistant-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.assistant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.assistant-header h3 {
  margin: 0;
  font-size: 16px;
}

.assistant-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: 15px;
  overflow: hidden;
}

.chat-history {
  flex-grow: 1;
  overflow-y: auto;
  margin-bottom: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  background-color: #fff;
}

.message p {
    margin: 0;
}

.chat-input {
  display: flex;
  flex-direction: column;
}

.input-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-label {
  font-size: 12px;
  color: #606266;
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.el-dropdown-menu__item.is-active {
  color: #409eff;
  font-weight: bold;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}
</style>
