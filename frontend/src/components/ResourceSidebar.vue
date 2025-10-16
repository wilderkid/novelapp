<template>
  <div class="resource-sidebar">
    <div v-for="resource in resources" :key="resource.type" class="resource-category">
      <div class="category-header" @click="handleCategoryClick(resource)">
        <el-icon v-if="resource.type !== 'worldview'" class="expand-icon" :class="{ expanded: expandedState[resource.type] }">
          <ArrowRight />
        </el-icon>
        <span class="category-name">{{ resource.emoji }} {{ resource.name }}</span>
        <div class="actions" v-if="resource.type !== 'worldview'">
          <el-icon class="action-icon" @click.stop="emit('open-summary-modal', resource.type)"><InfoFilled /></el-icon>
          <el-icon class="action-icon" @click.stop="emit('open-add-modal', resource.type)"><Plus /></el-icon>
        </div>
      </div>
      <div v-if="expandedState[resource.type]">
        <resource-list 
          :ref="el => listRefs[resource.type] = el"
          :resource-type="resource.type" 
          :project-id="projectId"
          :service="resource.service"
          @item-selected="onItemSelected"
          @delete-item="onItemDeleted"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useProjectStore } from '../stores/projectStore';
import { ArrowRight, InfoFilled, Plus } from '@element-plus/icons-vue';
import ResourceList from './ResourceList.vue';
import { characterService, organizationService, supernaturalPowerService, weaponService, dungeonService, worldviewService } from '../services/resourceService';

const projectStore = useProjectStore();
const projectId = computed(() => projectStore.currentProject?.id);

const emit = defineEmits(['open-summary-modal', 'open-editor', 'item-selected', 'open-add-modal', 'delete-item']);

const resources = ref([
  { type: 'worldview', name: '世界观', emoji: '🌍', service: worldviewService },
  { type: 'rpg_characters', name: '角色', emoji: '👤', service: characterService },
  { type: 'organizations', name: '组织', emoji: '🏛️', service: organizationService },
  { type: 'supernatural_powers', name: '超凡之力', emoji: '✨', service: supernaturalPowerService },
  { type: 'weapons', name: '兵器', emoji: '⚔️', service: weaponService },
  { type: 'dungeons', name: '副本', emoji: '🗺️', service: dungeonService },
]);

const expandedState = ref({});
const listRefs = ref({});

const toggleExpand = (type) => {
  if (type === 'worldview') return;
  expandedState.value[type] = !expandedState.value[type];
};

const handleCategoryClick = (resource) => {
  if (resource.type === 'worldview') {
    emit('open-editor', resource);
  } else {
    toggleExpand(resource.type);
  }
};

const onItemSelected = (payload) => {
  emit('item-selected', payload);
};

const onItemDeleted = (payload) => {
  emit('delete-item', payload);
};

const refreshList = (resourceType) => {
  const listComponent = listRefs.value[resourceType];
  if (listComponent) {
    listComponent.fetchItems();
  }
};

defineExpose({ refreshList });

</script>

<style scoped>
.resource-sidebar { padding: 10px; }
.category-header { display: flex; align-items: center; cursor: pointer; padding: 8px 12px; border-radius: 4px; transition: background-color 0.2s; }
.category-header:hover { background-color: #f5f7fa; }
.expand-icon { margin-right: 8px; transition: transform 0.2s; }
.expand-icon.expanded { transform: rotate(90deg); }
.category-name { flex-grow: 1; }
.actions { display: flex; align-items: center; gap: 8px; }
.action-icon { cursor: pointer; color: #606266; }
.action-icon:hover { color: #409eff; }
</style>
