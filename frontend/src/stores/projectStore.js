import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const currentProject = ref(null)
  const projects = ref([])

  // 计算属性
  const hasProject = computed(() => currentProject.value !== null)

  // 方法
  const setCurrentProject = (project) => {
    currentProject.value = project
  }

  const addProject = (project) => {
    projects.value.push(project)
    return project
  }

  const updateProject = (projectId, updatedData) => {
    const index = projects.value.findIndex(p => p.id === projectId)
    if (index !== -1) {
      projects.value[index] = { ...projects.value[index], ...updatedData }
      if (currentProject.value && currentProject.value.id === projectId) {
        currentProject.value = { ...currentProject.value, ...updatedData }
      }
      return projects.value[index]
    }
    return null
  }

  const deleteProject = (projectId) => {
    projects.value = projects.value.filter(p => p.id !== projectId)
    if (currentProject.value && currentProject.value.id === projectId) {
      currentProject.value = null
    }
  }

  return {
    // 状态
    currentProject,
    projects,

    // 计算属性
    hasProject,

    // 方法
    setCurrentProject,
    addProject,
    updateProject,
    deleteProject
  }
})
