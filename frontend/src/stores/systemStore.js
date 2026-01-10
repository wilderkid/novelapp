import { defineStore } from "pinia";
import { ref, watch } from "vue";

export const useSystemStore = defineStore("system", () => {
  // 从 localStorage 初始化 state
  const settings = ref(
    JSON.parse(localStorage.getItem("systemSettings")) || {
      proxyUrl: "",
      chatDefaults: {
        aiModelId: null,
        promptTemplateId: null,
        temperature: 0.7,
        maxTokens: 2000,
        memoryRounds: 10,
      },
      assistantDefaults: {
        aiModelId: null,
        promptTemplateId: null,
        temperature: 0.7,
        maxTokens: 2000,
        memoryRounds: 10,
      },
    },
  );

  // 监听 settings 的变化并将其保存到 localStorage
  watch(
    settings,
    (newSettings) => {
      localStorage.setItem("systemSettings", JSON.stringify(newSettings));
    },
    { deep: true },
  );

  // Action to update settings
  const updateSettings = (newSettings) => {
    settings.value = { ...settings.value, ...newSettings };
  };

  return {
    settings,
    updateSettings,
  };
});
