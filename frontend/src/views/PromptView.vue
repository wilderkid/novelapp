<template>
  <div class="prompt-view-container">
    <div v-if="!projectStore.currentProject" class="no-project-selected">
      <el-empty description="请先选择一个小说项目">
        <el-button type="primary" @click="router.push('/novels')">选择小说</el-button>
      </el-empty>
    </div>

    <template v-else>
      <div class="content-header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/novels' }">小说管理</el-breadcrumb-item>
          <el-breadcrumb-item>{{ projectStore.currentProject.title }}</el-breadcrumb-item>
          <el-breadcrumb-item>提示词管理</el-breadcrumb-item>
        </el-breadcrumb>
        <el-button type="primary" @click="handleAddNew">新增提示词</el-button>
      </div>

      <div class="prompt-cards-container">
        <el-card v-for="prompt in prompts" :key="prompt.id" class="prompt-card">
          <template #header>
            <div class="card-header">
              <span>{{ prompt.name }}</span>
              <div class="card-actions">
                <el-button text type="primary" @click="handleEdit(prompt)">编辑</el-button>
                <el-button text type="danger" @click="handleDelete(prompt)">删除</el-button>
              </div>
            </div>
          </template>
          <div class="card-content" @click="handleView(prompt)">
            {{ prompt.content }}
          </div>
        </el-card>
      </div>
    </template>

    <!-- Add/Edit/View Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="50%">
      <el-form :model="currentPrompt" label-position="top">
        <el-form-item label="名称">
          <el-input v-model="currentPrompt.name" :readonly="isViewing"></el-input>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="currentPrompt.content" type="textarea" :rows="10" :readonly="isViewing"></el-input>
        </el-form-item>
      </el-form>
      <template #footer v-if="!isViewing">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useProjectStore } from '../stores/projectStore';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios'; // Assuming a generic axios instance is available

const API_URL = 'http://localhost:9009/api';

const router = useRouter();
const projectStore = useProjectStore();

const prompts = ref([]);
const dialogVisible = ref(false);
const isEditing = ref(false);
const isViewing = ref(false);
const currentPrompt = ref({});

const dialogTitle = computed(() => {
  if (isViewing.value) return '查看提示词';
  return isEditing.value ? '编辑提示词' : '新增提示词';
});

const fetchPrompts = async () => {
  if (!projectStore.currentProject) return;
  try {
    const response = await axios.get(`${API_URL}/projects/${projectStore.currentProject.id}/prompt-templates`);
    prompts.value = response.data;
  } catch (error) {
    ElMessage.error('加载提示词列表失败');
  }
};

onMounted(fetchPrompts);

const handleAddNew = () => {
  isEditing.value = false;
  isViewing.value = false;
  currentPrompt.value = { name: '', content: '' };
  dialogVisible.value = true;
};

const handleEdit = (prompt) => {
  isEditing.value = true;
  isViewing.value = false;
  currentPrompt.value = { ...prompt };
  dialogVisible.value = true;
};

const handleView = (prompt) => {
  isViewing.value = true;
  currentPrompt.value = { ...prompt };
  dialogVisible.value = true;
};

const handleDelete = (prompt) => {
  ElMessageBox.confirm(`确定要删除提示词 “${prompt.name}” 吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await axios.delete(`${API_URL}/prompt-templates/${prompt.id}`);
      ElMessage.success('删除成功');
      fetchPrompts(); // Refresh list
    } catch (error) {
      ElMessage.error('删除失败');
    }
  }).catch(() => {});
};

const handleSave = async () => {
  if (!currentPrompt.value.name || !currentPrompt.value.content) {
    ElMessage.warning('名称和内容不能为空');
    return;
  }

  const payload = {
    ...currentPrompt.value,
    project_id: projectStore.currentProject.id,
  };

  try {
    if (isEditing.value) {
      await axios.put(`${API_URL}/prompt-templates/${currentPrompt.value.id}`, payload);
    } else {
      await axios.post(`${API_URL}/projects/${projectStore.currentProject.id}/prompt-templates`, payload);
    }
    ElMessage.success('保存成功');
    dialogVisible.value = false;
    fetchPrompts(); // Refresh list
  } catch (error) {
    ElMessage.error('保存失败');
  }
};
</script>

<style scoped>
.prompt-view-container { padding: 20px; }
.no-project-selected { display: flex; justify-content: center; align-items: center; height: calc(100vh - 140px); }
.content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.prompt-cards-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.prompt-card .card-header { display: flex; justify-content: space-between; align-items: center; }
.prompt-card .card-content { height: 100px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; cursor: pointer; }
</style>
