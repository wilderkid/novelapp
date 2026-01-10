<template>
  <div class="page-header" :class="{ 'has-actions': $slots.actions }">
    <div class="header-content">
      <div class="header-title">
        <slot name="title">
          <h2 :class="{ compact: compact }">{{ title }}</h2>
        </slot>
      </div>
      <div v-if="$slots.actions || actions.length > 0" class="header-actions">
        <slot name="actions">
          <el-button
            v-for="action in actions"
            :key="action.text"
            :type="action.type || 'primary'"
            :icon="action.icon"
            :loading="action.loading"
            :disabled="action.disabled"
            @click="action.handler"
            size="default"
          >
            {{ action.text }}
          </el-button>
        </slot>
      </div>
    </div>
    <div v-if="$slots.filters" class="header-filters">
      <slot name="filters"></slot>
    </div>
  </div>
</template>

<script setup>
import { ElButton } from "element-plus";

defineProps({
  title: {
    type: String,
    default: "",
  },
  actions: {
    type: Array,
    default: () => [],
  },
  compact: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-title h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
}

.header-title h2.compact {
  font-size: var(--font-size-lg);
  margin-bottom: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.header-filters {
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .header-actions {
    justify-content: flex-end;
  }

  .header-title h2 {
    text-align: center;
  }
}
</style>
