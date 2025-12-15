<template>
  <el-container class="app-container" role="main" aria-label="主要应用容器">
    <el-container class="main-layout-container">
      <el-aside :width="isSidebarCollapsed ? '65px' : '200px'" class="sidebar" role="navigation" aria-label="主要导航">
        <el-menu
          default-active="1"
          class="sidebar-menu"
          :collapse="isSidebarCollapsed"
          @select="handleMenuSelect"
          role="menubar"
          aria-label="主要导航菜单"
        >
          <el-menu-item index="1" role="menuitem" tabindex="0">
            <el-icon><Reading /></el-icon>
            <template #title><span>小说管理</span></template>
          </el-menu-item>
          <el-menu-item index="2" role="menuitem" tabindex="0">
            <el-icon><Document /></el-icon>
            <template #title><span>章节管理</span></template>
          </el-menu-item>
          <el-menu-item index="3" role="menuitem" tabindex="0">
            <el-icon><Collection /></el-icon>
            <template #title><span>资源管理</span></template>
          </el-menu-item>
          <el-menu-item index="4" role="menuitem" tabindex="0">
            <el-icon><MagicStick /></el-icon>
            <template #title><span>提示词管理</span></template>
          </el-menu-item>
          <el-menu-item index="5" role="menuitem" tabindex="0">
            <el-icon><Cpu /></el-icon>
            <template #title><span>AI 管理</span></template>
          </el-menu-item>
          <el-menu-item index="6" role="menuitem" tabindex="0">
            <el-icon><ChatDotRound /></el-icon>
            <template #title><span>AI 对话</span></template>
          </el-menu-item>
          <el-menu-item index="7" role="menuitem" tabindex="0">
            <el-icon><Opportunity /></el-icon>
            <template #title><span>创作助手</span></template>
          </el-menu-item>
          <el-menu-item index="8" role="menuitem" tabindex="0">
            <el-icon><Setting /></el-icon>
            <template #title><span>系统管理</span></template>
          </el-menu-item>

        </el-menu>
        <div
          class="sidebar-toggle" 
          @click="toggleSidebar"
          role="button"
          tabindex="0"
          @keydown.enter="toggleSidebar"
          @keydown.space="toggleSidebar"
          :aria-label="isSidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
        >
          <el-icon>
            <Fold v-if="!isSidebarCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
      </el-aside>
      <el-main class="main-content" role="main" aria-label="主要内容区域">
        <transition name="fade" mode="out-in">
          <router-view />
        </transition>
      </el-main>
      <CreativeAssistant 
        v-if="editorStore.creativeAssistantVisible" 
        :aria-hidden="!editorStore.creativeAssistantVisible"
      />
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Document, MagicStick, Reading, Collection, Fold, Expand, Cpu, ChatDotRound, Opportunity, Setting } from '@element-plus/icons-vue'
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
    case '8':
      router.push('/system')
      break
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  background-color: #f5f7fa;
}

.main-layout-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  position: relative;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0,0,0,0.05);
  z-index: 100;
}

.sidebar-menu {
  flex-grow: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #fff;
}

.sidebar-toggle {
  flex-shrink: 0;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #606266;
  border-top: 1px solid #e6e6e6;
  background-color: #f5f7fa;
  transition: background-color 0.3s;
}

.sidebar-toggle:hover {
  background-color: #e6e6e6;
  color: #303133;
}

.main-content {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
  background-color: #f5f7fa;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    height: 100vh;
    z-index: 99;
  }
  
  .main-content {
    padding: 12px;
  }
}
</style>