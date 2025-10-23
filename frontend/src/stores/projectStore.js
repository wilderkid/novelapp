import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useProjectStore = defineStore('project', () => {
  // 状态：尝试从localStorage恢复currentProject
  const savedProject = localStorage.getItem('currentProject');
  const currentProject = ref(savedProject ? JSON.parse(savedProject) : null);
  const projects = ref([]);

  // 计算属性
  const hasProject = computed(() => currentProject.value !== null);

  // 方法
  const setCurrentProject = (project) => {
    currentProject.value = project;
    if (project) {
      localStorage.setItem('currentProject', JSON.stringify(project));
    } else {
      localStorage.removeItem('currentProject');
    }
  };

  const addProject = (project) => {
    projects.value.push(project);
    return project;
  };

  const updateProject = (projectId, updatedData) => {
    const index = projects.value.findIndex(p => p.id === projectId);
    if (index !== -1) {
      projects.value[index] = { ...projects.value[index], ...updatedData };
      if (currentProject.value && currentProject.value.id === projectId) {
        // 更新持久化的状态
        setCurrentProject({ ...currentProject.value, ...updatedData });
      }
      return projects.value[index];
    }
    return null;
  };

  const deleteProject = (projectId) => {
    projects.value = projects.value.filter(p => p.id !== projectId);
    if (currentProject.value && currentProject.value.id === projectId) {
      // 清除持久化的状态
      setCurrentProject(null);
    }
  };

  // 监听currentProject的变化并更新localStorage
  watch(currentProject, (newProject) => {
    if (newProject) {
      localStorage.setItem('currentProject', JSON.stringify(newProject));
    } else {
      localStorage.removeItem('currentProject');
    }
  }, { deep: true });

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