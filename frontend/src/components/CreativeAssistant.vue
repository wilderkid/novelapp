<template>
  <el-aside :width="sidebarWidth + 'px'" class="creative-assistant-sidebar" v-if="creativeAssistantVisible" ref="assistantSidebar">
    <div class="assistant-container">
      <div class="assistant-header">
        <h3>创作助手</h3>
        <div>
          <el-button type="text" @click="startNewConversation" title="开始新对话">
            <el-icon><Refresh /></el-icon>
          </el-button>
          <el-button type="text" @click="clearCurrentMessages" title="清除当前对话">
            <el-icon><Delete /></el-icon>
          </el-button>
          <el-button type="text" @click="toggleCollapse">
            <el-icon><Right /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="assistant-content">
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
              <div v-if="msg.role === 'assistant'" v-html="formatMessage(msg.content)" class="markdown-body"></div>
              <span v-else>{{ msg.content }}</span>
              <div v-if="msg.role === 'assistant' && !isLoading" class="message-actions">
                <el-button size="small" circle :icon="CopyDocument" @click="copyMessage(msg.content)" title="复制消息"></el-button>
                <el-button size="small" circle :icon="Refresh" @click="regenerateResponse(index)" title="重新生成"></el-button>
                <el-button size="small" circle :icon="Delete" @click="deleteMessage(index)" title="删除消息"></el-button>
              </div>
              <div v-if="msg.role === 'user' && !isLoading" class="message-actions">
                <el-button size="small" circle :icon="Delete" @click="deleteMessage(index)" title="删除消息"></el-button>
              </div>
            </div>
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
            placeholder="请输入提示词... (Shift+Enter 换行)"
            @keydown.enter.prevent="handleEnter"
          />
          <div class="input-actions">
            <el-button type="primary" @click="newSendMessageStream" :loading="isLoading" :icon="Promotion">
              <span v-if="!isLoading">发送</span>
            </el-button>
            <el-button 
              @click="insertIntoEditor" 
              :disabled="!activeEditorInstance || !lastAiResponse"
              title="将最后一条AI回复插入编辑器"
              :icon="DocumentCopy">
              写入编辑器
            </el-button>

          </div>
        </div>
      </div>
    </div>
    <div class="resize-bar"></div>
  </el-aside>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useEditorStore } from '../stores/editorStore';
import { useProjectStore } from '../stores/projectStore';
import { useConversationStore } from '../stores/conversationStore';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';
import { Right, ChatDotRound, Setting, CopyDocument, Refresh, ChatLineRound, User, Delete, Promotion, DocumentCopy } from '@element-plus/icons-vue';
import MarkdownIt from 'markdown-it';

const editorStore = useEditorStore();
const projectStore = useProjectStore();
const conversationStore = useConversationStore();
const userInput = ref('');
// Add a conversation ID to track the conversation in the creative assistant
const conversationId = ref(null);
const messages = ref([]); // Keep local messages for the temporary creative assistant session
const isLoading = ref(false);
const messagesContainer = ref(null);

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

// When creative assistant is hidden, optionally keep the conversation or reset it
// For now, we keep the conversation in the component but you could add logic to clear it

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
  messages.value.push({ role: 'assistant', content: '你好！有什么可以帮助你的吗？' });
  
  // Initialize resize if the assistant is already visible
  if (creativeAssistantVisible.value) {
    nextTick(() => {
      initResize();
    });
  }
});

// 监听侧边栏可见性，在可见时初始化拖动功能
watch(creativeAssistantVisible, (newValue) => {
  if (newValue) {
    nextTick(() => {
      initResize();
    });
  }
}, { immediate: true }); // Initialize immediately when component mounts if already visible

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

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// Modify sendMessageStream function to support updating existing messages
const testUserInput = () => {
  console.log('[CreativeAssistant] Testing userInput:');
  console.log('[CreativeAssistant] Current userInput value:', userInput.value);
  console.log('[CreativeAssistant] Current isLoading state:', isLoading.value);
  console.log('[CreativeAssistant] Messages count:', messages.value.length);
};

const sendMessageStream = async (messageContent = null, updateMessageIndex = null) => {
  console.log('[CreativeAssistant] sendMessageStream called with:', { messageContent, updateMessageIndex, userInput: userInput.value });
  const content = messageContent || userInput.value;
  if (!content.trim()) {
    ElMessage.warning('消息不能为空');
    return;
  }

  // 检查用户输入和提示词模板中是否包含变量，如果包含，则必须有项目上下文
  const selectedTemplate = promptTemplates.value.find(t => t.id === selectedPromptTemplateId.value);
  const templateContent = selectedTemplate ? selectedTemplate.content : '';
  const fullContentToCheck = content + templateContent; // 检查用户输入和模板内容

  if (fullContentToCheck.includes('{{') && !currentProject.value) {
    ElMessage.warning('您似乎使用了变量，请先在“小说管理”中选择一个项目以正确渲染它们。');
    return;
  }

  if (isLoading.value) {
    console.log('[CreativeAssistant] Already loading, returning early');
    return;
  }

  isLoading.value = true;
  console.log('[CreativeAssistant] Set isLoading to true');

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
      console.log('[CreativeAssistant DEBUG] User input rendered to:', processedUserInput);
    } catch (error) {
      console.error('Failed to render user input:', error);
      ElMessage.error('渲染用户输入中的变量失败。');
      messages.value.pop(); // 移除已添加的"正在思考中..."消息
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

    const payload = {
      message: processedUserInput, // 使用渲染后的用户输入
      conversation_id: conversationId.value, // Use conversation ID if exists
      history: actualHistory.map(m => ({ role: m.role, content: m.content })),
      prompt_template_id: selectedPromptTemplateId.value,
      ai_model_id: selectedAiModelId.value,
      project_id: currentProject.value ? currentProject.value.id : null // 附加项目ID
    };

    console.log('[CreativeAssistant DEBUG] Sending stream payload:', payload);

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
                // 保存对话ID以供后续消息使用
                if (!conversationId.value) {
                  conversationId.value = data.conversation_id;
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

// Add a new sendMessageStream function based on the working ChatView implementation
const newSendMessageStream = async (messageContent = null, updateMessageIndex = null) => {
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
      console.log('[CreativeAssistant DEBUG] User input rendered to:', processedUserInput);
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

    const payload = {
      message: processedUserInput, // 使用渲染后的用户输入
      conversation_id: conversationId.value, // Use conversation ID if exists
      history: actualHistory.map(m => ({ role: m.role, content: m.content })),
      prompt_template_id: selectedPromptTemplateId.value,
      ai_model_id: selectedAiModelId.value,
      project_id: currentProject.value ? currentProject.value.id : null // 附加项目ID
    };

    console.log('[CreativeAssistant DEBUG] Sending stream payload:', payload);

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
                // 保存对话ID以供后续消息使用
                if (!conversationId.value) {
                  conversationId.value = data.conversation_id;
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

const debugSendMessage = () => {
  console.log('发送按钮被点击了！');
  newSendMessageStream();
};

const handleEnter = (e) => {
  console.log('[CreativeAssistant] handleEnter called with event:', e);
  console.log('[CreativeAssistant] shiftKey:', e.shiftKey);
  if (e.shiftKey) {
    console.log('[CreativeAssistant] Shift key pressed, allowing new line');
    return;
  }
  console.log('[CreativeAssistant] Enter key pressed, calling sendMessageStream');
  // Use stream API to send message
  sendMessageStream();
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

// Function to clear only the current messages but keep the conversation context

// Function to clear only the current messages but keep the conversation context
const clearCurrentMessages = () => {
  ElMessageBox.confirm(
    '确定要清除当前对话内容吗？这将清除所有消息记录，但保持当前的AI设置继续对话。', 
    '清除对话确认',
    {
      confirmButtonText: '确定清除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // Reset to initial state with just the assistant greeting
    messages.value = [{ role: 'assistant', content: '你好！有什么可以帮助你的吗？' }];
    userInput.value = '';
    ElMessage.success('对话内容已清除');
  }).catch(() => {
    // User cancelled
    ElMessage.info('已取消清除操作');
  });
};

// Add a function to start a new conversation
const startNewConversation = () => {
  conversationId.value = null;
  messages.value = [{ role: 'assistant', content: '你好！有什么可以帮助你的吗？' }];
  userInput.value = '';
};

// Regenerate AI response
const regenerateResponse = async (aiMessageIndex) => {
  // Find the corresponding user question for this AI response
  const userMessageIndex = aiMessageIndex - 1;
  if (userMessageIndex < 0 || messages.value[userMessageIndex].role !== 'user') {
    ElMessage.error('找不到对应的用户提问');
    return;
  }
  const userMessageContent = messages.value[userMessageIndex].content;
  
  // Update AI response in place instead of removing it
  messages.value[aiMessageIndex].content = '正在重新思考中...';
  
  // Reuse sendMessageStream logic, but pass historical messages and specify the message index to update
  await sendMessageStream(userMessageContent, aiMessageIndex);
};

// Delete specific message
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
      // If it's a user message, delete the following AI response as well
      const message = messages.value[messageIndex];
      if (message.role === 'user' && messageIndex + 1 < messages.value.length) {
        const nextMessage = messages.value[messageIndex + 1];
        if (nextMessage.role === 'assistant') {
          // Delete user message and AI response
          messages.value.splice(messageIndex, 2);
          ElMessage.success('消息对已删除');
          return;
        }
      }
      
      // Delete single message
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

// Copy message to clipboard
const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content);
    ElMessage.success('已复制到剪贴板');
  } catch (err) {
    ElMessage.error('复制失败');
  }
};



// 侧边栏宽度调整
const assistantSidebar = ref(null);
const sidebarWidth = ref(350); // 默认宽度
const isResizing = ref(false);
const startX = ref(0);
const startWidth = ref(0);

const initResize = () => {
  // Use nextTick to ensure DOM is rendered before accessing elements
  nextTick(() => {
    const resizeBar = assistantSidebar.value?.$el.querySelector('.resize-bar');
    if (!resizeBar) {
      console.warn('Resize bar not found in CreativeAssistant component');
      return;
    }
    
    resizeBar.addEventListener('mousedown', startResize);
  });
};

const startResize = (e) => {
  isResizing.value = true;
  startX.value = e.clientX;
  startWidth.value = sidebarWidth.value;
  
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', stopResize);
  
  e.preventDefault();
};

const handleMouseMove = (e) => {
  if (!isResizing.value) return;
  
  const diff = e.clientX - startX.value;
  // For a right-side sidebar, dragging the left edge of the sidebar to the left
  // makes the sidebar wider, so we subtract the negative diff (which increases width)
  // Dragging the left edge to the right makes the sidebar narrower
  // diff = positive when dragging right -> startWidth - positive = smaller width
  // diff = negative when dragging left -> startWidth - negative = larger width
  const newWidth = startWidth.value - diff;
  
  // 限制最小和最大宽度
  if (newWidth >= 200 && newWidth <= 600) {
    sidebarWidth.value = newWidth;
  }
};

const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', stopResize);
};

// Clean up event listeners on component unmount
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', stopResize);
});

</script>

<style scoped>
.creative-assistant-sidebar {
  background-color: #f9fafb;
  border-left: 1px solid #e4e7ed;
  transition: width 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative; /* 为resize-bar定位 */
}

.assistant-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  flex-grow: 1; /* 确保内容区域填充可用空间 */
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

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  margin-bottom: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 1.5rem 4rem 1.5rem 1.5rem; /* 增加右边距以容纳操作按钮 */
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

.message-wrapper-assistant {
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
}

.avatar svg {
  width: 24px;
  height: 24px;
}

.avatar-user {
  order: 2; /* 用户头像在右侧 */
}

.avatar-assistant {
  order: 1; /* AI头像在左侧 */
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

.message-assistant {
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

.message-assistant .markdown-body {
  background-color: white;
  color: #333;
  border-radius: 4px 18px 18px 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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

/* 消息操作按钮 */
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

/* 宽度调整条 */
.resize-bar {
  position: absolute;
  left: -5px; /* 位于侧边栏的左侧边缘 */
  top: 0;
  bottom: 0;
  width: 10px;
  cursor: col-resize;
  z-index: 10;
  background-color: transparent;
}

.resize-bar:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.resize-bar:active {
  background-color: rgba(0, 0, 0, 0.2);
}
</style>
