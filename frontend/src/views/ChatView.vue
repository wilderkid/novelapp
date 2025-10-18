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
        <h1>{{ currentConversationId ? '对话中' : '新对话' }}</h1>
      </div>
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(msg, index) in messages" :key="index" class="message-wrapper" :class="`message-wrapper-${msg.role}`">
          <div class="message" :class="`message-${msg.role}`">
            <div v-if="msg.role === 'ai'" v-html="renderMarkdown(msg.content)" class="markdown-body"></div>
            <span v-else>{{ msg.content }}</span>
          </div>
          <div v-if="msg.role === 'ai' && !isLoading" class="message-actions">
            <el-button size="small" circle :icon="CopyDocument" @click="copyMessage(msg.content)"></el-button>
            <el-button size="small" circle :icon="Refresh" @click="regenerateResponse(index)"></el-button>
          </div>
        </div>
      </div>
      <div class="chat-input-area">
        <div class="prompt-template-selector">
          <el-select v-model="selectedPromptTemplateId" placeholder="选择自定义指令 (可选)" clearable>
            <el-option
              v-for="item in promptTemplates"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
        </div>
        <div class="ai-model-selector">
          <el-select v-model="selectedAiModelId" placeholder="选择AI模型 (可选)" clearable>
            <el-option
              v-for="item in aiModels"
              :key="item.id"
              :label="item.name"
              :value="item.id">
            </el-option>
          </el-select>
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
import { ref, nextTick, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/default.css';
import { CopyDocument, Refresh, Edit, Delete } from '@element-plus/icons-vue';

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
  
  // 从界面上移除旧的AI回复
  messages.value.splice(aiMessageIndex, 1);
  
  // 复用sendMessage逻辑，但传入历史消息
  await sendMessage(userMessageContent);
};


const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
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
    // Assuming a project_id of 1 for now, as multi-tenancy is removed.
    // In a real app, this would be dynamic.
    const response = await axios.get(`http://localhost:9009/api/ai-providers/1/ai-models`);
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
  messages.value = [{ role: 'ai', content: '你好！有什么可以帮助你的吗？' }];
  userInput.value = '';
  selectedPromptTemplateId.value = null; // Clear selected prompt on new chat
  selectedAiModelId.value = null; // Clear selected AI model on new chat
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

  isLoading.value = true;

  // 如果是新消息（非重新生成），则添加到消息列表
  if (!messageContent) {
    messages.value.push({ role: 'user', content });
    userInput.value = '';
  }
  
  scrollToBottom();

  messages.value.push({ role: 'ai', content: '正在思考中...' });
  scrollToBottom();

  try {
    const payload = {
      message: content,
      conversation_id: currentConversationId.value,
      history: messages.value.slice(0, -2).map(m => ({ role: m.role, content: m.content })),
      prompt_template_id: selectedPromptTemplateId.value,
      ai_model_id: selectedAiModelId.value,
    };

    const response = await axios.post('http://localhost:9009/api/chat', payload);

    messages.value[messages.value.length - 1].content = response.data.reply;

    if (!currentConversationId.value) {
      currentConversationId.value = response.data.conversation_id;
      fetchConversations();
    }

  } catch (error) {
    console.error('AI request failed:', error);
    messages.value[messages.value.length - 1].content = '抱歉，与AI连接时出现错误。';
    ElMessage.error('AI响应失败');
  }
  finally {
    isLoading.value = false;
    scrollToBottom();
  }
};

const handleEnter = (e) => {
  if (e.shiftKey) {
    return;
  }
  sendMessage();
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
  background-color: #f9f9f9;
}

.history-sidebar {
  width: 240px;
  flex-shrink: 0;
  border-right: 1px solid #e0e0e0;
  background-color: #fff;
  display: flex;
  flex-direction: column;
}

.new-chat-button {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}
.new-chat-button .el-button {
  width: 100%;
}

.history-menu {
  flex-grow: 1;
  overflow-y: auto;
  border-right: none;
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

.chat-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  margin: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  padding: 1rem;
  background-color: #f7f7f7;
  border-bottom: 1px solid #e0e0e0;
  text-align: center;
  flex-shrink: 0;
}

.chat-header h1 {
  margin: 0;
  font-size: 1.25rem;
}

.chat-messages {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
}

.message-wrapper {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
}

.message-wrapper-user {
  align-items: flex-end;
}

.message-wrapper-ai {
  align-items: flex-start;
}

.message {
  max-width: 90%;
  line-height: 1.6;
}

.message-user .message {
  justify-content: flex-end;
}

.message-ai .message {
  justify-content: flex-start;
}

.message span, .markdown-body {
  padding: 0.6rem 1rem;
  border-radius: 18px;
  white-space: pre-wrap;
}

.message-user span {
  background-color: #409eff;
  color: white;
  border-top-right-radius: 4px;
}

.message-ai .markdown-body {
  background-color: #f0f2f5;
  color: #333;
  border-top-left-radius: 4px;
}

.message-actions {
  margin-top: 8px;
  margin-left: 10px;
  display: flex;
  gap: 8px;
}

.chat-input-area {
  display: flex;
  flex-direction: column; /* Changed to column to stack elements */
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  background-color: #f7f7f7;
  flex-shrink: 0;
}

.prompt-template-selector {
  margin-bottom: 1rem; /* Space between selector and textarea */
  width: 100%;
}

.ai-model-selector {
  margin-bottom: 1rem; /* Space between selector and textarea */
  width: 100%;
}

.send-button {
  margin-top: 1rem; /* Space between textarea and send button */
  align-self: flex-end; /* Align button to the right */
}
</style>
