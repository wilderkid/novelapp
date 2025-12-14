<template>
  <div class="resource-view-container">
    <div v-if="!projectStore.currentProject" class="no-project-selected">
      <el-empty description="请先选择一个小说项目">
        <el-button type="primary" @click="goToNovels">选择小说</el-button>
      </el-empty>
    </div>

    <template v-else>
      <div class="content-header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/novels' }">小说管理</el-breadcrumb-item>
          <el-breadcrumb-item>{{ projectStore.currentProject.title }}</el-breadcrumb-item>
          <el-breadcrumb-item>资源管理</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <div class="content-main">
        <div class="sidebar">
          <resource-sidebar 
            ref="sidebarRef"
            @open-summary-modal="openSummaryModal"
            @open-editor="openResourceEditor"
            @item-selected="openResourceEditor"
            @open-add-modal="openAddItemModal"
            @delete-item="handleDeleteItem"
          />
        </div>

        <div class="editor-area">
          <div v-if="currentResource" class="resource-editor">
            <div class="editor-header">
              <el-input v-if="currentResource.type !== 'worldview'" v-model="currentResource.item.name" placeholder="资源名称" class="title-input" />
              <h3 v-else>世界观</h3>
              <div class="editor-actions">
                <el-button @click="saveCurrentResource">保存</el-button>
              </div>
            </div>
            <div class="editor-content">
              <UEditorPlus
                ref="resourceEditorRef"
                v-model="currentResource.item.content"
                :editor-id="'resource-editor-' + currentResource.type + '-' + currentResource.item.id"
                :key="currentResource.type + '-' + currentResource.item.id"
                @auto-save="autoSaveResource"
              />
            </div>
          </div>
          <div v-else class="empty-editor">
            <el-empty description="请从左侧选择一个资源开始编辑" />
          </div>
        </div>
      </div>
    </template>

    <!-- 资源管理弹窗 -->
    <el-dialog v-model="summaryModalVisible" :title="modalTitle" width="60%">
      <div class="modal-summary">
        <span>总计: {{ resourceList.length }} 项</span>
      </div>
      <el-table :data="resourceList" style="width: 100%" max-height="400">
        <el-table-column prop="name" label="名称" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" @click="editResourceFromModal(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="confirmDeleteResource(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 新增条目弹窗 -->
    <el-dialog v-model="addItemModalVisible" :title="'新增' + resourceTypeInfo.name" width="30%">
      <el-form>
        <el-form-item :label="resourceTypeInfo.name + '名称'">
          <el-input v-model="newItemName" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addItemModalVisible = false">取消</el-button>
        <el-button type="primary" @click="addNewItem">确定</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useProjectStore } from '../stores/projectStore';
import ResourceSidebar from '../components/ResourceSidebar.vue';
import UEditorPlus from '../components/UEditorPlus_New.vue';
import { worldviewService, characterService, organizationService, supernaturalPowerService, weaponService, dungeonService } from '../services/resourceService';

const router = useRouter();
const projectStore = useProjectStore();

// Component refs
const sidebarRef = ref(null);

// Editor state
const currentResource = ref(null);
const resourceEditorRef = ref(null);

// Auto-save state
const isSaving = ref(false);
const lastSaveTime = ref(null);

// Modal state
const summaryModalVisible = ref(false);
const addItemModalVisible = ref(false);
const currentOpenResourceType = ref('');
const resourceList = ref([]);
const newItemName = ref('');

const resourceTypeMap = {
  rpg_characters: { name: '角色', service: characterService },
  organizations: { name: '组织', service: organizationService },
  supernatural_powers: { name: '超凡之力', service: supernaturalPowerService },
  weapons: { name: '兵器', service: weaponService },
  dungeons: { name: '副本', service: dungeonService },
  worldview: { name: '世界观', service: worldviewService },
};

const resourceTypeInfo = computed(() => resourceTypeMap[currentOpenResourceType.value] || { name: '' });
const modalTitle = computed(() => `${resourceTypeInfo.value.name}管理`);

const goToNovels = () => router.push('/novels');

// Open editor directly (for Worldview or from modal)
const openResourceEditor = async (resource) => {
  const service = resourceTypeMap[resource.type].service;
  try {
    const id = resource.type === 'worldview' ? projectStore.currentProject.id : resource.item.id;
    const response = await service.get(id);
    currentResource.value = { type: resource.type, item: response.data };
    summaryModalVisible.value = false;
  } catch (error) {
    ElMessage.error(`加载${resourceTypeMap[resource.type].name}失败`);
  }
};

// Open summary modal (for Characters, Orgs, etc.)
const openSummaryModal = async (resourceType) => {
  currentOpenResourceType.value = resourceType;
  const service = resourceTypeMap[resourceType].service;
  try {
    const response = await service.getAll(projectStore.currentProject.id);
    resourceList.value = response.data;
    summaryModalVisible.value = true;
  } catch (error) {
    ElMessage.error(`获取${resourceTypeInfo.value.name}列表失败`);
  }
};

const editResourceFromModal = (item) => {
  openResourceEditor({ type: currentOpenResourceType.value, item });
};

const openAddItemModal = (resourceType) => {
  currentOpenResourceType.value = resourceType;
  newItemName.value = '';
  addItemModalVisible.value = true;
};

const addNewItem = async () => {
  if (!newItemName.value) {
    ElMessage.warning('名称不能为空');
    return;
  }
  const service = resourceTypeMap[currentOpenResourceType.value].service;
  try {
    await service.create(projectStore.currentProject.id, { name: newItemName.value, content: '' });
    ElMessage.success('新增成功');
    addItemModalVisible.value = false;
    // Refresh modal list
    const response = await service.getAll(projectStore.currentProject.id);
    resourceList.value = response.data;
    // Refresh sidebar list
    if (sidebarRef.value) {
      sidebarRef.value.refreshList(currentOpenResourceType.value);
    }
  } catch (error) {
    ElMessage.error('新增失败');
  }
};

const confirmDeleteResource = (item) => {
  ElMessageBox.confirm(`确定要删除“${item.name}”吗？此操作不可恢复。`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    const service = resourceTypeMap[currentOpenResourceType.value].service;
    try {
      await service.delete(item.id);
      ElMessage.success('删除成功');
      // Refresh list
      const response = await service.getAll(projectStore.currentProject.id);
      resourceList.value = response.data;
    } catch (error) {
      ElMessage.error('删除失败');
    }
  }).catch(() => {});
};

// Auto-save resource
const autoSaveResource = async () => {
  if (!currentResource.value || isSaving.value) return;
  
  try {
    isSaving.value = true;
    const { type, item } = currentResource.value;
    const service = resourceTypeMap[type].service;
    const id = type === 'worldview' ? projectStore.currentProject.id : item.id;
    await service.update(id, item);
    lastSaveTime.value = new Date();
    ElMessage.success({
      message: '自动保存成功',
      duration: 1000,
      showClose: false
    });
  } catch (error) {
    console.error('自动保存失败:', error);
  } finally {
    isSaving.value = false;
  }
};

// Manual save resource
const saveCurrentResource = async () => {
  if (!currentResource.value) return;
  
  try {
    isSaving.value = true;
    const { type, item } = currentResource.value;
    const service = resourceTypeMap[type].service;
    const id = type === 'worldview' ? projectStore.currentProject.id : item.id;
    await service.update(id, item);
    lastSaveTime.value = new Date();
    ElMessage.success('资源已保存');
  } catch (error) {
    ElMessage.error('保存资源失败');
  } finally {
    isSaving.value = false;
  }
};

const handleDeleteItem = ({ type, item }) => {
  ElMessageBox.confirm(`确定要删除“${item.name}”吗？此操作不可恢复。`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    const service = resourceTypeMap[type].service;
    try {
      await service.delete(item.id);
      ElMessage.success('删除成功');
      // If the deleted item is the one currently being edited, close it
      if (currentResource.value && currentResource.value.item.id === item.id) {
        currentResource.value = null;
      }
      // Refresh the sidebar list
      if (sidebarRef.value) {
        sidebarRef.value.refreshList(type);
      }
    } catch (error) {
      ElMessage.error('删除失败');
    }
  }).catch(() => {});
};

</script>

<style scoped>
.resource-view-container { padding: 20px; height: 100vh; display: flex; flex-direction: column; box-sizing: border-box; }
.no-project-selected { display: flex; justify-content: center; align-items: center; height: 100%; }
.content-header { margin-bottom: 20px; }
.content-main { flex: 1; display: flex; gap: 20px; height: calc(100vh - 100px); }
.sidebar { width: 240px; background-color: white; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); display: flex; flex-direction: column; }
.editor-area { flex: 1; background-color: white; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); display: flex; flex-direction: column; }
.resource-editor { height: 100%; display: flex; flex-direction: column; }
.editor-header { padding: 15px; border-bottom: 1px solid #e6e6e6; display: flex; justify-content: space-between; align-items: center; }
.title-input { width: 300px; }
.editor-content { flex: 1; padding: 15px; overflow: hidden; }
.empty-editor { display: flex; justify-content: center; align-items: center; height: 100%; }
.modal-summary { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>