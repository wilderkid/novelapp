import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useEditorStore = defineStore("editor", () => {
  // 状态
  const openChapters = ref([]); // 最多存储3个章节
  const maxOpenChapters = 3;
  const activeChapterId = ref(null);
  const activeEditorInstance = ref(null); // 新增：存储当前激活的编辑器实例
  const creativeAssistantVisible = ref(false); // 新增：控制AI助手侧边栏的显示与隐藏
  const cachedSelectedText = ref(""); // 新增：缓存编辑器中选中的文字

  // 计算属性
  const activeChapter = computed(() => {
    return openChapters.value.find(
      (chapter) => chapter.id === activeChapterId.value,
    );
  });

  const isChapterOpen = computed(() => {
    return (chapterId) =>
      openChapters.value.some((chapter) => chapter.id === chapterId);
  });

  const canOpenMoreChapters = computed(() => {
    return openChapters.value.length < maxOpenChapters;
  });

  // 方法
  const openChapter = (chapter) => {
    if (
      openChapters.value.length >= maxOpenChapters &&
      !isChapterOpen.value(chapter.id)
    ) {
      return {
        success: false,
        message: `最多只能同时打开${maxOpenChapters}个章节，请先关闭一个章节`,
      };
    }

    if (!isChapterOpen.value(chapter.id)) {
      openChapters.value.push(chapter);
    }

    activeChapterId.value = chapter.id;
    return { success: true };
  };

  const closeChapter = (chapterId) => {
    const index = openChapters.value.findIndex((c) => c.id === chapterId);
    if (index > -1) {
      openChapters.value.splice(index, 1);
    }

    if (activeChapterId.value === chapterId) {
      if (openChapters.value.length > 0) {
        activeChapterId.value =
          openChapters.value[openChapters.value.length - 1].id;
      } else {
        activeChapterId.value = null;
        clearActiveEditorInstance(); // 新增：没有打开的章节时，清除编辑器实例
      }
    }
  };

  const setActiveChapter = (chapterId) => {
    activeChapterId.value = chapterId;
  };

  const updateChapter = (chapterId, updatedData) => {
    const index = openChapters.value.findIndex(
      (chapter) => chapter.id === chapterId,
    );
    if (index !== -1) {
      openChapters.value[index] = {
        ...openChapters.value[index],
        ...updatedData,
      };
      return openChapters.value[index];
    }
    return null;
  };

  const closeAllChapters = () => {
    openChapters.value = [];
    activeChapterId.value = null;
    clearActiveEditorInstance(); // 新增：关闭所有章节时，清除编辑器实例
  };

  // --- 新增：AI助手与编辑器交互 ---

  // 设置当前激活的编辑器实例
  const setActiveEditorInstance = (editorInstance) => {
    activeEditorInstance.value = editorInstance;
  };

  // 清除编辑器实例
  const clearActiveEditorInstance = () => {
    activeEditorInstance.value = null;
  };

  // 向当前激活的编辑器插入内容
  const insertContent = (content) => {
    if (
      activeEditorInstance.value &&
      typeof activeEditorInstance.value.execCommand === "function"
    ) {
      activeEditorInstance.value.execCommand("insertHtml", content);
      return { success: true };
    }
    return { success: false, message: "没有检测到活动的编辑器" };
  };

  // 获取编辑器中选中的文字（返回缓存的文字）
  const getSelectedText = () => {
    return cachedSelectedText.value;
  };

  // 更新缓存的选中文字
  const updateCachedSelectedText = (text) => {
    cachedSelectedText.value = text;
  };

  // 清除缓存的选中文字
  const clearCachedSelectedText = () => {
    cachedSelectedText.value = "";
  };

  // 切换AI助手侧边栏的可见性
  const toggleCreativeAssistant = () => {
    creativeAssistantVisible.value = !creativeAssistantVisible.value;
  };

  return {
    // 状态
    openChapters,
    activeChapterId,
    maxOpenChapters,
    activeEditorInstance, // 新增
    creativeAssistantVisible, // 新增
    cachedSelectedText, // 新增

    // 计算属性
    activeChapter,
    isChapterOpen,
    canOpenMoreChapters,

    // 方法
    openChapter,
    closeChapter,
    setActiveChapter,
    updateChapter,
    closeAllChapters,

    // 新增方法
    setActiveEditorInstance,
    clearActiveEditorInstance,
    insertContent,
    getSelectedText,
    updateCachedSelectedText,
    clearCachedSelectedText,
    toggleCreativeAssistant,
  };
});
