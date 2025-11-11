<template>
  <div class="ai-manager-view">
    <el-header class="view-header">
      <h2>AI 管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索平台或模型..."
          clearable
          class="search-input"
        >
          <template #prepend>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="openAddProviderModal">添加提供商</el-button>
      </div>
    </el-header>

    <!-- 添加提供商对话框 -->
    <el-dialog v-model="addProviderDialogVisible" title="添加新的AI提供商" width="500px">
      <el-form :model="newProviderForm" :rules="providerFormRules" ref="newProviderFormRef" label-position="top">
        <el-form-item label="提供商名称" prop="name">
          <el-input v-model="newProviderForm.name" placeholder="例如: OpenAI"></el-input>
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="newProviderForm.api_key" placeholder="请输入API Key"></el-input>
        </el-form-item>
        <el-form-item label="API Base URL" prop="base_url">
          <el-input v-model="newProviderForm.base_url" placeholder="例如: https://api.openai.com" @input="updateUrlPreview('new')"></el-input>
          <div v-if="urlPreview.new" class="url-preview">
            <p><strong>对话补全端点:</strong> {{ urlPreview.new.chatCompletionEndpoint }}</p>
            <p v-if="urlPreview.new.modelsEndpoint"><strong>模型列表端点:</strong> {{ urlPreview.new.modelsEndpoint }}</p>
            <p v-if="urlPreview.new.isManualModelEntryRequired" class="warning-text">
              <el-icon><Warning /></el-icon>
              无法自动获取模型列表，请手动添加模型名称
            </p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addProviderDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddProvider">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑提供商对话框 -->
    <el-dialog v-model="editProviderDialogVisible" title="编辑AI提供商" width="500px">
      <el-form :model="editProviderForm" :rules="providerFormRules" ref="editProviderFormRef" label-position="top">
        <el-form-item label="提供商名称" prop="name">
          <el-input v-model="editProviderForm.name" placeholder="例如: OpenAI"></el-input>
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="editProviderForm.api_key" placeholder="请输入API Key"></el-input>
        </el-form-item>
        <el-form-item label="API Base URL" prop="base_url">
          <el-input v-model="editProviderForm.base_url" placeholder="例如: https://api.openai.com" @input="updateUrlPreview('edit')"></el-input>
          <div v-if="urlPreview.edit" class="url-preview">
            <p><strong>对话补全端点:</strong> {{ urlPreview.edit.chatCompletionEndpoint }}</p>
            <p v-if="urlPreview.edit.modelsEndpoint"><strong>模型列表端点:</strong> {{ urlPreview.edit.modelsEndpoint }}</p>
            <p v-if="urlPreview.edit.isManualModelEntryRequired" class="warning-text">
              <el-icon><Warning /></el-icon>
              无法自动获取模型列表，请手动添加模型名称
            </p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editProviderDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateProvider">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 管理模型对话框 -->
    <el-dialog v-model="modelDialogVisible" title="管理模型" width="600px" @close="fetchProviders">
      <div class="model-management-dialog">
        <!-- Part 1: Fetched Models List -->
        <div class="fetched-models-section">
          <div class="fetched-models-header">
            <h4>可用在线模型</h4>
            <el-button 
              :loading="isFetchingModels" 
              @click="handleFetchModels" 
              type="primary"
            >
              {{ fetchedModels.length > 0 ? '刷新列表' : '获取列表' }}
            </el-button>
          </div>
          <el-input
            v-if="fetchedModels.length > 0"
            v-model="modelSearchQuery"
            placeholder="搜索模型..."
            clearable
            class="model-search-input"
          />
          <div v-if="fetchedModels.length > 0 && filteredFetchedModels.length > 0" class="fetched-models-list">
            <div v-for="model in filteredFetchedModels" :key="model.id" class="fetched-model-item">
              <span>{{ model.id }}</span>
              <el-button 
                :icon="isModelAdded(model.id) ? Minus : Plus" 
                circle 
                size="small"
                :type="isModelAdded(model.id) ? 'danger' : 'success'"
                plain
                @click="handleAddOrRemoveFetchedModel(model)"
              />
            </div>
          </div>
          <el-empty v-if="fetchedModels.length === 0" description="点击获取列表以显示可用模型"></el-empty>
          <el-empty v-if="fetchedModels.length > 0 && filteredFetchedModels.length === 0" description="未找到匹配的模型"></el-empty>
        </div>

        <el-divider />

        <!-- Part 2: Manual Add Form -->
        <el-form :model="modelForm" :rules="modelFormRules" ref="modelFormRef" label-position="top" class="manual-add-form">
          <el-form-item label="手动添加模型" prop="name">
             <el-input v-model="modelForm.name" placeholder="模型ID (例如: gpt-4-custom)">
              <template #append>
                <el-button @click="handleModelSubmit" :disabled="!modelForm.name">添加</el-button>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="modelDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑模型对话框 -->
    <el-dialog v-model="editModelDialogVisible" title="编辑模型" width="500px">
      <el-form :model="editModelForm" :rules="modelEditFormRules" ref="editModelFormRef" label-position="top">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="editModelForm.name" placeholder="模型在UI中显示的名称"></el-input>
        </el-form-item>
        <el-form-item label="模型ID" prop="model_identifier">
          <el-input v-model="editModelForm.model_identifier" placeholder="API中使用的模型ID"></el-input>
        </el-form-item>
        <el-form-item label="状态" prop="enabled">
           <el-switch v-model="editModelForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editModelDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateModel">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <el-main class="view-content">
      <div v-for="provider in filteredProviders" :key="provider.id" class="provider-card">
        <div class="provider-header">
          <div class="provider-title">
            <span class="provider-name">{{ provider.name }}</span>
            <el-tag v-if="provider.is_system" type="info" size="small">系统</el-tag>
          </div>
          <div class="provider-actions">
            <el-button-group>
              <el-tooltip content="编辑提供商" placement="top">
                <el-button :icon="Edit" size="small" @click="openEditProviderModal(provider)"></el-button>
              </el-tooltip>
              <el-tooltip content="删除提供商" placement="top">
                <el-button :icon="Delete" type="danger" size="small" @click="deleteProvider(provider)"></el-button>
              </el-tooltip>
            </el-button-group>
            <el-switch v-model="provider.enabled" @change="updateProviderStatus(provider)" style="margin-left: 15px;" />
          </div>
        </div>
        <div class="provider-body">
          <el-form label-position="top">
            <el-form-item label="API Key">
              <el-input v-model="provider.api_key" show-password placeholder="请输入 API Key">
                <template #append>
                  <el-button @click="checkApiKey(provider)">检测</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="API Base URL">
              <el-input v-model="provider.base_url" placeholder="请输入 API 地址" @input="updateUrlPreview('card', provider)"></el-input>
              <div v-if="urlPreview[provider.id]" class="url-preview">
                <p><strong>对话补全端点:</strong> {{ urlPreview[provider.id].chatCompletionEndpoint }}</p>
                <p v-if="urlPreview[provider.id].modelsEndpoint"><strong>模型列表端点:</strong> {{ urlPreview[provider.id].modelsEndpoint }}</p>
                <p v-if="urlPreview[provider.id].isManualModelEntryRequired" class="warning-text">
                  <el-icon><Warning /></el-icon>
                  无法自动获取模型列表，请手动添加模型名称
                </p>
              </div>
            </el-form-item>
          </el-form>

          <div class="model-section">
            <div class="model-list-header">
              <h4>模型列表</h4>
              <el-button type="text" @click="openAddModelModal(provider)">添加模型</el-button>
            </div>
            <el-table :data="provider.models" stripe class="model-table">
              <el-table-column prop="name" label="模型名称">
                <template #header>
                  <el-icon><Setting /></el-icon> 模型名称
                </template>
              </el-table-column>
              <el-table-column prop="model_identifier" label="模型ID">
                <template #header>
                  <el-icon><Key /></el-icon> 模型ID
                </template>
              </el-table-column>
              <el-table-column label="状态">
                <template #header>
                  <el-icon><SuccessFilled /></el-icon> 状态
                </template>
                <template #default="{ row }">
                  <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '已启用' : '已禁用' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #header>
                  <el-icon><Operation /></el-icon> 操作
                </template>
                <template #default="{ row }">
                  <el-button-group>
                    <el-tooltip content="查看" placement="top">
                      <el-button :icon="View" size="small" @click="openViewModel(row)"></el-button>
                    </el-tooltip>
                    <el-tooltip content="编辑" placement="top">
                      <el-button :icon="Edit" size="small" @click="openEditModelModal(row)"></el-button>
                    </el-tooltip>
                     <el-tooltip content="删除" placement="top">
                      <el-button :icon="Delete" type="danger" size="small" @click="deleteModel(row)"></el-button>
                    </el-tooltip>
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, View, Edit, Delete, Warning, Plus, Minus, Setting, Key, SuccessFilled, Operation } from '@element-plus/icons-vue';
import { useProjectStore } from '../stores/projectStore';
import * as aiService from '../services/aiService';

const projectStore = useProjectStore();
const searchQuery = ref('');
const providers = ref([]); // 使用空数组替代模拟数据

// URL预览相关
const urlPreview = ref({
  new: null,
  edit: null
});

// 更新URL预览
const updateUrlPreview = (type, provider = null) => {
  if (type === 'new') {
    urlPreview.value.new = aiService.processOpenAIUrl(newProviderForm.value.base_url);
  } else if (type === 'edit') {
    urlPreview.value.edit = aiService.processOpenAIUrl(editProviderForm.value.base_url);
  } else if (type === 'card' && provider) {
    urlPreview.value[provider.id] = aiService.processOpenAIUrl(provider.base_url);
  }
};

// API密钥检测
const checkApiKey = async (provider) => {
  if (!provider.api_key || !provider.base_url) {
    ElMessage.warning('请先填写API Key和Base URL');
    return;
  }
  
  try {
    ElMessage.info('正在验证API密钥...');
    const result = await aiService.checkApiKey(provider);
    
    if (result.valid) {
      ElMessage.success('API密钥验证成功');
      
      // 如果获取到了模型列表，可以提示用户
      if (result.models && result.models.length > 0) {
        ElMessage.info(`已获取到 ${result.models.length} 个可用模型`);
      }
    } else {
      ElMessage.error(`API密钥验证失败: ${result.error}`);
    }
  } catch (error) {
    ElMessage.error('API密钥验证过程中发生错误');
    console.error(error);
  }
};

// 添加提供商相关
const addProviderDialogVisible = ref(false);
const newProviderFormRef = ref(null);
const newProviderForm = ref({
  name: '',
  api_key: '',
  base_url: ''
});
const providerFormRules = {
  name: [{ required: true, message: '请输入提供商名称', trigger: 'blur' }],
};

const openAddProviderModal = () => {
  newProviderForm.value = { name: '', api_key: '', base_url: '' };
  addProviderDialogVisible.value = true;
  newProviderFormRef.value?.resetFields();
};

const handleAddProvider = async () => {
  if (!newProviderFormRef.value) return;
  await newProviderFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await aiService.createProvider(newProviderForm.value);
        ElMessage.success('提供商添加成功');
        addProviderDialogVisible.value = false;
        fetchProviders(); // 重新加载列表
      } catch (error) {
        ElMessage.error('添加提供商失败');
        console.error(error);
      }
    }
  });
};

// 编辑提供商相关
const editProviderDialogVisible = ref(false);
const editProviderFormRef = ref(null);
const editProviderForm = ref({
  id: null,
  name: '',
  api_key: '',
  base_url: ''
});

const openEditProviderModal = (provider) => {
  editProviderForm.value = { ...provider };
  editProviderDialogVisible.value = true;
  editProviderFormRef.value?.resetFields();
};

const handleUpdateProvider = async () => {
  if (!editProviderFormRef.value) return;
  await editProviderFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await aiService.updateProvider(editProviderForm.value.id, editProviderForm.value);
        ElMessage.success('提供商更新成功');
        editProviderDialogVisible.value = false;
        fetchProviders(); // 重新加载列表
      } catch (error) {
        ElMessage.error('更新提供商失败');
        console.error(error);
      }
    }
  });
};

const filteredProviders = computed(() => {
  if (!searchQuery.value) {
    return providers.value;
  }
  const lowerQuery = searchQuery.value.toLowerCase();
  return providers.value.filter(p => 
    p.name.toLowerCase().includes(lowerQuery) || 
    p.models.some(m => m.name.toLowerCase().includes(lowerQuery) || m.model_identifier.toLowerCase().includes(lowerQuery))
  );
});

const fetchProviders = async () => {
  try {
    const response = await aiService.getProviders();
    providers.value = response.data;
    // 获取 providers 后，更新每个 provider 的 URL 预览
    providers.value.forEach(p => {
      updateUrlPreview('card', p);
    });
  } catch (error) {
    ElMessage.error('加载AI提供商失败');
    console.error(error);
  }
};

onMounted(() => {
  fetchProviders();
});

// 监听当前项目的变化 (已移除，因为AI管理是全局的)
// watch(() => projectStore.currentProject?.id, (newId, oldId) => {
//   if (newId !== oldId) {
//     fetchProviders();
//   }
// });

const updateProviderStatus = async (provider) => {
  try {
    // 传递完整的提供商数据以进行更新
    await aiService.updateProvider(provider.id, provider);
    ElMessage.success(`提供商 ${provider.name} 状态已更新`);
  } catch (error) {
    ElMessage.error('更新提供商状态失败');
    // 状态更新失败时，恢复原来的值
    provider.enabled = !provider.enabled;
    console.error(error);
  }
};

const deleteProvider = async (provider) => {
  try {
    await ElMessageBox.confirm(`确定要删除提供商 "${provider.name}" 吗？这将同时删除其下所有模型配置。`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    await aiService.deleteProvider(provider.id);
    ElMessage.success('提供商已删除');
    fetchProviders(); // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
      console.error(error);
    }
  }
};

// --- 模型管理 ---
const modelDialogVisible = ref(false);
const modelFormRef = ref(null);
const modelForm = ref({}); // For manual adding
const currentProviderForModel = ref(null);
const isFetchingModels = ref(false);
const fetchedModels = ref([]);
const modelSearchQuery = ref('');

const filteredFetchedModels = computed(() => {
  if (!modelSearchQuery.value) {
    return fetchedModels.value;
  }
  const lowerQuery = modelSearchQuery.value.toLowerCase();
  return fetchedModels.value.filter(model => 
    model.id.toLowerCase().includes(lowerQuery)
  );
});

const modelFormRules = {
  name: [{ required: true, message: '请输入模型ID', trigger: 'blur' }],
};

const openAddModelModal = (provider) => {
  currentProviderForModel.value = provider;
  
  const cachedModels = sessionStorage.getItem(`models_${provider.id}`);
  if (cachedModels) {
    fetchedModels.value = JSON.parse(cachedModels);
  } else {
    fetchedModels.value = [];
  }

  modelForm.value = {
    provider_id: provider.id,
    name: '', // For manual add
  };
  
  modelDialogVisible.value = true;
};

const handleFetchModels = async () => {
  if (!currentProviderForModel.value) return;
  
  const provider = providers.value.find(p => p.id === currentProviderForModel.value.id);
  if (!provider || !provider.api_key || !provider.base_url) {
    ElMessage.warning('请先为该提供商设置API Key和Base URL');
    return;
  }

  isFetchingModels.value = true;
  try {
    const models = await aiService.getModelsFromProvider(provider);
    fetchedModels.value = models;
    sessionStorage.setItem(`models_${provider.id}`, JSON.stringify(models));

    if (models.length > 0) {
      ElMessage.success(`成功获取 ${models.length} 个模型`);
    } else {
      ElMessage.info('未找到可用的在线模型');
    }
  } catch (error) {
    ElMessage.error(`获取模型失败: ${error.message}`);
    console.error(error);
  } finally {
    isFetchingModels.value = false;
  }
};

const isModelAdded = (modelIdentifier) => {
  if (!currentProviderForModel.value || !currentProviderForModel.value.models) {
    return false;
  }
  return currentProviderForModel.value.models.some(m => m.model_identifier === modelIdentifier);
};

const handleAddOrRemoveFetchedModel = async (model) => {
  const providerId = currentProviderForModel.value.id;
  const existingModel = currentProviderForModel.value.models.find(m => m.model_identifier === model.id);

  if (existingModel) {
    // Remove
    try {
      await aiService.deleteModel(existingModel.id);
      const index = currentProviderForModel.value.models.findIndex(m => m.id === existingModel.id);
      if (index > -1) {
        currentProviderForModel.value.models.splice(index, 1);
      }
      ElMessage.success(`模型 '${model.id}' 已移除`);
    } catch (error) {
      ElMessage.error('移除模型失败');
      console.error(error);
    }
  } else {
    // Add
    try {
      const newModelData = {
        name: model.id,
        model_identifier: model.id,
        enabled: true,
        is_default: false,
      };
      const response = await aiService.createModel(providerId, newModelData);
      currentProviderForModel.value.models.push(response.data);
      ElMessage.success(`模型 '${model.id}' 已添加`);
    } catch (error) {
      ElMessage.error('添加模型失败');
      console.error(error);
    }
  }
};

// For the manual add form
const handleModelSubmit = async () => {
  if (!modelFormRef.value) return;
  await modelFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const modelData = {
            provider_id: modelForm.value.provider_id,
            name: modelForm.value.name,
            model_identifier: modelForm.value.name, // Use name as identifier for manual add
            enabled: true,
            is_default: false,
        };
        const response = await aiService.createModel(modelData.provider_id, modelData);
        currentProviderForModel.value.models.push(response.data);
        ElMessage.success('手动添加模型成功');
        modelForm.value.name = ''; // Clear input
        modelFormRef.value.resetFields();
      } catch (error) {
        ElMessage.error('添加失败');
        console.error(error);
      }
    }
  });
};

const deleteModel = async (model) => {
  try {
    await ElMessageBox.confirm(`确定要删除模型 "${model.name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    await aiService.deleteModel(model.id);
    ElMessage.success('模型已删除');
    fetchProviders(); // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
      console.error(error);
    }
  }
};

// --- 编辑模型 ---
const editModelDialogVisible = ref(false);
const editModelFormRef = ref(null);
const editModelForm = ref({});
const modelEditFormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  model_identifier: [{ required: true, message: '请输入模型ID', trigger: 'blur' }],
};

const openEditModelModal = (model) => {
  editModelForm.value = { ...model };
  editModelDialogVisible.value = true;
};

const handleUpdateModel = async () => {
  if (!editModelFormRef.value) return;
  await editModelFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await aiService.updateModel(editModelForm.value.id, editModelForm.value);
        ElMessage.success('模型更新成功');
        editModelDialogVisible.value = false;
        fetchProviders(); // Reload all data
      } catch (error) {
        ElMessage.error('更新模型失败');
        console.error(error);
      }
    }
  });
};
</script>

<style scoped>
.ai-manager-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #dcdfe6;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}
.search-input {
  width: 250px;
}
.view-content {
  padding: 20px;
  background-color: #f5f7fa;
  flex: 1;
  overflow-y: auto;
}
.provider-card {
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  transition: box-shadow 0.3s ease;
}
.provider-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0,0,0,0.15);
}
.provider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #fafafa;
  border-radius: 8px 8px 0 0;
}
.provider-name {
  font-size: 1.2em;
  font-weight: bold;
  color: #303133;
}
.provider-body {
  padding: 20px;
}
.model-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
.model-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.model-list-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}
.url-preview {
  margin-top: 8px;
  padding: 10px;
  background-color: #f0f9ff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
  font-size: 13px;
}
.url-preview p {
  margin: 5px 0;
}
.warning-text {
  color: #e6a23c;
  display: flex;
  align-items: center;
  background-color: #fdf6ec;
  padding: 8px;
  border-radius: 4px;
  margin-top: 8px;
}
.warning-text .el-icon {
  margin-right: 4px;
}

.fetched-models-section {
  margin-top: 10px;
  padding: 10px 0;
}
.fetched-models-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.fetched-models-header h4 {
  margin: 0;
  color: #303133;
}
.fetched-models-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  background-color: #fafafa;
}
.fetched-model-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}
.fetched-model-item:last-child {
  border-bottom: none;
}
.manual-add-form {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}
.model-search-input {
  margin-bottom: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .search-input {
    width: 100%;
  }
  
  .provider-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .provider-actions {
    width: 100%;
    display: flex;
    justify-content: space-between;
  }
}

/* 表格样式优化 */
:deep(.model-table) {
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style>
