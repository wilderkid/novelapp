<template>
  <div class="resource-list">
    <ul>
      <li v-for="item in items" :key="item.id">
        <span class="item-name" @click="selectItem(item)">{{ item.name }}</span>
        <el-icon class="delete-icon" @click.stop="deleteItem(item)"><Delete /></el-icon>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { Delete } from '@element-plus/icons-vue';

const props = defineProps({
  resourceType: {
    type: String,
    required: true,
  },
  projectId: {
    type: Number,
    required: true,
  },
  service: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['item-selected', 'delete-item']);

const items = ref([]);

const fetchItems = async () => {
  if (!props.projectId || !props.service) return;
  try {
    const response = await props.service.getAll(props.projectId);
    items.value = response.data;
  } catch (error) {
    console.error(`Failed to fetch ${props.resourceType}:`, error);
  }
};

const selectItem = (item) => {
  emit('item-selected', { type: props.resourceType, item });
};

const deleteItem = (item) => {
  emit('delete-item', { type: props.resourceType, item });
};

// Expose fetchItems to be called from parent
defineExpose({ fetchItems });

onMounted(fetchItems);
watch(() => props.projectId, fetchItems);

</script>

<style scoped>
.resource-list ul {
  list-style: none;
  padding: 0 0 0 20px; /* Indent the list */
}
.resource-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 0.9em;
}
.resource-list li:hover {
  background-color: #f0f0f0;
}
.item-name {
  flex-grow: 1;
}
.delete-icon {
  visibility: hidden; /* Hide by default */
  cursor: pointer;
  color: #F56C6C;
}
.resource-list li:hover .delete-icon {
  visibility: visible; /* Show on hover */
}
</style>
