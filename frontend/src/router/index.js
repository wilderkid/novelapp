import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/novels'
    },
    {
      path: '/novels',
      name: 'novels',
      component: () => import('../views/NovelsView.vue')
    },
    {
      path: '/chapters',
      name: 'chapters',
      component: () => import('../views/ChaptersView.vue')
    },
    {
      path: '/resources',
      name: 'resources',
      component: () => import('../views/ResourceView.vue')
    },
    {
      path: '/prompts',
      name: 'prompts',
      component: () => import('../views/PromptView.vue')
    },
    {
      path: '/ai-management',
      name: 'ai-management',
      component: () => import('@/views/AIManagerView.vue')
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('@/views/ChatView.vue')
    },
    {
      path: '/system',
      name: 'system',
      component: () => import('@/views/SystemSettingsView.vue')
    }
  ]
})

export default router
