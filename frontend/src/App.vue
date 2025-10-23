<template>
  <el-container class="app-container">
    <el-container class="main-layout-container">
      <el-aside :width="isSidebarCollapsed ? '65px' : '200px'" class="sidebar">
        <el-menu
          default-active="1"
          class="sidebar-menu"
          :collapse="isSidebarCollapsed"
          @select="handleMenuSelect"
        >
          <el-menu-item index="1">
            <el-icon><Reading /></el-icon>
            <template #title><span>小说管理</span></template>
          </el-menu-item>
          <el-menu-item index="2">
            <el-icon><Document /></el-icon>
            <template #title><span>章节管理</span></template>
          </el-menu-item>
          <el-menu-item index="3">
            <el-icon><Collection /></el-icon>
            <template #title><span>资源管理</span></template>
          </el-menu-item>
          <el-menu-item index="4">
            <el-icon><MagicStick /></el-icon>
            <template #title><span>提示词管理</span></template>
          </el-menu-item>
          <el-menu-item index="5">
            <el-icon><Cpu /></el-icon>
            <template #title><span>AI 管理</span></template>
          </el-menu-item>
          <el-menu-item index="6">
            <el-icon><ChatDotRound /></el-icon>
            <template #title><span>AI 对话</span></template>
          </el-menu-item>
          <el-menu-item index="7">
            <el-icon><Opportunity /></el-icon>
            <template #title><span>创作助手</span></template>
          </el-menu-item>
        </el-menu>
        <div class="sidebar-toggle" @click="toggleSidebar">
          <el-icon>
            <Fold v-if="!isSidebarCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
      </el-aside>
      <el-main class="main-content">
        <router-view />
      </el-main>
      <CreativeAssistant v-if="editorStore.creativeAssistantVisible" />
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Document, MagicStick, Reading, Collection, Fold, Expand, Cpu, ChatDotRound, Opportunity } from '@element-plus/icons-vue'
import { useEditorStore } from './stores/editorStore';
import CreativeAssistant from './components/CreativeAssistant.vue';

const router = useRouter()
const editorStore = useEditorStore();
const isSidebarCollapsed = ref(false)

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const handleMenuSelect = (index) => {
  switch (index) {
    case '1':
      router.push('/novels')
      break
    case '2':
      router.push('/chapters')
      break
    case '3':
      router.push('/resources')
      break
    case '4':
      router.push('/prompts')
      break
    case '5':
      router.push('/ai-management')
      break
    case '6':
      router.push('/chat')
      break
    case '7':
      editorStore.toggleCreativeAssistant();
      break;
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
}

.main-layout-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #e6e6e6;
  position: relative;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar-menu {
  flex-grow: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-toggle {
  flex-shrink: 0;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #606266;
  border-top: 1px solid #e6e6e6;
}

.sidebar-toggle:hover {
  background-color: #f0f0f0;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}
</style>