import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAIStore = defineStore("ai", () => {
  // 状态
  const aiConfigs = ref([]);
  const promptTemplates = ref([]);

  // 计算属性
  const defaultAIConfig = computed(() => {
    return aiConfigs.value.find((config) => config.is_default);
  });

  const defaultPromptTemplate = computed(() => {
    return promptTemplates.value.find((template) => template.is_default);
  });

  const promptTemplatesByCategory = computed(() => {
    const categories = {};
    promptTemplates.value.forEach((template) => {
      if (!categories[template.category]) {
        categories[template.category] = [];
      }
      categories[template.category].push(template);
    });
    return categories;
  });

  // 方法
  const setAIConfigs = (configs) => {
    aiConfigs.value = configs;
  };

  const addAIConfig = (config) => {
    aiConfigs.value.push(config);
    return config;
  };

  const updateAIConfig = (configId, updatedData) => {
    const index = aiConfigs.value.findIndex((config) => config.id === configId);
    if (index !== -1) {
      aiConfigs.value[index] = { ...aiConfigs.value[index], ...updatedData };
      return aiConfigs.value[index];
    }
    return null;
  };

  const deleteAIConfig = (configId) => {
    aiConfigs.value = aiConfigs.value.filter(
      (config) => config.id !== configId,
    );
  };

  const setPromptTemplates = (templates) => {
    promptTemplates.value = templates;
  };

  const addPromptTemplate = (template) => {
    promptTemplates.value.push(template);
    return template;
  };

  const updatePromptTemplate = (templateId, updatedData) => {
    const index = promptTemplates.value.findIndex(
      (template) => template.id === templateId,
    );
    if (index !== -1) {
      promptTemplates.value[index] = {
        ...promptTemplates.value[index],
        ...updatedData,
      };
      return promptTemplates.value[index];
    }
    return null;
  };

  const deletePromptTemplate = (templateId) => {
    promptTemplates.value = promptTemplates.value.filter(
      (template) => template.id !== templateId,
    );
  };

  return {
    // 状态
    aiConfigs,
    promptTemplates,

    // 计算属性
    defaultAIConfig,
    defaultPromptTemplate,
    promptTemplatesByCategory,

    // 方法
    setAIConfigs,
    addAIConfig,
    updateAIConfig,
    deleteAIConfig,
    setPromptTemplates,
    addPromptTemplate,
    updatePromptTemplate,
    deletePromptTemplate,
  };
});
