<template>
  <div class="prompt-view-container">
    <!-- 未选择小说时的提示 -->
    <div v-if="!projectStore.currentProject" class="no-project-selected">
      <el-empty description="请先选择一个小说项目">
        <el-button type="primary" @click="goToNovels">选择小说</el-button>
      </el-empty>
    </div>

    <!-- 已选择小说时显示提示词管理 -->
    <template v-else>
      <div class="content-header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/novels' }">小说管理</el-breadcrumb-item>
          <el-breadcrumb-item>{{ projectStore.currentProject.title }}</el-breadcrumb-item>
          <el-breadcrumb-item>提示词管理</el-breadcrumb-item>
        </el-breadcrumb>
        <el-button type="primary" @click="handleAddNew" class="add-button">
          <svg viewBox="0 0 1024 1024" width="16" height="16">
            <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm192 472c0 4.4-3.6 8-8 8H544v152c0 4.4-3.6 8-8 8h-48c-4.4 0-8-3.6-8-8V544H328c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h152V328c0-4.4 3.6-8 8-8h48c4.4 0 8 3.6 8 8v152h152c4.4 0 8 3.6 8 8v48z" fill="currentColor"></path>
          </svg>
          新增提示词
        </el-button>
      </div>

    <div class="prompt-cards-container" v-loading="loading">
      <el-card 
        v-for="prompt in prompts" 
        :key="prompt.id" 
        class="prompt-card" 
        shadow="hover"
        @mouseenter="hoverCard = prompt.id"
        @mouseleave="hoverCard = null">
        <template #header>
          <div class="card-header">
            <div class="title-container">
              <span class="prompt-icon">{{ getPromptIcon(prompt.name) }}</span>
              <span class="prompt-name">{{ prompt.name }}</span>
            </div>
            <div class="card-actions" :class="{ 'visible': hoverCard === prompt.id }">
              <div 
                class="svg-button edit-button"
                @click="handleEdit(prompt)"
                title="编辑">
                <svg viewBox="0 0 1024 1024" width="16" height="16">
                  <path d="M827.2 169.6c-24.8-24.8-65.6-24.8-90.4 0L608 298.4l99.2 99.2 128.8-128.8c24.8-24.8 24.8-65.6 0-90.4zM589.6 316.8l-256 256-160 16V256L416 32l173.6 173.6-99.2 99.2z" fill="#409EFF"/>
                  <path d="M224 592l160-160 256 256-160 160L224 592z" fill="#409EFF"/>
                  <path d="M672 224l64 64 99.2-99.2-64-64-99.2 99.2z" fill="#409EFF"/>
                </svg>
              </div>
              <div 
                class="svg-button delete-button"
                @click="handleDelete(prompt)"
                title="删除">
                <svg viewBox="0 0 1024 1024" width="16" height="16">
                  <path d="M168 480h688c4.4 0 8-3.6 8-8v-32c0-4.4-3.6-8-8-8H168c-4.4 0-8 3.6-8 8v32c0 4.4 3.6 8 8 8z" fill="#F56C6C"/>
                  <path d="M368 704c0-4.4 3.6-8 8-8h272c4.4 0 8 3.6 8 8v32c0 4.4-3.6 8-8 8H376c-4.4 0-8-3.6-8-8v-32z" fill="#F56C6C"/>
                  <path d="M320 384v480c0 8.8 7.2 16 16 16h352c8.8 0 16-7.2 16-16V384c0-8.8-7.2-16-16-16H336c-8.8 0-16 7.2-16 16z" fill="#F56C6C"/>
                  <path d="M496 224h32c4.4 0 8-3.6 8-8v-32c0-4.4-3.6-8-8-8h-32c-4.4 0-8 3.6-8 8v32c0 4.4 3.6 8 8 8z" fill="#F56C6C"/>
                  <path d="M496 704c0-4.4 3.6-8 8-8h32c4.4 0 8 3.6 8 8v32c0 4.4-3.6 8-8 8h-32c-4.4 0-8-3.6-8-8v-32z" fill="#F56C6C"/>
                  <path d="M240 272c0-8.8 7.2-16 16-16h512c8.8 0 16 7.2 16 16s-7.2 16-16 16H256c-8.8 0-16-7.2-16-16z" fill="#F56C6C"/>
                </svg>
              </div>
            </div>
          </div>
        </template>
        <div class="card-content" @click="handleView(prompt)">
          <div class="content-preview">{{ prompt.content }}</div>
          <div class="view-more">点击查看详情</div>
        </div>
      </el-card>
      
      <!-- 空状态提示 -->
      <el-empty v-if="prompts.length === 0 && !loading" description="暂无提示词" class="empty-state">
        <el-button type="primary" @click="handleAddNew">创建第一个提示词</el-button>
      </el-empty>
    </div>

    <!-- Add/Edit/View Dialog -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="50%"
      :close-on-click-modal="false"
      class="prompt-dialog"
      destroy-on-close>
      <el-form :model="currentPrompt" label-position="top" class="prompt-form">
        <el-form-item label="名称">
          <el-input 
            v-model="currentPrompt.name" 
            :readonly="isViewing"
            placeholder="请输入提示词名称"
            clearable>
          </el-input>
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="currentPrompt.content"
            type="textarea"
            :rows="10"
            :readonly="isViewing"
            placeholder="请输入提示词内容，可使用{{变量名}}格式引用资源"
            ref="contentTextarea">
          </el-input>
          <el-dropdown
            v-if="!isViewing"
            trigger="click"
            @command="insertResourceReference"
            placement="top-start"
            popper-class="reference-dropdown-popper"
            style="margin-top: 8px;">
            <el-button type="primary" size="small">
              引用资源
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <div v-if="!projectStore.currentProject" class="reference-empty">请先选择项目</div>
                <template v-else>
                  <div v-if="resourceReferences.worldview" class="provider-group">
                    <div class="provider-group-title">世界观</div>
                    <el-dropdown-item command="世界观">世界观</el-dropdown-item>
                  </div>
                  <div v-if="resourceReferences.characters.length > 0" class="provider-group">
                    <div class="provider-group-title">角色</div>
                    <el-dropdown-item v-for="char in resourceReferences.characters" :key="char.id" :command="char.name">
                      {{ char.name }}
                    </el-dropdown-item>
                  </div>
                  <div v-if="resourceReferences.organizations.length > 0" class="provider-group">
                    <div class="provider-group-title">组织</div>
                    <el-dropdown-item v-for="org in resourceReferences.organizations" :key="org.id" :command="org.name">
                      {{ org.name }}
                    </el-dropdown-item>
                  </div>
                  <div v-if="resourceReferences.powers.length > 0" class="provider-group">
                    <div class="provider-group-title">超自然力量</div>
                    <el-dropdown-item v-for="power in resourceReferences.powers" :key="power.id" :command="power.name">
                      {{ power.name }}
                    </el-dropdown-item>
                  </div>
                  <div v-if="resourceReferences.weapons.length > 0" class="provider-group">
                    <div class="provider-group-title">武器</div>
                    <el-dropdown-item v-for="weapon in resourceReferences.weapons" :key="weapon.id" :command="weapon.name">
                      {{ weapon.name }}
                    </el-dropdown-item>
                  </div>
                  <div v-if="resourceReferences.dungeons.length > 0" class="provider-group">
                    <div class="provider-group-title">副本</div>
                    <el-dropdown-item v-for="dungeon in resourceReferences.dungeons" :key="dungeon.id" :command="dungeon.name">
                      {{ dungeon.name }}
                    </el-dropdown-item>
                  </div>
                </template>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-form-item>
      </el-form>
      <template #footer v-if="!isViewing">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useProjectStore } from '../stores/projectStore';
import { ElMessage, ElMessageBox } from 'element-plus';
// 图标已替换为SVG，无需导入Element Plus图标
import axios from 'axios';
import { worldviewService, characterService, organizationService, supernaturalPowerService, weaponService, dungeonService } from '../services/resourceService';

const API_URL = '/api';

const router = useRouter();
const projectStore = useProjectStore();

// 状态变量
const prompts = ref([]);
const dialogVisible = ref(false);
const isEditing = ref(false);
const isViewing = ref(false);
const currentPrompt = ref({});
const loading = ref(false);
const saving = ref(false);
const hoverCard = ref(null);
const contentTextarea = ref(null);

// 引用库数据
const resourceReferences = ref({
  worldview: null,
  characters: [],
  organizations: [],
  powers: [],
  weapons: [],
  dungeons: []
});

// 根据提示词名称获取图标
const getPromptIcon = (name) => {
  // 根据名称首字符或关键词返回对应的emoji图标
  if (!name) return '📝';
  
  const firstChar = name.charAt(0).toUpperCase();
  
  // 根据关键词匹配
  if (name.includes('创作') || name.includes('写作')) return '✍️';
  if (name.includes('角色') || name.includes('人物')) return '👤';
  if (name.includes('世界观') || name.includes('设定')) return '🌍';
  if (name.includes('情节') || name.includes('故事')) return '📖';
  if (name.includes('对话') || name.includes('交流')) return '💬';
  if (name.includes('描述') || name.includes('场景')) return '🏞️';
  
  // 根据首字母匹配
  const iconMap = {
    'A': '🅰️', 'B': '🅱️', 'C': '🇨', 'D': '🇩', 'E': '🇪', 'F': '🇫',
    'G': '🇬', 'H': '🇭', 'I': '🇮', 'J': '🇯', 'K': '🇰', 'L': '🇱',
    'M': '🇲', 'N': '🇳', 'O': '🅾️', 'P': '🇵', 'Q': '🇶', 'R': '🇷',
    'S': '🇸', 'T': '🇹', 'U': '🇺', 'V': '🇻', 'W': '🇼', 'X': '❌',
    'Y': '🇾', 'Z': '🇿', '0': '0️⃣', '1': '1️⃣', '2': '2️⃣',
    '3': '3️⃣', '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣',
    '8': '8️⃣', '9': '9️⃣'
  };
  
  return iconMap[firstChar] || '📝';
};

const dialogTitle = computed(() => {
  if (isViewing.value) return '查看提示词';
  return isEditing.value ? '编辑提示词' : '新增提示词';
});

const fetchPrompts = async () => {
  if (!projectStore.currentProject) {
    prompts.value = [];
    return;
  }

  loading.value = true;
  try {
    // 使用项目ID获取提示词
    const response = await axios.get(`${API_URL}/projects/${projectStore.currentProject.id}/prompt-templates`);
    prompts.value = response.data;
  } catch (error) {
    console.error('加载提示词列表失败:', error);
    ElMessage.error('加载提示词列表失败');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchPrompts();
  loadResourceReferences();
});

projectStore.$subscribe((mutation, state) => {
  if (state.currentProject) {
    fetchPrompts();
    loadResourceReferences();
  } else {
    prompts.value = [];
    resourceReferences.value = {
      worldview: null,
      characters: [],
      organizations: [],
      powers: [],
      weapons: [],
      dungeons: []
    };
  }
});

const goToNovels = () => {
  router.push('/novels');
};

// 加载引用库数据
const loadResourceReferences = async () => {
  if (!projectStore.currentProject) {
    resourceReferences.value = {
      worldview: null,
      characters: [],
      organizations: [],
      powers: [],
      weapons: [],
      dungeons: []
    };
    return;
  }

  try {
    const projectId = projectStore.currentProject.id;
    
    try {
      const worldviewRes = await worldviewService.get(projectId);
      resourceReferences.value.worldview = worldviewRes.data;
    } catch (e) {
      resourceReferences.value.worldview = null;
    }

    const [charsRes, orgsRes, powersRes, weaponsRes, dungeonsRes] = await Promise.all([
      characterService.getAll(projectId).catch(() => ({ data: [] })),
      organizationService.getAll(projectId).catch(() => ({ data: [] })),
      supernaturalPowerService.getAll(projectId).catch(() => ({ data: [] })),
      weaponService.getAll(projectId).catch(() => ({ data: [] })),
      dungeonService.getAll(projectId).catch(() => ({ data: [] }))
    ]);

    resourceReferences.value.characters = charsRes.data;
    resourceReferences.value.organizations = orgsRes.data;
    resourceReferences.value.powers = powersRes.data;
    resourceReferences.value.weapons = weaponsRes.data;
    resourceReferences.value.dungeons = dungeonsRes.data;
  } catch (error) {
    console.error('加载引用库失败:', error);
  }
};

// 插入资源引用
const insertResourceReference = (name) => {
  const textarea = contentTextarea.value?.$el?.querySelector('textarea');
  if (!textarea) return;

  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const text = currentPrompt.value.content || '';
  
  const insertText = `{{${name}}}`;
  currentPrompt.value.content = text.substring(0, start) + insertText + text.substring(end);
  
  setTimeout(() => {
    textarea.focus();
    textarea.setSelectionRange(start + insertText.length, start + insertText.length);
  }, 0);
};

const handleAddNew = () => {
  if (!projectStore.currentProject) {
    ElMessage.error('请先选择一个小说项目');
    return;
  }

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

  if (!projectStore.currentProject) {
    ElMessage.error('请先选择一个小说项目');
    return;
  }

  saving.value = true;
  const payload = {
    ...currentPrompt.value,
    // 关联到当前项目ID
    project_id: projectStore.currentProject.id
  };

  try {
    if (isEditing.value) {
      await axios.put(`${API_URL}/prompt-templates/${currentPrompt.value.id}`, payload);
    } else {
      await axios.post(`${API_URL}/prompt-templates`, payload);
    }
    ElMessage({
      message: '保存成功',
      type: 'success',
      duration: 2000
    });
    dialogVisible.value = false;
    fetchPrompts(); // Refresh list
  } catch (error) {
    console.error('保存失败:', error);
    ElMessage.error('保存失败');
  } finally {
    saving.value = false;
  }
};
</script>

<style scoped>
/* 主容器样式 */
.prompt-view-container {
  padding: 10px; /* Reduced padding to minimum needed */
  width: 100%;
  margin: 0;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* 页面标题样式 */
.page-title {
  display: flex;
  align-items: center;
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-title .el-icon, .page-title svg {
  margin-right: 10px;
  color: #409EFF;
  font-size: 28px;
  vertical-align: middle;
  height: 28px;
  width: 28px;
}

/* 头部样式 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 15px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 添加按钮样式 */
.add-button {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 20px;
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.add-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(64, 158, 255, 0.4);
}

.add-button .el-icon, .add-button svg {
  margin-right: 5px;
  font-size: 16px;
  height: 16px;
  width: 16px;
  vertical-align: middle;
}

/* 卡片容器样式 */
.prompt-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); /* Changed from 320px to 380px for wider cards */
  gap: 24px; /* Reset gap to original */
}

/* 卡片样式 */
.prompt-card {
  border-radius: 12px; /* Reset to original */
  transition: all 0.3s ease;
  overflow: hidden;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* Reset to original */
}

.prompt-card:hover {
  transform: translateY(-5px); /* Reset to original */
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); /* Reset to original */
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0; /* Reset to original */
}

.title-container {
  display: flex;
  align-items: center;
  flex: 1;
}

.prompt-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px; /* Reset to original size */
  height: 36px; /* Reset to original size */
  margin-right: 12px; /* Reset to original margin */
  font-size: 20px; /* Reset to original font size */
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.prompt-name {
  font-weight: 600;
  font-size: 16px; /* Reset to original font size */
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 卡片操作按钮样式 */
.card-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

/* Show actions when card is hovered */
.prompt-card:hover .card-actions {
  opacity: 1;
}

/* Show actions when visible class is applied */
.card-actions.visible {
  opacity: 1;
}

.svg-button {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: 8px;
}

.svg-button svg {
  width: 16px;
  height: 16px;
}

.edit-button {
  background-color: rgba(64, 158, 255, 0.15);
  border: 1px solid #409EFF;
}

.edit-button svg {
  color: #409EFF;
  fill: #409EFF;
}

.edit-button:hover {
  background-color: rgba(64, 158, 255, 0.25);
  transform: scale(1.1);
}

.delete-button {
  background-color: rgba(245, 108, 108, 0.15);
  border: 1px solid #F56C6C;
}

.delete-button svg {
  color: #F56C6C;
  fill: #F56C6C;
}

.delete-button:hover {
  background-color: rgba(245, 108, 108, 0.25);
  transform: scale(1.1);
}

/* 卡片内容样式 */
.card-content {
  height: 120px; /* Reset to original height */
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 15px 0; /* Reset to original padding */
  position: relative;
}

.content-preview {
  height: 100px; /* Reset to original height */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4; /* Reset to original number of lines */
  -webkit-box-orient: vertical;
  line-height: 1.6; /* Reset to original line height */
  color: #606266;
}

.view-more {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  text-align: center;
  color: #909399;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card-content:hover .view-more {
  opacity: 1;
}

/* 空状态样式 */
.empty-state {
  grid-column: 1 / -1;
  padding: 40px 0;
}

/* 对话框样式 */
.prompt-dialog {
  border-radius: 12px;
}

.prompt-dialog .el-dialog__header {
  background-color: #f5f7fa;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

.prompt-dialog .el-dialog__title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.prompt-dialog .el-dialog__body {
  padding: 24px;
}

.prompt-form .el-form-item__label {
  font-weight: 600;
  color: #303133;
}

.prompt-dialog .el-textarea__inner {
  font-family: 'Monaco', 'Courier New', monospace;
  line-height: 1.5;
}

.dialog-footer {
  padding: 15px 24px;
  background-color: #f5f7fa;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 下拉菜单分组标题样式 */
.provider-group-title {
  color: #909399;
  font-size: 12px;
  padding: 8px 20px 4px;
  font-weight: 600;
  pointer-events: none;
  user-select: none;
}

.provider-group:not(:first-child) .provider-group-title {
  margin-top: 8px;
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}

/* 引用库空状态 */
.reference-empty {
  padding: 12px 20px;
  color: #909399;
  font-size: 13px;
  text-align: center;
}

/* 引用库下拉菜单最大高度和滚动 */
.reference-dropdown-popper {
  max-height: 400px !important;
}

.reference-dropdown-popper .el-dropdown-menu {
  max-height: 400px !important;
  overflow-y: auto !important;
}

.prompt-card {
  animation: fadeIn 0.5s ease forwards;
}

.prompt-card:nth-child(1) { animation-delay: 0.1s; }
.prompt-card:nth-child(2) { animation-delay: 0.2s; }
.prompt-card:nth-child(3) { animation-delay: 0.3s; }
.prompt-card:nth-child(4) { animation-delay: 0.4s; }
.prompt-card:nth-child(5) { animation-delay: 0.5s; }
</style>
