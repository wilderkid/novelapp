import axios from 'axios';

const API_URL = 'http://localhost:9009/api';

// OpenAI兼容模式URL处理函数
export const processOpenAIUrl = (userProvidedUrl) => {
  if (!userProvidedUrl) {
    return {
      chatCompletionEndpoint: '',
      modelsEndpoint: '',
      isManualModelEntryRequired: false
    };
  }

  // 规则1：直接端点模式（特征: 包含 #）
  if (userProvidedUrl.includes('#')) {
    const baseUrl = userProvidedUrl.split('#')[0];
    return {
      chatCompletionEndpoint: baseUrl,
      modelsEndpoint: '',
      isManualModelEntryRequired: true
    };
  }

  // 规则2：V1已包含模式（特征: 以 /v1 或 /v1/ 结尾）
  let normalizedUrl = userProvidedUrl.endsWith('/') ? userProvidedUrl.slice(0, -1) : userProvidedUrl;
  
  if (normalizedUrl.endsWith('/v1')) {
    return {
      chatCompletionEndpoint: `${normalizedUrl}/chat/completions`,
      modelsEndpoint: `${normalizedUrl}/models`,
      isManualModelEntryRequired: false
    };
  }

  // 规则3：标准OpenAI模式（默认规则）
  return {
    chatCompletionEndpoint: `${normalizedUrl}/v1/chat/completions`,
    modelsEndpoint: `${normalizedUrl}/v1/models`,
    isManualModelEntryRequired: false
  };
};

// API密钥检测函数
export const checkApiKey = async (provider) => {
  try {
    const { chatCompletionEndpoint, modelsEndpoint, isManualModelEntryRequired } = processOpenAIUrl(provider.base_url);
    
    // 尝试获取模型列表来验证API密钥
    if (!isManualModelEntryRequired && modelsEndpoint) {
      const response = await axios.get(modelsEndpoint, {
        headers: {
          'Authorization': `Bearer ${provider.api_key}`
        }
      });
      return { valid: true, models: response.data.data || [] };
    } else {
      // 对于需要手动添加模型的提供商，只检查端点是否可访问
      const response = await axios.get(chatCompletionEndpoint, {
        headers: {
          'Authorization': `Bearer ${provider.api_key}`
        }
      });
      return { valid: true, models: [] };
    }
  } catch (error) {
    console.error('API密钥验证失败:', error);
    return { valid: false, error: error.response?.data?.error?.message || error.message };
  }
};

// 从服务商处获取模型列表
export const getModelsFromProvider = async (provider) => {
  const { modelsEndpoint, isManualModelEntryRequired } = processOpenAIUrl(provider.base_url);

  if (isManualModelEntryRequired || !modelsEndpoint) {
    throw new Error('该提供商不支持自动获取模型列表。');
  }

  const response = await axios.get(modelsEndpoint, {
    headers: {
      'Authorization': `Bearer ${provider.api_key}`
    }
  });

  // The models are usually in a 'data' property
  return response.data.data || [];
};

// 自动获取并添加模型
export const fetchAndAddModels = async (provider) => {
  try {
    const { modelsEndpoint, isManualModelEntryRequired } = processOpenAIUrl(provider.base_url);
    
    if (isManualModelEntryRequired || !modelsEndpoint) {
      return { success: false, message: '该提供商不支持自动获取模型列表，请手动添加' };
    }
    
    const response = await axios.get(modelsEndpoint, {
      headers: {
        'Authorization': `Bearer ${provider.api_key}`
      }
    });
    
    const models = response.data.data || [];
    if (models.length === 0) {
      return { success: false, message: '未找到可用模型' };
    }
    
    // 添加获取到的模型
    const addedModels = [];
    for (const model of models) {
      try {
        await createModel(provider.id, {
          name: model.id, // 使用模型ID作为名称，用户可以后续修改
          model_identifier: model.id,
          enabled: true,
          is_default: false
        });
        addedModels.push(model.id);
      } catch (error) {
        console.error(`添加模型 ${model.id} 失败:`, error);
      }
    }
    
    return { 
      success: true, 
      message: `成功添加 ${addedModels.length} 个模型`,
      models: addedModels
    };
  } catch (error) {
    console.error('获取模型列表失败:', error);
    return { 
      success: false, 
      message: error.response?.data?.error?.message || error.message 
    };
  }
};

// AI Provider services - 全局级别
export const getProviders = () => {
  return axios.get(`${API_URL}/ai-providers`);
};

export const createProvider = (data) => {
  return axios.post(`${API_URL}/ai-providers`, data);
};

export const updateProvider = (providerId, data) => {
  return axios.put(`${API_URL}/ai-providers/${providerId}`, data);
};

export const deleteProvider = (providerId) => {
  return axios.delete(`${API_URL}/ai-providers/${providerId}`);
};

// AI Provider services - 项目级别（保持原有功能）
export const getProjectProviders = (projectId) => {
  return axios.get(`${API_URL}/projects/${projectId}/ai-providers`);
};

export const createProjectProvider = (projectId, data) => {
  return axios.post(`${API_URL}/projects/${projectId}/ai-providers`, data);
};

// AI Model services
export const getModels = (providerId) => {
  return axios.get(`${API_URL}/ai-providers/${providerId}/ai-models`);
};

export const createModel = (providerId, data) => {
  return axios.post(`${API_URL}/ai-providers/${providerId}/ai-models`, data);
};

export const updateModel = (modelId, data) => {
  return axios.put(`${API_URL}/ai-models/${modelId}`, data);
};

export const deleteModel = (modelId) => {
  return axios.delete(`${API_URL}/ai-models/${modelId}`);
};
