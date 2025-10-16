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
          <el-input v-model="newProviderForm.base_url" placeholder="例如: https://api.openai.com/v1"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addProviderDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddProvider">确定</el-button>
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
              <el-input v-model="provider.base_url" placeholder="请输入 API 地址" :disabled="provider.is_system"></el-input>
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
import { Search, View, Edit, Delete } from '@element-plus/icons-vue';
import { useProjectStore } from '../stores/projectStore';
import * as aiService from '../services/aiService';

const projectStore = useProjectStore();
const searchQuery = ref('');
const providers = ref([]); // 使用空数组替代模拟数据

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
        await aiService.createProvider(projectStore.currentProject.id, newProviderForm.value);
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
  if (projectStore.currentProject?.id) {
    try {
      const response = await aiService.getProviders(projectStore.currentProject.id);
      providers.value = response.data;
    } catch (error) {
      ElMessage.error('加载AI提供商失败');
      console.error(error);
    }
  } else {
    providers.value = []; // 如果没有项目，则清空列表
  }
};

onMounted(() => {
  if (!projectStore.currentProject?.id) {
    ElMessage.warning('请先选择一个项目以管理AI提供商');
  }
  fetchProviders();
});

// 监听当前项目的变化
watch(() => projectStore.currentProject?.id, (newId, oldId) => {
  if (newId !== oldId) {
    fetchProviders();
  }
});

const updateProviderStatus = async (provider) => {
  try {
    await aiService.updateProvider(provider.id, { enabled: provider.enabled });
    ElMessage.success(`提供商 ${provider.name} 状态已更新`);
  } catch (error) {
    ElMessage.error('更新提供商状态失败');
    // 状态更新失败时，恢复原来的值
    provider.enabled = !provider.enabled;
  }
};

const openEditProviderModal = (provider) => {
  ElMessage.info(`将为 ${provider.name} 打开编辑对话框`);
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
</style>
