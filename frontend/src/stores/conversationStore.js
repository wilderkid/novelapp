import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useConversationStore = defineStore('conversation', () => {
  // 状态
  const conversations = ref([]) // 所有对话列表
  const currentConversationId = ref(null) // 当前对话ID
  const currentMessages = ref([]) // 当前对话的消息列表

  // 获取所有对话
  const fetchConversations = async () => {
    try {
      const response = await axios.get('/api/conversations')
      conversations.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
      throw error
    }
  }

  // 获取指定对话的消息
  const fetchConversationMessages = async (convId) => {
    try {
      const response = await axios.get(`/api/conversations/${convId}/messages`)
      return response.data.map(m => ({ role: m.role, content: m.content }))
    } catch (error) {
      console.error('Failed to fetch conversation messages:', error)
      throw error
    }
  }

  // 创建新对话
  const createNewConversation = (title = '新对话') => {
    const newConversation = {
      id: Date.now(), // 临时ID，实际应用中应由后端生成
      title: title,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_temp: true // 标记为临时对话，未保存到后端
    }
    conversations.value.unshift(newConversation)
    return newConversation
  }

  // 开始新对话
  const startNewConversation = () => {
    currentConversationId.value = null
    currentMessages.value = [{ role: 'assistant', content: '你好！有什么可以帮助你的吗？' }]
  }

  // 加载对话
  const loadConversation = async (convId) => {
    try {
      const messages = await fetchConversationMessages(convId)
      currentMessages.value = messages
      currentConversationId.value = Number(convId)
    } catch (error) {
      console.error('Failed to load conversation:', error)
      throw error
    }
  }

  // 添加消息到当前对话
  const addMessage = (message) => {
    currentMessages.value.push(message)
  }

  // 更新当前对话ID
  const setCurrentConversationId = (convId) => {
    currentConversationId.value = convId
  }

  // 清空当前对话消息
  const clearCurrentMessages = () => {
    currentMessages.value = []
  }

  // 删除对话
  const deleteConversation = async (convId) => {
    try {
      await axios.delete(`/api/conversations/${convId}`)
      conversations.value = conversations.value.filter(conv => conv.id !== convId)
      
      // 如果删除的是当前对话，则开始新对话
      if (currentConversationId.value === convId) {
        startNewConversation()
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
      throw error
    }
  }

  // 重命名对话
  const renameConversation = async (convId, newTitle) => {
    try {
      await axios.put(`/api/conversations/${convId}`, { title: newTitle })
      const conversation = conversations.value.find(conv => conv.id === convId)
      if (conversation) {
        conversation.title = newTitle
      }
    } catch (error) {
      console.error('Failed to rename conversation:', error)
      throw error
    }
  }

  // 发送消息到AI并添加到指定对话
  const sendMessage = async (content, convId = null, history = [], prompt_template_id = null, ai_model_id = null, project_id = null) => {
    if (!content.trim()) {
      throw new Error('Message content cannot be empty');
    }

    // 检查是否需要变量替换
    if (content.includes('{{') && project_id) {
      try {
        const renderPayload = {
          content: content,
          project_id: project_id,
        };
        const response = await axios.post('/api/prompts/render', renderPayload);
        content = response.data.rendered_content;
        console.log('[ConversationStore DEBUG] User input rendered to:', content);
      } catch (error) {
        console.error('Failed to render user input:', error);
        throw error;
      }
    }

    const payload = {
      message: content,
      conversation_id: convId,
      history: history.map(m => ({ role: m.role, content: m.content })),
      prompt_template_id: prompt_template_id,
      ai_model_id: ai_model_id,
      project_id: project_id,
    };

    const response = await axios.post('/api/chat', payload);
    return response.data;
  };

  // 发送流式消息到AI并添加到指定对话
  const sendMessageStream = async (content, convId = null, history = [], prompt_template_id = null, ai_model_id = null, project_id = null) => {
    if (!content.trim()) {
      throw new Error('Message content cannot be empty');
    }

    // 检查是否需要变量替换
    if (content.includes('{{') && project_id) {
      try {
        const renderPayload = {
          content: content,
          project_id: project_id,
        };
        const response = await axios.post('/api/prompts/render', renderPayload);
        content = response.data.rendered_content;
        console.log('[ConversationStore DEBUG] User input rendered to:', content);
      } catch (error) {
        console.error('Failed to render user input:', error);
        throw error;
      }
    }

    const payload = {
      message: content,
      conversation_id: convId,
      history: history.map(m => ({ role: m.role, content: m.content })),
      prompt_template_id: prompt_template_id,
      ai_model_id: ai_model_id,
      project_id: project_id,
    };

    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    return response;
  };

  return {
    // 状态
    conversations,
    currentConversationId,
    currentMessages,

    // 方法
    fetchConversations,
    fetchConversationMessages,
    createNewConversation,
    startNewConversation,
    loadConversation,
    addMessage,
    setCurrentConversationId,
    clearCurrentMessages,
    deleteConversation,
    renameConversation,
    sendMessage,
    sendMessageStream
  }
})