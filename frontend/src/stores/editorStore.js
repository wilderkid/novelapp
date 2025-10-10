import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useEditorStore = defineStore('editor', () => {
  // 状态
  const openChapters = ref([]) // 最多存储3个章节
  const maxOpenChapters = 3
  const activeChapterId = ref(null)

  // 计算属性
  const activeChapter = computed(() => {
    return openChapters.value.find(chapter => chapter.id === activeChapterId.value)
  })

  const isChapterOpen = computed(() => {
    return (chapterId) => openChapters.value.some(chapter => chapter.id === chapterId)
  })

  const canOpenMoreChapters = computed(() => {
    return openChapters.value.length < maxOpenChapters
  })

  // 方法
  const openChapter = (chapter) => {
    // 检查是否已达到最大打开章节数
    if (openChapters.value.length >= maxOpenChapters) {
      // 检查章节是否已经打开
      if (!isChapterOpen.value(chapter.id)) {
        return { success: false, message: `最多只能同时打开${maxOpenChapters}个章节，请先关闭一个章节` }
      }
    }

    // 如果章节未打开，则添加到打开列表
    if (!isChapterOpen.value(chapter.id)) {
      openChapters.value.push(chapter)
    }

    // 设置为活动章节
    activeChapterId.value = chapter.id

    return { success: true }
  }

  const closeChapter = (chapterId) => {
    openChapters.value = openChapters.value.filter(chapter => chapter.id !== chapterId)

    // 如果关闭的是当前活动章节，则切换到另一个打开的章节
    if (activeChapterId.value === chapterId && openChapters.value.length > 0) {
      activeChapterId.value = openChapters.value[0].id
    } else if (openChapters.value.length === 0) {
      activeChapterId.value = null
    }
  }

  const updateChapter = (chapterId, updatedData) => {
    const index = openChapters.value.findIndex(chapter => chapter.id === chapterId)
    if (index !== -1) {
      openChapters.value[index] = { ...openChapters.value[index], ...updatedData }
      return openChapters.value[index]
    }
    return null
  }

  const closeAllChapters = () => {
    openChapters.value = []
    activeChapterId.value = null
  }

  return {
    // 状态
    openChapters,
    activeChapterId,
    maxOpenChapters,

    // 计算属性
    activeChapter,
    isChapterOpen,
    canOpenMoreChapters,

    // 方法
    openChapter,
    closeChapter,
    updateChapter,
    closeAllChapters
  }
})
