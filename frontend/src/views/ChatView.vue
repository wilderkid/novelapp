<template>
  <div class="chat-view-layout">
    <!-- 对话历史侧边栏 -->
    <div class="history-sidebar">
      <div class="new-chat-button">
        <el-button type="primary" @click="startNewChat" plain>+ 新建对话</el-button>
      </div>
      <el-menu class="history-menu" @select="loadChat">
        <el-menu-item v-for="conv in conversations" :key="conv.id" :index="String(conv.id)">
          <template #title>
            <div class="conv-item-content">
              <el-icon style="margin-right: 8px;"><ChatDotRound /></el-icon>
              <span class="conv-title">{{ conv.title }}</span>
              <div class="conv-actions">
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
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
          <h1>{{ currentConversationId ? '对话中' : '新对话' }}</h1>
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
      </div>
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(msg, index) in messages" :key="index" class="message-wrapper" :class="`message-wrapper-${msg.role}`">
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
            <div v-if="msg.role === 'assistant'" v-html="renderMarkdown(msg.content)" class="markdown-body"></div>
            <span v-else>{{ msg.content }}</span>
            <div v-if="(msg.role === 'assistant' || msg.role === 'user') && !isLoading" class="message-actions">
              <el-button v-if="msg.role === 'assistant'" size="small" circle :icon="CopyDocument" @click="copyMessage(msg.content)" title="复制消息"></el-button>
              <el-button v-if="msg.role === 'assistant'" size="small" circle :icon="Refresh" @click="regenerateResponse(index)" title="重新生成"></el-button>
              <el-button size="small" circle :icon="Delete" @click="deleteMessage(index)" title="删除消息"></el-button>
            </div>
          </div>
        </div>
      </div>
      <div class="chat-input-area">
        <div class="input-controls">
          <!-- 提示词选择器 -->
          <div class="control-item">
            <el-dropdown trigger="click" v-model:show="showPromptTemplateMenu" @command="selectPromptTemplate">
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
            <el-dropdown trigger="click" v-model:show="showAiModelMenu" @command="selectAiModel">
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
          :rows="3"
          :autosize="{ minRows: 3, maxRows: 8 }"
          placeholder="请输入你的问题... (Shift+Enter 换行)"
          @keydown.enter.prevent="handleEnter"
        ></el-input>
        <el-button type="primary" @click="sendMessage()" class="send-button" :loading="isLoading">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/default.css';
import { CopyDocument, Refresh, Edit, Delete, ChatDotRound, Setting, ChatSquare, ChatLineRound, User } from '@element-plus/icons-vue';
import { useProjectStore } from '@/stores/projectStore';

const projectStore = useProjectStore();
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

// 下拉菜单状态
const showPromptTemplateMenu = ref(false);
const showAiModelMenu = ref(false);

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
        await axios.delete(`http://localhost:9009/api/conversations/${convId}`);
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
        await axios.put(`http://localhost:9009/api/conversations/${conv.id}`, { title: value });
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
  // 当AI正在回复时，显示“正在思考中...”，不进行markdown渲染
  if (content === '正在思考中...') {
    return content;
  }
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
    const response = await axios.get(`http://localhost:9009/api/conversations`);
    conversations.value = response.data;
  } catch (error) {
    console.error('Failed to fetch conversations:', error);
    ElMessage.error('加载对话列表失败');
  }
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
    // Get all AI models in one call
    const response = await axios.get(`http://localhost:9009/api/ai-models`);
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
  startNewChat();
});

const startNewChat = () => {
  currentConversationId.value = null;
  messages.value = [{ role: 'assistant', content: '你好！有什么可以帮助你的吗？' }];
  userInput.value = '';
  selectedPromptTemplateId.value = null; // Clear selected prompt on new chat
  selectedAiModelId.value = null; // Clear selected AI model on new chat
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
    const response = await axios.get(`http://localhost:9009/api/conversations/${convId}/messages`);
    messages.value = response.data.map(m => ({ role: m.role, content: m.content }));
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
      const response = await axios.post('http://localhost:9009/api/prompts/render', renderPayload);
      processedUserInput = response.data.rendered_content;
      console.log('[ChatView DEBUG] User input rendered to:', processedUserInput);
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
    
    // 添加详细的调用日志
    console.log("=" * 80);
    console.log("【前端AI调用详细日志】");
    console.log("调用时间:", new Date());
    console.log("消息内容:", content);
    console.log("处理后的消息内容:", processedUserInput);
    console.log("对话ID:", currentConversationId.value);
    console.log("历史消息数量:", actualHistory.length);
    console.log("提示模板ID:", selectedPromptTemplateId.value);
    console.log("AI模型ID:", selectedAiModelId.value);

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

    console.log("请求载荷:", payload);
    console.log("=" * 80);

    const response = await axios.post('http://localhost:9009/api/chat', payload);

    // 添加响应日志
    console.log("=" * 80);
    console.log("【前端AI响应详细日志】");
    console.log("响应时间:", new Date());
    console.log("响应状态:", response.status);
    console.log("响应数据:", response.data);
    console.log("=" * 80);

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
      console.error('Validation Error:', error.response.data);
      
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
  if (!messageContent) {
    messages.value.push({ role: 'user', content });
    userInput.value = '';
  }

  scrollToBottom();

  // 如果是更新现有消息，则更新该消息内容；否则添加新消息
  if (updateMessageIndex !== null) {
    messages.value[updateMessageIndex].content = '正在重新思考中...';
  } else {
    messages.value.push({ role: 'assistant', content: '正在思考中...' });
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
      const response = await axios.post('http://localhost:9009/api/prompts/render', renderPayload);
      processedUserInput = response.data.rendered_content;
      console.log('[ChatView DEBUG] User input rendered to:', processedUserInput);
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

    // 准备请求参数
    const payload = {
      message: processedUserInput, // 使用处理后的用户输入
      conversation_id: currentConversationId.value,
      history: actualHistory.map(m => ({ role: m.role, content: m.content })),
      prompt_template_id: selectedPromptTemplateId.value,
      ai_model_id: selectedAiModelId.value,
      resources: resources,
      project_id: currentProject.value ? currentProject.value.id : null // 添加项目ID
    };

    // 使用fetch API进行流式请求
    const response = await fetch('http://localhost:9009/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 当前AI消息的索引
    const aiMessageIndex = messages.value.length - 1;
    let aiContent = '';

    // 获取响应流
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    // 处理流式数据
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      // 解码数据块
      const chunk = decoder.decode(value, { stream: true });

      // 处理SSE格式的数据
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));

            switch (data.type) {
              case 'conversation_id':
                if (!currentConversationId.value) {
                  currentConversationId.value = data.conversation_id;
                  fetchConversations();
                }
                break;

              case 'content':
                // 第一次接收到内容时，替换"正在思考中..."
                if (aiContent === '') {
                  messages.value[aiMessageIndex].content = data.content;
                } else {
                  // 追加内容
                  messages.value[aiMessageIndex].content += data.content;
                }
                aiContent += data.content;
                scrollToBottom();
                break;

              case 'error':
                messages.value[aiMessageIndex].content = data.message;
                ElMessage.error('AI响应失败');
                break;

              case 'done':
                // 流式响应结束
                break;
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e);
          }
        }
      }
    }

  } catch (error) {
    console.error('AI request failed:', error);
    messages.value[messages.value.length - 1].content = '抱歉，与AI连接时出现错误。';
    ElMessage.error('AI响应失败');
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
};

const handleEnter = (e) => {
  if (e.shiftKey) {
    return;
  }
  // 使用流式API发送消息
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
.chat-view-layout {
  display: flex;
  height: calc(100vh - 40px);
  background-color: #f5f7fa;
}

.history-sidebar {
  width: 260px;
  flex-shrink: 0;
  border-right: 1px solid #e0e0e0;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0,0,0,0.05);
}

.new-chat-button {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
}
.new-chat-button .el-button {
  width: 100%;
}

.history-menu {
  flex-grow: 1;
  overflow-y: auto;
  border-right: none;
  background-color: #fff;
}

.conv-item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.conv-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
  margin-right: 10px; /* Give some space before icons */
}

.conv-actions {
  display: flex;
  gap: 5px;
  opacity: 0; /* Hidden by default */
  transition: opacity 0.2s ease-in-out;
}

.history-menu .el-menu-item:hover .conv-actions {
  opacity: 1; /* Show on hover */
}

.history-menu .el-menu-item {
  border-radius: 6px;
  margin: 4px 8px;
}

.chat-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  margin: 12px 12px 12px 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.chat-header {
  padding: 1rem;
  background: linear-gradient(135deg, #409eff, #5a7eff);
  color: white;
  text-align: center;
  flex-shrink: 0;
  border-radius: 8px 8px 0 0;
}

.chat-header h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 500;
}

.chat-messages {
  flex-grow: 1;
  padding: 1.5rem 4rem 1.5rem 1.5rem; /* 增加右边距以容纳操作按钮 */
  overflow-y: auto;
  background-color: #fafafa;
}

.message-wrapper {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

.message-wrapper-user {
  justify-content: flex-end;
}

.message-wrapper-ai {
  justify-content: flex-start;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 8px;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.avatar svg {
  width: 24px;
  height: 24px;
}

.avatar-user {
  order: 2; /* 用户头像在右侧 */
  background-color: #409eff;
  color: white;
}

.avatar-ai {
  order: 1; /* AI头像在左侧 */
  background-color: #67c23a;
  color: white;
}

.message {
  max-width: 75%;
  line-height: 1.6;
  position: relative;
  border-radius: 18px;
  overflow: hidden;
}

.message-user {
  order: 1; /* 用户消息在左侧 */
}

.message-ai {
  order: 2; /* AI消息在右侧 */
}

.message span, .markdown-body {
  padding: 0.8rem 1.2rem;
  white-space: pre-wrap;
  display: block;
}

.message-user span {
  background: linear-gradient(135deg, #409eff, #5a7eff);
  color: white;
  border-radius: 18px 4px 18px 18px;
}

.message-ai .markdown-body {
  background-color: white;
  color: #333;
  border-radius: 4px 18px 18px 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.message-actions {
  position: absolute;
  right: 10px;
  top: 10px;
  display: flex;
  flex-direction: row;
  gap: 5px;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 5px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 10;
}

.message:hover .message-actions {
  opacity: 1;
}

/* 新的控制按钮样式 */
.input-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-label {
  font-size: 13px;
  color: #606266;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 下拉菜单激活状态 */
.el-dropdown-menu__item.is-active {
  color: #409eff;
  font-weight: bold;
}

.chat-input-area {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background-color: #fff;
  flex-shrink: 0;
  border-top: 1px solid #ebeef5;
}

.send-button {
  margin-top: 1rem;
  align-self: flex-end;
  min-width: 80px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-view-layout {
    flex-direction: column;
    height: 100vh;
  }
  
  .history-sidebar {
    width: 100%;
    height: 180px;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .chat-container {
    margin: 0 0 12px 0;
  }
  
  .message {
    max-width: 85%;
  }
  
  .input-controls {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .control-item {
    width: 100%;
  }
  
  .control-label {
    max-width: 100%;
  }
}
</style>
