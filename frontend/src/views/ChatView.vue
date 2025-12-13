<template>
  <div class="chat-view-layout">
    <!-- 对话历史侧边栏 -->
    <div class="history-sidebar">
      <div class="new-chat-button">
        <el-button type="primary" @click="startNewChat" plain>+ 新建对话</el-button>
        <div class="button-row">
          <el-button
            v-if="!isSelectionMode"
            type="warning"
            @click="enterSelectionMode"
            plain
            :disabled="conversations.length === 0">
            批量管理
          </el-button>
          <template v-else>
            <el-button type="danger" @click="deleteSelectedConversations" plain :disabled="selectedConversations.length === 0">
              删除选中 ({{ selectedConversations.length }})
            </el-button>
            <el-button @click="exitSelectionMode" plain>取消</el-button>
          </template>
        </div>
      </div>
      <el-menu class="history-menu" @select="loadChat">
        <el-menu-item v-for="conv in conversations" :key="conv.id" :index="String(conv.id)">
          <template #title>
            <div class="conv-item-content">
              <el-checkbox
                v-if="isSelectionMode"
                v-model="selectedConversations"
                :value="conv.id"
                @click.stop
                style="margin-right: 8px;"
              />
              <el-icon v-else style="margin-right: 8px;"><ChatDotRound /></el-icon>
              <span class="conv-title">{{ conv.title }}</span>
              <div class="conv-actions" v-if="!isSelectionMode">
                <el-button
                  :icon="Edit"
                  circle
                  size="small"
                  @click.stop="renameConversation(conv)"
                ></el-button>
                <el-button
                  :icon="Delete"
                  circle
                  size="small"
                  type="danger"
                  @click.stop="deleteConversation(conv.id)"
                ></el-button>
              </div>
            </div>
          </template>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 聊天主窗口 -->
    <div class="chat-container">
      <div class="chat-header">
        <div class="chat-header-left">
          <!-- AI模型选择器 -->
          <el-dropdown trigger="click" :visible="showAiModelMenu" @update:visible="showAiModelMenu = $event" @command="selectAiModel">
            <h1 class="model-title-dropdown" :class="{ 'is-model-selected': selectedAiModelId }">
              {{ getAiModelName(selectedAiModelId) || '默认模型' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </h1>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="">默认模型</el-dropdown-item>
                <div v-for="(models, providerName) in groupedAiModels" :key="providerName" class="provider-group">
                  <div class="provider-group-title">{{ providerName }}</div>
                  <el-dropdown-item
                    v-for="model in models"
                    :key="model.id"
                    :command="model.id"
                    :class="{ 'is-active': selectedAiModelId === model.id }">
                    {{ model.name }}
                  </el-dropdown-item>
                </div>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <el-button
          type="danger"
          size="small"
          plain
          @click="clearConversation"
          :disabled="!currentConversationId"
        >
          <el-icon><Delete /></el-icon>
          清除对话
        </el-button>
      </div>
      <div class="chat-messages" ref="messagesContainer">
        <transition-group name="message" tag="div">
          <div v-for="(msg, index) in messages" :key="index" class="message-wrapper" :class="`message-wrapper-${msg.role}`">
            <div class="message-content-wrapper">
              <!-- 添加头像 -->
              <div class="avatar" :class="`avatar-${msg.role}`">
                <el-icon v-if="msg.role === 'assistant'" :size="24">
                  <ChatLineRound />
                </el-icon>
                <el-icon v-else :size="24">
                  <User />
                </el-icon>
              </div>
              <div class="message" :class="`message-${msg.role}`">
                <!-- 思考过程 -->
                <div v-if="msg.role === 'assistant' && msg.hadThinkingProcess"
                     class="thinking-process-container">
                  <div class="thinking-process-header"
                       @click="msg.showThinkingProcess = !msg.showThinkingProcess">
                    <div class="thinking-process-title">
                      <el-icon><Files /></el-icon>
                      <span>思考过程</span>
                    </div>
                    <el-button
                      v-if="!msg.isThinking"
                      type="primary"
                      link
                      size="small"
                      class="collapse-button"
                    >
                      {{ msg.showThinkingProcess ? '收起' : '展开' }}
                      <el-icon class="el-icon--right">
                        <ArrowUp v-if="msg.showThinkingProcess" />
                        <ArrowDown v-else />
                      </el-icon>
                    </el-button>
                  </div>
                  <el-collapse-transition>
                    <div v-show="msg.showThinkingProcess">
                      <div class="thinking-process-content markdown-body"
                           :class="{ 'is-thinking': msg.isThinking }"
                           v-html="renderMarkdown(msg.thinkingContent)">
                      </div>
                    </div>
                  </el-collapse-transition>
                </div>

                <!-- 最终回复 (Assistant) / 加载中 -->
                <div v-if="msg.role === 'assistant'">
                  <div v-if="msg.content" v-html="renderMarkdown(msg.content)" class="markdown-body final-answer"></div>
                  <!-- 加载中提示 -->
                  <div v-if="msg.isThinking && !msg.hadThinkingProcess" class="loading-indicator markdown-body">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>AI正在思考...</span>
                  </div>
                </div>

                <!-- 用户消息 -->
                <span v-else-if="msg.role === 'user'">{{ msg.content }}</span>
              </div>
            </div>
            <!-- 将 message-actions 移到 .message 外部，作为其兄弟元素 -->
            <div v-if="(msg.role === 'assistant' || msg.role === 'user') && !isLoading" class="message-actions">
              <el-button v-if="msg.role === 'assistant'" size="small" circle :icon="CopyDocument" @click="copyMessage(msg.content)" title="复制消息"></el-button>
              <el-button v-if="msg.role === 'assistant'" size="small" circle :icon="Refresh" @click="regenerateResponse(index)" title="重新生成"></el-button>
              <el-button size="small" circle :icon="Delete" @click="deleteMessage(index)" title="删除消息"></el-button>
            </div>
          </div>
        </transition-group>
      </div>
      <div class="chat-input-area">
        <div class="input-controls">
          <div class="control-buttons">
            <el-dropdown trigger="click" :visible="showPromptTemplateMenu" @update:visible="showPromptTemplateMenu = $event" @command="selectPromptTemplate">
              <el-button :icon="Tickets" circle size="small" />
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
            <el-button :icon="Setting" circle size="small" @click="showSettingsDialog = true" />
          </div>
          <div class="control-item">
            <span class="control-label" v-if="selectedPromptTemplateId">
              {{ getPromptTemplateName(selectedPromptTemplateId) }}
            </span>
          </div>
        </div>
        <div class="input-wrapper">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="2"
            :autosize="{ minRows: 2, maxRows: 8 }"
            placeholder="请输入你的问题... (Shift+Enter 换行)"
            @keydown.enter.prevent="handleEnter"
          ></el-input>
          <el-button
            type="primary"
            @click="sendMessageStream()"
            class="send-button-icon"
            :loading="isLoading"
            :icon="Promotion"
            circle
          />
        </div>
      </div>
    </div>

    <!-- AI参数设置对话框 -->
    <el-dialog v-model="showSettingsDialog" title="AI调用参数设置" width="400px">
      <el-form label-width="100px">
        <el-form-item label="温度">
          <el-input-number v-model="aiSettings.temperature" :min="0" :max="1" :step="0.1" :precision="1" />
          <div class="form-item-tip">控制输出的随机性，0-1之间</div>
        </el-form-item>
        <el-form-item label="最大Token">
          <el-input-number v-model="aiSettings.maxTokens" :min="100" :max="1000000" :step="100" />
          <div class="form-item-tip">限制AI回复的最大长度</div>
        </el-form-item>
        <el-form-item label="记忆轮数">
          <el-input-number v-model="aiSettings.memoryRounds" :min="1" :max="200" :step="1" />
          <div class="form-item-tip">保留最近N轮对话作为上下文</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSettingsDialog = false">取消</el-button>
        <el-button type="primary" @click="showSettingsDialog = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/default.css';
import { CopyDocument, Refresh, Edit, Delete, Tickets, Setting, ChatSquare, ChatLineRound, User, Loading, Files, ArrowDown, ArrowUp, Promotion } from '@element-plus/icons-vue';
import { useProjectStore } from '@/stores/projectStore';
import { useSystemStore } from '@/stores/systemStore';

const projectStore = useProjectStore();
const systemStore = useSystemStore();
const currentProject = computed(() => projectStore.currentProject);
const userInput = ref('');
const messages = ref([]);
const conversations = ref([]);
const currentConversationId = ref(null);
const isLoading = ref(false);
const messagesContainer = ref(null);
const promptTemplates = ref([]);
const selectedPromptTemplateId = ref(null);
const aiModels = ref([]);
const selectedAiModelId = ref(null);

// 批量选择状态
const isSelectionMode = ref(false);
const selectedConversations = ref([]);

// 下拉菜单状态
const showPromptTemplateMenu = ref(false);
const showAiModelMenu = ref(false);

// AI调用参数设置
const showSettingsDialog = ref(false);
const aiSettings = ref({
  temperature: systemStore.settings.chatDefaults?.temperature ?? 0.7,
  maxTokens: systemStore.settings.chatDefaults?.maxTokens ?? 2000,
  memoryRounds: systemStore.settings.chatDefaults?.memoryRounds ?? 10
});

// -- Computed Properties --
const groupedAiModels = computed(() => {
  if (!aiModels.value) return {};
  return aiModels.value.reduce((acc, model) => {
    const providerName = model.provider.name;
    if (!acc[providerName]) {
      acc[providerName] = [];
    }
    acc[providerName].push(model);
    return acc;
  }, {});
});

// -- Conversation Actions --
const deleteConversation = async (convId) => {
  ElMessageBox.confirm(
    '此操作将永久删除该对话及其所有消息，是否继续？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await axios.delete(`/api/conversations/${convId}`);
        ElMessage.success('对话删除成功');
        fetchConversations();
        if (currentConversationId.value === convId) {
          startNewChat();
        }
      } catch (error) {
        console.error('Failed to delete conversation:', error);
        ElMessage.error('删除对话失败');
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除');
    });
};

const renameConversation = async (conv) => {
  ElMessageBox.prompt('请输入新的对话标题', '重命名对话', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: conv.title,
    inputPattern: /^.{1,50}$/,
    inputErrorMessage: '标题不能为空且长度不能超过50个字符',
  })
    .then(async ({ value }) => {
      try {
        await axios.put(`/api/conversations/${conv.id}`, { title: value });
        ElMessage.success('对话重命名成功');
        fetchConversations();
      } catch (error) {
        console.error('Failed to rename conversation:', error);
        ElMessage.error('重命名对话失败');
      }
    })
    .catch(() => {
      ElMessage.info('已取消重命名');
    });
};

// 进入批量选择模式
const enterSelectionMode = () => {
  isSelectionMode.value = true;
  selectedConversations.value = [];
};

// 退出批量选择模式
const exitSelectionMode = () => {
  isSelectionMode.value = false;
  selectedConversations.value = [];
};

// 批量删除选中的对话
const deleteSelectedConversations = async () => {
  if (selectedConversations.value.length === 0) {
    ElMessage.warning('请先选择要删除的对话');
    return;
  }

  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedConversations.value.length} 条对话记录吗？此操作不可恢复！`,
    '批量删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        // 批量删除选中的对话
        await Promise.all(
          selectedConversations.value.map(convId =>
            axios.delete(`/api/conversations/${convId}`)
          )
        );
        ElMessage.success(`已删除 ${selectedConversations.value.length} 条对话`);
        
        // 如果当前对话被删除，则开始新对话
        if (selectedConversations.value.includes(currentConversationId.value)) {
          startNewChat();
        }
        
        fetchConversations();
        exitSelectionMode();
      } catch (error) {
        console.error('Failed to delete selected conversations:', error);
        ElMessage.error('批量删除失败');
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除');
    });
};

// -- Markdown & Highlight.js Setup --
const renderer = new marked.Renderer();
marked.setOptions({
  renderer,
  gfm: true,
  breaks: true,
  pedantic: false,
  highlight: (code, lang) => {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    return hljs.highlight(code, { language }).value;
  },
});

const renderMarkdown = (content) => {
  if (!content) return '';
  // No longer replacing <think> tags here, they are handled by separating content
  return marked.parse(content);
};

const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content);
    ElMessage.success('已复制到剪贴板');
  } catch (err) {
    ElMessage.error('复制失败');
  }
};

const regenerateResponse = async (aiMessageIndex) => {
  // 找到这条AI回复对应的用户问题
  const userMessageIndex = aiMessageIndex - 1;
  if (userMessageIndex < 0 || messages.value[userMessageIndex].role !== 'user') {
    ElMessage.error('找不到对应的用户提问');
    return;
  }
  const userMessageContent = messages.value[userMessageIndex].content;
  
  // 在原地更新AI回复而不是移除它
  messages.value[aiMessageIndex].content = '正在重新思考中...';
  
  // 复用sendMessageStream逻辑，但传入历史消息并指定要更新的消息索引
  await sendMessageStream(userMessageContent, aiMessageIndex);
};

// 删除指定消息
const deleteMessage = async (messageIndex) => {
  ElMessageBox.confirm(
    '确定要删除这条消息吗？此操作不可恢复！', 
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      // 如果是用户消息，同时删除后面紧跟着的AI回复
      const message = messages.value[messageIndex];
      if (message.role === 'user' && messageIndex + 1 < messages.value.length) {
        const nextMessage = messages.value[messageIndex + 1];
        if (nextMessage.role === 'assistant') {
          // 删除用户消息和AI回复
          messages.value.splice(messageIndex, 2);
          ElMessage.success('消息对已删除');
          return;
        }
      }
      
      // 只删除单条消息
      messages.value.splice(messageIndex, 1);
      ElMessage.success('消息已删除');
    } catch (error) {
      ElMessage.error('删除消息失败');
      console.error(error);
    }
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};


const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 处理提示词选择
const selectPromptTemplate = (templateId) => {
  selectedPromptTemplateId.value = templateId;
  showPromptTemplateMenu.value = false;
};

// 处理AI模型选择
const selectAiModel = (modelId) => {
  selectedAiModelId.value = modelId;
  showAiModelMenu.value = false;
};

// 获取提示词名称
const getPromptTemplateName = (templateId) => {
  const template = promptTemplates.value.find(t => t.id === templateId);
  return template ? template.name : '';
};

// 获取AI模型名称
const getAiModelName = (modelId) => {
  const model = aiModels.value.find(m => m.id === modelId);
  return model ? model.name : '';
};

const fetchConversations = async () => {
  try {
    const response = await axios.get(`/api/conversations`);
    conversations.value = response.data;
  } catch (error) {
    console.error('Failed to fetch conversations:', error);
    ElMessage.error('加载对话列表失败');
  }
};

const fetchPromptTemplates = async () => {
  try {
    const response = await axios.get(`/api/prompt-templates`);
    promptTemplates.value = response.data;
  } catch (error) {
    console.error('Failed to fetch prompt templates:', error);
    ElMessage.error('加载提示模板失败');
  }
};

const fetchAiModels = async () => {
  try {
    // Get all AI models in one call
    const response = await axios.get(`/api/ai-models`);
    // 后端已过滤，前端直接使用返回的数据
    aiModels.value = response.data;
  } catch (error) {
    console.error('Failed to fetch AI models:', error);
    ElMessage.error('加载AI模型失败');
  }
};

onMounted(() => {
  fetchConversations();
  fetchPromptTemplates();
  fetchAiModels();
  
  // 应用默认设置（如果存在）
  if (systemStore.settings.chatDefaults) {
    selectedAiModelId.value = systemStore.settings.chatDefaults.aiModelId ?? null;
    selectedPromptTemplateId.value = systemStore.settings.chatDefaults.promptTemplateId ?? null;
  }
  
  startNewChat();
});

const startNewChat = () => {
  currentConversationId.value = null;
  messages.value = [{ role: 'assistant', content: '你好！有什么可以帮助你的吗？' }];
  userInput.value = '';
  // 恢复默认设置而不是清空
  if (systemStore.settings.chatDefaults) {
    selectedPromptTemplateId.value = systemStore.settings.chatDefaults.promptTemplateId ?? null;
    selectedAiModelId.value = systemStore.settings.chatDefaults.aiModelId ?? null;
  } else {
    selectedPromptTemplateId.value = null;
    selectedAiModelId.value = null;
  }
};

// Function to clear the current conversation context (keeps the conversation ID but clears messages)
const clearConversation = () => {
  ElMessageBox.confirm(
    '确定要清除当前对话内容吗？这将清除所有消息记录，但会保留当前对话的上下文继续对话。', 
    '清除对话确认',
    {
      confirmButtonText: '确定清除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // Keep the conversation ID but clear the messages
    if (currentConversationId.value) {
      // Start with a fresh assistant message
      messages.value = [{ role: 'assistant', content: '好的，我已经清除了之前的对话记录。现在我们可以开始新的对话。' }];
      userInput.value = '';
      ElMessage.success('对话内容已清除');
    } else {
      // If no conversation exists, start a new one
      startNewChat();
    }
  }).catch(() => {
    // User cancelled
    ElMessage.info('已取消清除操作');
  });
};

const loadChat = async (convId) => {
  if (!convId) return;
  try {
    const response = await axios.get(`/api/conversations/${convId}/messages`);
    messages.value = response.data.map(m => {
      // 前端统一处理思考和最终内容
      const rawContent = m.content || '';
      const thinkRegex = /<think>(.*?)<\/think>/s;
      const match = rawContent.match(thinkRegex);
      
      let thinkingContent = '';
      let content = rawContent;
      let hadThinkingProcess = false;

      if (match) {
        hadThinkingProcess = true;
        thinkingContent = match[1];
        content = rawContent.replace(thinkRegex, '').trim();
      }

      return {
        role: m.role,
        content: content,
        thinkingContent: thinkingContent,
        rawContent: rawContent, // 保存原始消息
        isThinking: false,
        hadThinkingProcess: hadThinkingProcess,
        showThinkingProcess: false, // 历史消息默认折叠
      };
    });
    currentConversationId.value = Number(convId);
    scrollToBottom();
  } catch (error) {
    console.error('Failed to load chat messages:', error);
    ElMessage.error('加载对话内容失败');
  }
};

const sendMessage = async (messageContent = null) => {
  const content = messageContent || userInput.value;
  if (!content.trim()) {
    ElMessage.warning('消息不能为空');
    return;
  }
  if (isLoading.value) return;

  // 检查用户输入和提示词模板中是否包含变量，如果包含，则必须有项目上下文
  const selectedTemplate = promptTemplates.value.find(t => t.id === selectedPromptTemplateId.value);
  const templateContent = selectedTemplate ? selectedTemplate.content : '';
  const fullContentToCheck = content + templateContent; // 检查用户输入和模板内容

  if (fullContentToCheck.includes('{{') && !currentProject.value) {
    ElMessage.warning('您似乎使用了变量，请先在"小说管理"中选择一个项目以正确渲染它们。');
    return;
  }

  isLoading.value = true;

  // 如果是新消息（非重新生成），则添加到消息列表
  if (!messageContent) {
    messages.value.push({ role: 'user', content });
    userInput.value = '';
  }
  
  scrollToBottom();

  messages.value.push({ role: 'assistant', content: '正在思考中...' });
  scrollToBottom();

  let processedUserInput = content;

  // 如果用户输入包含变量且有项目上下文，则先进行渲染
  if (content.includes('{{') && currentProject.value) {
    try {
      const renderPayload = {
        content: content,
        project_id: currentProject.value.id,
      };
      const response = await axios.post('/api/prompts/render', renderPayload);
      processedUserInput = response.data.rendered_content;
    } catch (error) {
      console.error('Failed to render user input:', error);
      ElMessage.error('渲染用户输入中的变量失败。');
      messages.value.pop(); // 移除已添加的AI消息
      messages.value.pop(); // 移除已添加的用户消息
      userInput.value = content; // 恢复用户输入
      isLoading.value = false;
      return;
    }
  }

  try {
    // Build history excluding the current "正在思考中..." AI message
    const actualHistory = [...messages.value]; // Create a copy
    actualHistory.pop(); // Remove the last "正在思考中..." AI message
    actualHistory.pop(); // Remove the current user message that's being sent
    
    // 准备资源数据，用于替换提示词中的变量
    const resources = {};

    // 如果有选中的提示词模板，尝试解析其中的变量
    if (selectedPromptTemplateId.value) {
      // 这里可以添加逻辑来收集用户输入的变量值
      // 例如，可以弹出一个对话框让用户输入每个变量的值
      // 不再使用硬编码数据，让后端从数据库中获取
    }

    const payload = {
      message: processedUserInput, // 使用处理后的用户输入
      // AI对话功能不依赖project_id，移除此参数
      conversation_id: currentConversationId.value,
      history: actualHistory.map(m => ({ role: m.role, content: m.content })),
      prompt_template_id: selectedPromptTemplateId.value,
      ai_model_id: selectedAiModelId.value,
      resources: resources,
      project_id: currentProject.value ? currentProject.value.id : null // 添加项目ID
    };

    const response = await axios.post('/api/chat', payload);

    messages.value[messages.value.length - 1].content = response.data.reply;

    if (!currentConversationId.value) {
      currentConversationId.value = response.data.conversation_id;
      fetchConversations();
    }

  } catch (error) {
    console.error('AI request failed:', error);
    messages.value[messages.value.length - 1].content = '抱歉，与AI连接时出现错误。';
    ElMessage.error('AI响应失败');
    
    // If there's a validation error (400), show more specific error
    if (error.response && error.response.status === 400) {
      
      // Check if it's specifically a project ID error
      if (error.response.data.detail && error.response.data.detail.includes('Project ID')) {
        ElMessage.error('请先选择一个项目');
      }
    }
  }
  finally {
    isLoading.value = false;
    scrollToBottom();
  }
};

// 使用流式API发送消息
// 修改sendMessageStream函数以支持更新现有消息
const sendMessageStream = async (messageContent = null, updateMessageIndex = null) => {
  const content = messageContent || userInput.value;
  if (!content.trim()) {
    ElMessage.warning('消息不能为空');
    return;
  }
  if (isLoading.value) return;

  // 检查用户输入和提示词模板中是否包含变量，如果包含，则必须有项目上下文
  const selectedTemplate = promptTemplates.value.find(t => t.id === selectedPromptTemplateId.value);
  const templateContent = selectedTemplate ? selectedTemplate.content : '';
  const fullContentToCheck = content + templateContent; // 检查用户输入和模板内容

  if (fullContentToCheck.includes('{{') && !currentProject.value) {
    ElMessage.warning('您似乎使用了变量，请先在"小说管理"中选择一个项目以正确渲染它们。');
    return;
  }

  isLoading.value = true;

  // 如果是新消息（非重新生成），则添加到消息列表
  if (updateMessageIndex === null) {
    messages.value.push({ role: 'user', content });
    userInput.value = '';
  }

  scrollToBottom();

  let aiMessageIndex;
  // 如果是更新现有消息，则更新该消息内容；否则添加新消息
  if (updateMessageIndex !== null) {
    aiMessageIndex = updateMessageIndex;
    const msg = messages.value[aiMessageIndex];
    msg.content = '';
    msg.thinkingContent = '';
    msg.rawContent = '';
    msg.isThinking = true;
    msg.hadThinkingProcess = false;
    msg.showThinkingProcess = true;
  } else {
    messages.value.push({
      role: 'assistant',
      content: '',
      thinkingContent: '',
      rawContent: '',
      isThinking: true,
      hadThinkingProcess: false,
      showThinkingProcess: true, // 默认展开
    });
    aiMessageIndex = messages.value.length - 1;
  }
  scrollToBottom();

  let processedUserInput = content;

  // 如果用户输入包含变量且有项目上下文，则先进行渲染
  if (content.includes('{{') && currentProject.value) {
    try {
      const renderPayload = {
        content: content,
        project_id: currentProject.value.id,
      };
      const response = await axios.post('/api/prompts/render', renderPayload);
      processedUserInput = response.data.rendered_content;
    } catch (error) {
      console.error('Failed to render user input:', error);
      ElMessage.error('渲染用户输入中的变量失败。');
      messages.value.pop(); // 移除已添加的AI消息
      if (updateMessageIndex === null) {
        messages.value.pop(); // 移除已添加的用户消息
      }
      userInput.value = content; // 恢复用户输入
      isLoading.value = false;
      return;
    }
  }

  try {
    // Build history excluding the current "正在思考中..." AI message
    const actualHistory = [...messages.value]; // Create a copy
    actualHistory.pop(); // Remove the last "正在思考中..." AI message
    actualHistory.pop(); // Remove the current user message that's being sent

    // 准备资源数据，用于替换提示词中的变量
    const resources = {};

    // 如果有选中的提示词模板，尝试解析其中的变量
    if (selectedPromptTemplateId.value) {
      // 这里可以添加逻辑来收集用户输入的变量值
      // 例如，可以弹出一个对话框让用户输入每个变量的值
      // 不再使用硬编码数据，让后端从数据库中获取
    }

    // 限制历史消息轮数
    const limitedHistory = actualHistory.slice(-aiSettings.value.memoryRounds * 2);
    
    // 准备请求参数
    const payload = {
      message: processedUserInput,
      conversation_id: currentConversationId.value,
      history: limitedHistory.map(m => ({ role: m.role, content: m.content })),
      prompt_template_id: selectedPromptTemplateId.value,
      ai_model_id: selectedAiModelId.value,
      resources: resources,
      project_id: currentProject.value ? currentProject.value.id : null,
      temperature: aiSettings.value.temperature,
      max_tokens: aiSettings.value.maxTokens
    };

    // 使用fetch API进行流式请求
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 获取响应流
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const msg = messages.value[aiMessageIndex];

    // 处理流式数据
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const dataStr = line.substring(6);
            if (dataStr.trim() === '[DONE]') continue;
            
            const data = JSON.parse(dataStr);
            if (!msg) continue;

            if (data.type === 'conversation_id') {
              if (!currentConversationId.value) {
                currentConversationId.value = data.conversation_id;
                fetchConversations();
              }
              continue;
            }

            if (data.type === 'error') {
              msg.content = data.message;
              ElMessage.error('AI响应失败');
              continue;
            }
            
            if (data.type === 'done') continue;

            if (data.content) {
              if (msg.rawContent === undefined) msg.rawContent = '';
              msg.rawContent += data.content;

              const thinkRegex = /<think>(.*?)<\/think>/s;
              const match = msg.rawContent.match(thinkRegex);

              if (match) {
                msg.hadThinkingProcess = true;
                // Ensure it's expanded while thinking
                if (!msg.showThinkingProcess) {
                  msg.showThinkingProcess = true;
                }
                msg.thinkingContent = match[1];
                msg.content = msg.rawContent.replace(thinkRegex, '').trim();
              } else {
                msg.content = msg.rawContent;
              }
              scrollToBottom();
            }
          } catch (e) {
            // Ignore JSON parsing errors
          }
        }
      }
    }
    
    // 缓冲区逻辑已移除，无需处理

  } catch (error) {
    console.error('AI request failed:', error);
    if (messages.value[aiMessageIndex]) {
        messages.value[aiMessageIndex].content = '抱歉，与AI连接时出现错误。';
    }
    ElMessage.error('AI响应失败');
  } finally {
    if (messages.value[aiMessageIndex]) {
        const msg = messages.value[aiMessageIndex];
        msg.isThinking = false;
        if (msg.hadThinkingProcess) {
          msg.showThinkingProcess = false; // Auto-collapse on finish
        }
        // Clean up
    }
    isLoading.value = false;
    scrollToBottom();
  }
};

const handleEnter = (e) => {
  if (e.shiftKey) {
    return;
  }
  sendMessageStream();
};
</script>

<style>
/* Global styles for highlight.js code blocks */
.markdown-body pre {
  background-color: #f5f5f5;
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9em;
}

.markdown-body p {
  margin: 0 0 1rem 0;
}

.markdown-body ul, .markdown-body ol {
  padding-left: 2em;
}

.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}
</style>

<style scoped>
/* --- 动画 --- */
.message-enter-active {
  transition: all 0.4s ease-out;
}
.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* --- 主布局 --- */
.chat-view-layout {
  display: flex;
  height: calc(100vh - 60px); /* 假设顶部导航栏高度为60px */
  background-color: var(--bg-color-base);
}

/* --- 历史记录侧边栏 --- */
.history-sidebar {
  width: 280px;
  flex-shrink: 0;
  border-right: 1px solid var(--border-color);
  background-color: var(--bg-color-card);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.new-chat-button {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.new-chat-button > .el-button {
  width: 100%;
  font-weight: 500;
}
.button-row {
  display: flex;
  gap: 8px;
}
.button-row .el-button {
  flex: 1;
  font-weight: 500;
}

.history-menu {
  flex-grow: 1;
  overflow-y: auto;
  border-right: none;
}
.history-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 6px;
  transition: background-color 0.2s ease, color 0.2s ease;
}
.history-menu .el-menu-item:hover {
  background-color: var(--bg-color-hover);
}
.history-menu .el-menu-item.is-active {
  background-color: var(--primary-color-light);
  color: var(--primary-color);
  font-weight: 600;
}

.conv-item-content {
  display: flex;
  align-items: center;
  width: 100%;
  overflow: hidden;
}
.conv-title {
  flex-grow: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 10px;
}
.conv-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}
.history-menu .el-menu-item:hover .conv-actions {
  opacity: 1;
}

/* --- 聊天主容器 --- */
.chat-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color-base);
  overflow: hidden;
}

.chat-header {
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--bg-color-card);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}
.chat-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.model-title-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}
.model-title-dropdown .el-icon {
  margin-left: 8px;
  transition: transform 0.3s;
}
.model-title-dropdown:hover,
.model-title-dropdown.is-model-selected {
  color: var(--primary-color);
}
.chat-header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary);
}

/* --- 消息区域 --- */
.chat-messages {
  flex-grow: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 外层 wrapper，用于控制整体左右对齐和垂直排列 */
.message-wrapper {
  display: flex;
  margin-bottom: 24px;
  flex-direction: column; /* 核心：内容和按钮垂直堆叠 */
}
.message-wrapper-assistant {
  align-items: flex-start; /* AI消息（内容+按钮）整体左对齐 */
}
.message-wrapper-user {
  align-items: flex-end; /* 用户消息（内容+按钮）整体右对齐 */
}

/* 包裹头像和消息气泡的容器 */
.message-content-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-start; /* 垂直方向上，头像和气泡顶部对齐 */
  max-width: 80%; /* 限制最大宽度，防止内容过长 */
}
/* 用户消息的内容 wrapper，头像在右边 */
.message-wrapper-user .message-content-wrapper {
   flex-direction: row-reverse; /* 头像和气泡反向排列 */
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}
.avatar-user {
  background-color: var(--primary-color);
}
.avatar-assistant {
  background: linear-gradient(135deg, #67c23a, #4caf50);
}

.message .markdown-body, .message-user span {
  padding: 10px 16px;
  border-radius: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  word-break: break-word;
}
.message-user span {
  background: var(--primary-color);
  color: white;
  border-radius: 12px 4px 12px 12px;
}
.message-assistant .markdown-body {
  background-color: var(--bg-color-card);
  color: var(--text-color-primary);
  border-radius: 4px 12px 12px 12px;
}


.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  color: var(--text-color-secondary);
}

/* 消息操作按钮 */
.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px; /* 与消息气泡的间距 */
}

/* 根据角色调整 message-actions 的边距，使其与消息气泡对齐 */
.message-wrapper-assistant .message-actions {
  margin-left: 52px; /* avatar width (40px) + gap (12px) */
}

.message-wrapper-user .message-actions {
  margin-right: 52px; /* avatar width (40px) + gap (12px) */
}

/* --- 输入区域 --- */
.chat-input-area {
  padding: 16px 24px;
  background-color: var(--bg-color-card);
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.control-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.input-wrapper {
  position: relative;
}

.send-button-icon {
  position: absolute;
  right: 10px;
  bottom: 10px;
  background-color: var(--primary-color);
  color: white;
  z-index: 100;
  pointer-events: auto;
}
.prompt-selector-icon {
  position: absolute;
  left: 10px;
  bottom: 10px;
  z-index: 10;
}
.send-button-icon:hover {
  background-color: var(--primary-color-dark);
}

.input-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.control-label {
  font-size: 12px;
  color: var(--text-color-secondary);
  background-color: var(--bg-color-hover);
  padding: 2px 8px;
  border-radius: 12px;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
  border-color: var(--border-color);
  padding-right: 50px; /* 为发送按钮留出空间 */
  line-height: 1.6;
}
:deep(.el-textarea__inner:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color-light);
}

/* --- 响应式设计 --- */
@media (max-width: 768px) {
  .history-sidebar {
    position: absolute;
    left: -280px;
    z-index: 1000;
    height: 100%;
    box-shadow: 2px 0 12px rgba(0,0,0,0.1);
  }
  .chat-header {
    padding: 0 16px;
  }
  .chat-messages {
    padding: 16px;
  }
  .message-content-wrapper {
    max-width: 90%;
  }
  /* 在移动端，操作按钮可能会占用过多空间，可以选择隐藏或调整样式 */
  .message-actions {
    gap: 4px;
  }
}
</style>

<style scoped>
/* ... existing styles ... */

/* --- 思考过程样式 --- */
.thinking-process-container {
  background-color: #f7f8fa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}

.thinking-process-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background-color: #f0f2f5;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.thinking-process-header:hover {
  background-color: #e9ebee;
}

.thinking-process-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.collapse-button {
  font-size: 12px;
}

.thinking-process-content {
  padding: 12px;
  font-size: 0.9em;
  color: #909399; /* 浅灰色字体 */
  background-color: #fdfdfd;
  border-top: 1px dashed #e4e7ed;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  line-height: 1.7;
}

/* 由于内容是通过 v-html 渲染的，我们需要使用 :deep() 来确保样式能正确应用到内部的 markdown 元素 */
.thinking-process-content :deep(p),
.thinking-process-content :deep(ul),
.thinking-process-content :deep(ol),
.thinking-process-content :deep(code),
.thinking-process-content :deep(pre),
.thinking-process-content :deep(span) {
  color: #909399 !important;
}

.thinking-process-content :deep(pre) {
    background-color: #f0f2f5;
}

/* --- 下拉菜单分组标题样式 --- */
.provider-group-title {
  color: #909399;
  font-size: 12px;
  padding: 8px 20px 4px;
  font-weight: 600;
  pointer-events: none;
  user-select: none;
}

.provider-group:not(:first-child) .provider-group-title {
  margin-top: 8px;
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}

/* 选中项高亮样式 */
:deep(.el-dropdown-menu__item.is-active) {
  background-color: var(--primary-color-light);
  color: var(--primary-color);
  font-weight: 600;
}
</style>
