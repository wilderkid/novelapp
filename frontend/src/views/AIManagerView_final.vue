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

    <!-- 添加/编辑模型对话框 -->
    <el-dialog v-model="modelDialogVisible" :title="isEditingModel ? '编辑模型' : '添加新模型'" width="500px">
      <el-form :model="modelForm" :rules="modelFormRules" ref="modelFormRef" label-position="top">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="modelForm.name" placeholder="用户友好的名称, 如: 创作模型 (GPT-4)"></el-input>
        </el-form-item>
        <el-form-item label="模型ID" prop="model_identifier">
          <el-input v-model="modelForm.model_identifier" placeholder="模型的实际ID, 如: gpt-4-1106-preview"></el-input>
        </el-form-item>
        <el-form-item label="Temperature">
          <el-slider v-model="modelForm.temperature" :min="0" :max="2" :step="0.1"></el-slider>
        </el-form-item>
        <el-form-item label="Max Tokens">
          <el-input-number v-model="modelForm.max_tokens" :min="1" :step="128"></el-input-number>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="modelForm.enabled" active-text="启用"></el-switch>
          <el-switch v-model="modelForm.is_default" active-text="设为默认" style="margin-left: 20px;"></el-switch>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="modelDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleModelSubmit">确定</el-button>
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
                <el-button :icon="Edit" size="small" @click="openEditProviderModal(provider)" :disabled="provider.is_system"></el-button>
              </el-tooltip>
              <el-tooltip content="删除提供商" placement="top">
                <el-button :icon="Delete" type="danger" size="small" @click="deleteProvider(provider)" :disabled="provider.is_system"></el-button>
              </el-tooltip>
            </el-button-group>
            <el-switch v-model="provider.enabled" @change="updateProviderStatus(provider)" style="margin-left: 15px;" />
          </div>
        </div>
        <div class="provider-body">
          <el-form label-position="top">
            <el-form-item label="API Key">
              <el-input v-model="provider.api_key" show-password placeholder="请输入 API Key" :disabled="provider.is_system">
                <template #append>
                  <el-button @click="checkApiKey(provider)">检测</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="API Base URL">
              <el-input v-model="provider.base_url" placeholder="请输入 API 地址" :disabled="provider.is_system" @input="updateUrlPreview('card', provider)"></el-input>
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
              <el-table-column prop="name" label="模型名称"></el-table-column>
              <el-table-column prop="model_identifier" label="模型ID"></el-table-column>
              <el-table-column label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '已启用' : '已禁用' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
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
import { Search, View, Edit, Delete, Warning } from '@element-plus/icons-vue';
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

      // 如果获取到了模型列表，询问用户是否要自动添加
      if (result.models && result.models.length > 0) {
        try {
          await ElMessageBox.confirm(
            `已获取到 ${result.models.length} 个可用模型，是否自动添加？`,
            '自动添加模型',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'info',
            }
          );

          // 用户确认，自动添加模型
          ElMessage.info('正在添加模型...');
          const addResult = await aiService.fetchAndAddModels(provider);

          if (addResult.success) {
            ElMessage.success(addResult.message);
            fetchProviders(); // 重新加载提供商列表
          } else {
            ElMessage.error(addResult.message);
          }
        } catch (action) {
          if (action !== 'cancel') {
            ElMessage.error('添加模型过程中发生错误');
            console.error(action);
          }
        }
      } else {
        // 没有获取到模型列表，提示用户手动添加
        const { isManualModelEntryRequired } = aiService.processOpenAIUrl(provider.base_url);
        if (isManualModelEntryRequired) {
          ElMessage.info('该提供商不支持自动获取模型列表，请手动添加模型');
        } else {
          ElMessage.warning('未能获取到模型列表，请检查API配置或手动添加模型');
        }
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
  // 初始化URL预览
  updateUrlPreview('edit');
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

    // 为每个提供商初始化URL预览
    providers.value.forEach(provider => {
      if (provider.base_url) {
        updateUrlPreview('card', provider);
      }
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
    // 仅更新 enabled 字段，其他字段保持不变
    await aiService.updateProvider(provider.id, { enabled: provider.enabled });
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
const isEditingModel = ref(false);
const modelFormRef = ref(null);
const modelForm = ref({});
const modelFormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  model_identifier: [{ required: true, message: '请输入模型ID', trigger: 'blur' }],
};

const openAddModelModal = (provider) => {
  isEditingModel.value = false;
  modelForm.value = {
    provider_id: provider.id,
    name: '',
    model_identifier: '',
    temperature: 0.7,
    max_tokens: 2048,
    enabled: true,
    is_default: false,
  };
  modelDialogVisible.value = true;
  modelFormRef.value?.resetFields();
};

const openEditModelModal = (model) => {
  isEditingModel.value = true;
  modelForm.value = { ...model };
  modelDialogVisible.value = true;
};

const handleModelSubmit = async () => {
  if (!modelFormRef.value) return;
  await modelFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditingModel.value) {
          await aiService.updateModel(modelForm.value.id, modelForm.value);
          ElMessage.success('模型更新成功');
        } else {
          await aiService.createModel(modelForm.value.provider_id, modelForm.value);
          ElMessage.success('模型添加成功');
        }
        modelDialogVisible.value = false;
        fetchProviders(); // 重新加载整个提供商列表以更新模型
      } catch (error) {
        ElMessage.error(isEditingModel.value ? '更新失败' : '添加失败');
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

</script>

<style scoped>
.ai-manager-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #dcdfe6;
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
  overflow-y: auto;
}
.provider-card {
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}
.provider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
}
.provider-name {
  font-size: 1.2em;
  font-weight: bold;
}
.provider-body {
  padding: 20px;
}
.model-section {
  margin-top: 20px;
}
.model-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.model-list-header h4 {
  margin: 0;
}
.url-preview {
  margin-top: 8px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
}
.url-preview p {
  margin: 4px 0;
}
.warning-text {
  color: #e6a23c;
  display: flex;
  align-items: center;
}
.warning-text .el-icon {
  margin-right: 4px;
}
</style>
