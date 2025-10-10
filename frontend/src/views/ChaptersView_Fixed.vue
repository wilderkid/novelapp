<template>
  <div class="chapters-container">
    <!-- 未选择小说时的提示 -->
    <div v-if="!projectStore.currentProject" class="no-project-selected">
      <el-empty description="请先选择一个小说项目">
        <el-button type="primary" @click="goToNovels">选择小说</el-button>
      </el-empty>
    </div>

    <!-- 已选择小说时显示章节管理 -->
    <template v-else>
      <div class="content-header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/novels' }">小说管理</el-breadcrumb-item>
          <el-breadcrumb-item>{{ projectStore.currentProject.title }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <div class="content-main">
        <!-- 左侧分卷和章节树形列表 -->
        <div class="sidebar" :style="{ width: sidebarWidth + 'px' }">
          <div class="sidebar-header">
            <h3>分卷与章节</h3>
            <div class="sidebar-actions">
              <el-dropdown trigger="click">
                <el-button size="small" type="primary">
                  <el-icon><Plus /></el-icon>
                  新建
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="showVolumeDialog = true">新建分卷</el-dropdown-item>
                    <el-dropdown-item @click="showChapterDialog = true" :disabled="volumes.length === 0">新建章节</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
          <div class="tree-container" ref="treeContainer">
            <el-tree
              :data="volumeTreeData"
              node-key="id"
              :default-expanded-keys="expandedKeys"
              :expand-on-click-node="false"
              @node-click="handleNodeClick"
              draggable
              :allow-drag="allowDrag"
              :allow-drop="allowDrop"
              @node-drag-start="handleDragStart"
              @node-drag-end="handleDragEnd"
            >
              <template #default="{ node, data }">
                <div class="tree-node" :data-id="data.id">
                  <span class="node-label">{{ node.label }}</span>
                  <div class="node-actions" v-if="!data.isFolder || data.id !== 'root'">
                    <!-- 分卷操作按钮 -->
                    <template v-if="data.type === 'volume'">
                      <el-button size="small" text @click.stop="viewVolume(data)">
                        <el-icon><View /></el-icon>
                      </el-button>
                      <el-button size="small" text @click.stop="editVolume(data)">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                      <el-button size="small" text type="danger" @click.stop="confirmDeleteVolume(data)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                      <el-button size="small" text @click.stop="addChapterToVolume(data)">
                        <el-icon><Plus /></el-icon>
                      </el-button>
                    </template>
                    <!-- 章节操作按钮 -->
                    <template v-else-if="data.type === 'chapter'">
                      <el-button size="small" text @click.stop="openChapter(data.chapterData || data)">
                        <el-icon><View /></el-icon>
                      </el-button>
                      <el-button size="small" text type="danger" @click.stop="confirmDeleteChapter(data.chapterData || data)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </template>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
          <div class="resize-bar"></div>
        </div>

        <!-- 右侧编辑区域 -->
        <div class="editor-area">
          <div v-if="currentChapter" class="chapter-editor">
            <div class="editor-header">
              <el-input v-model="currentChapter.title" placeholder="章节标题" class="title-input" />
              <div class="editor-actions">
                <el-button @click="saveCurrentChapter">保存</el-button>
              </div>
            </div>
            <div class="editor-content">
              <UEditorPlus
                ref="editorRef"
                v-model="currentChapter.content"
                editor-id="chapter-editor"
                @ready="onEditorReady"
              />
            </div>
          </div>
          <div v-else class="empty-editor">
            <el-empty description="请从左侧选择一个章节开始编辑" />
          </div>
        </div>
      </div>

      <!-- 分卷对话框 -->
      <el-dialog
        v-model="showVolumeDialog"
        :title="isEditingVolume ? '编辑分卷' : '新建分卷'"
        width="500px"
      >
        <el-form :model="volumeForm" label-width="80px">
          <el-form-item label="分卷标题">
            <el-input v-model="volumeForm.title" placeholder="请输入分卷标题" />
          </el-form-item>
          <el-form-item label="分卷简介">
            <el-input v-model="volumeForm.description" type="textarea" rows="3" placeholder="请输入分卷简介" />
          </el-form-item>
          <el-form-item label="分卷序号">
            <el-input-number v-model="volumeForm.order" :min="1" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showVolumeDialog = false">取消</el-button>
            <el-button type="primary" @click="saveVolume">确定</el-button>
          </span>
        </template>
      </el-dialog>

      <!-- 章节对话框 -->
      <el-dialog
        v-model="showChapterDialog"
        :title="isEditingChapter ? '编辑章节' : '新建章节'"
        width="500px"
      >
        <el-form :model="chapterForm" label-width="80px">
          <el-form-item label="章节标题">
            <el-input v-model="chapterForm.title" placeholder="请输入章节标题" />
          </el-form-item>
          <el-form-item label="所属分卷">
            <el-select v-model="chapterForm.volumeId" placeholder="请选择分卷" style="width: 100%">
              <el-option
                v-for="volume in volumes"
                :key="volume.id"
                :label="volume.title"
                :value="volume.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="章节序号">
            <el-input-number v-model="chapterForm.order" :min="1" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showChapterDialog = false">取消</el-button>
            <el-button type="primary" @click="saveChapterForm">确定</el-button>
          </span>
        </template>
      </el-dialog>

      <!-- 分卷详情对话框 -->
      <el-dialog
        v-model="showVolumeDetailDialog"
        title="分卷详情"
        width="600px"
      >
        <div v-if="currentVolume" class="volume-detail">
          <h3>{{ currentVolume.title }}</h3>
          <p>{{ currentVolume.description }}</p>
          <div class="volume-stats">
            <el-statistic title="章节数" :value="currentVolume.chapterCount" />
            <el-statistic title="总字数" :value="currentVolume.wordCount" suffix="字" />
          </div>
          <h4>章节列表</h4>
          <el-table :data="getVolumeChapters(currentVolume.id)" style="width: 100%">
            <el-table-column prop="title" label="章节标题" />
            <el-table-column prop="wordCount" label="字数" width="100">
              <template #default="scope">
                {{ formatWordCount(scope.row.wordCount) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-dialog>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Edit, Delete } from '@element-plus/icons-vue'
import { useEditorStore } from '../stores/editorStore'
import { useProjectStore } from '../stores/projectStore'
import UEditorPlus from '../components/UEditorPlus_New.vue'


// 状态管理
const router = useRouter()
const editorStore = useEditorStore()
const projectStore = useProjectStore()

// 对话框状态
const showVolumeDialog = ref(false)
const showChapterDialog = ref(false)
const showVolumeDetailDialog = ref(false)
const isEditingVolume = ref(false)
const isEditingChapter = ref(false)

// 分卷表单
const volumeForm = ref({
  id: null,
  title: '',
  description: '',
  order: 1
})

// 章节表单
const chapterForm = ref({
  id: null,
  title: '',
  volumeId: null,
  order: 1
})

// 当前查看的分卷
const currentVolume = ref(null)

// 当前选中的分卷ID（用于新建章节）
const currentVolumeId = ref(null)

// 当前编辑的章节
const currentChapter = ref(null)

// 分卷数据
const volumes = ref([
  {
    id: 1,
    title: '第一卷：初入江湖',
    description: '主角初入江湖，结识伙伴，开始冒险旅程',
    order: 1,
    chapterCount: 2,
    wordCount: 11000
  },
  {
    id: 2,
    title: '第二卷：风云变幻',
    description: '江湖风波四起，主角面临重大考验',
    order: 2,
    chapterCount: 1,
    wordCount: 5500
  }
])

// 章节数据
const chapters = ref([
  {
    id: 1,
    title: '第一章：初出茅庐',
    content: '<p>这是第一章的内容...</p>',
    wordCount: 5000,
    volumeId: 1,
    volumeTitle: '第一卷：初入江湖',
    order: 1,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-02T00:00:00Z'
  },
  {
    id: 2,
    title: '第二章：奇遇',
    content: '<p>这是第二章的内容...</p>',
    wordCount: 6000,
    volumeId: 1,
    volumeTitle: '第一卷：初入江湖',
    order: 2,
    created_at: '2023-01-03T00:00:00Z',
    updated_at: '2023-01-04T00:00:00Z'
  },
  {
    id: 3,
    title: '第三章：危机四伏',
    content: '<p>这是第三章的内容...</p>',
    wordCount: 5500,
    volumeId: 2,
    volumeTitle: '第二卷：风云变幻',
    order: 1,
    created_at: '2023-02-01T00:00:00Z',
    updated_at: '2023-02-02T00:00:00Z'
  }
])

// 打开的章节数据（用于标签页）
const openChapters = ref([])
const activeTab = ref('')

// 树形展开的节点
const expandedKeys = ref([])

// 编辑器容器引用
const editorContainer = ref(null)

// 容器宽度调整
const sidebarWidth = ref(300)
const isResizing = ref(false)
const startX = ref(0)
const startWidth = ref(0)

// 拖动排序相关
const treeContainer = ref(null)

// 计算属性
// 构建树形数据
const volumeTreeData = computed(() => {
  const tree = []

  volumes.value.forEach(volume => {
    const volumeNode = {
      id: `volume-${volume.id}`,
      label: volume.title,
      type: 'volume',
      children: []
    }

    // 获取该分卷下的章节
    const volumeChapters = chapters.value
      .filter(chapter => chapter.volumeId === volume.id)
      .sort((a, b) => a.order - b.order)

    volumeChapters.forEach(chapter => {
      volumeNode.children.push({
        id: `chapter-${chapter.id}`,
        label: chapter.title,
        type: 'chapter',
        chapterData: chapter
      })
    })

    tree.push(volumeNode)
  })

  return tree
})

// 方法
const goToNovels = () => {
  router.push('/novels')
}

// 处理树节点点击
const handleNodeClick = (data) => {
  if (data.type === 'volume') {
    // 点击分卷，展开/折叠
    const volumeId = data.id
    const index = expandedKeys.value.indexOf(volumeId)
    if (index > -1) {
      expandedKeys.value.splice(index, 1)
    } else {
      expandedKeys.value.push(volumeId)
    }
  } else if (data.type === 'chapter') {
    // 点击章节，打开章节编辑
    openChapter(data.chapterData)
  }
}

// 打开章节
const openChapter = (chapter) => {
  // 直接设置当前编辑的章节
  currentChapter.value = { ...chapter }
}

// 保存当前章节
const saveCurrentChapter = () => {
  if (!currentChapter.value) return

  if (!currentChapter.value.title) {
    ElMessage.warning('请填写章节标题')
    return
  }

  // 更新章节数据
  const index = chapters.value.findIndex(c => c.id === currentChapter.value.id)
  if (index !== -1) {
    chapters.value[index] = {
      ...chapters.value[index],
      ...currentChapter.value,
      updated_at: new Date().toISOString()
    }
    ElMessage.success('章节已保存')
  }
}

// 关闭标签页
const removeTab = (targetName) => {
  const index = openChapters.value.findIndex(c => c.id.toString() === targetName)
  if (index > -1) {
    openChapters.value.splice(index, 1)

    // 如果关闭的是当前激活的标签页，则激活前一个或第一个标签页
    if (activeTab.value === targetName && openChapters.value.length > 0) {
      activeTab.value = openChapters.value[Math.max(0, index - 1)].id.toString()
    }
  }
}

// 获取分卷的章节数据
const getVolumeChapters = (volumeId) => {
  return chapters.value
    .filter(chapter => chapter.volumeId === volumeId)
    .sort((a, b) => a.order - b.order)
}

// 格式化字数显示
const formatWordCount = (count) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count.toString()
}

// 分卷相关方法
const viewVolume = (volume) => {
  // 从volume节点中提取原始分卷数据
  const volumeId = volume.id.replace('volume-', '')
  const volumeData = volumes.value.find(v => v.id == volumeId)
  if (volumeData) {
    currentVolume.value = volumeData
    showVolumeDetailDialog.value = true
  }
}

const editVolume = (volume) => {
  // 从volume节点中提取原始分卷数据
  const volumeId = volume.id.replace('volume-', '')
  const volumeData = volumes.value.find(v => v.id == volumeId)
  if (volumeData) {
    volumeForm.value = { ...volumeData }
    isEditingVolume.value = true
    showVolumeDialog.value = true
  }
}

const saveVolume = () => {
  if (!volumeForm.value.title) {
    ElMessage.warning('请填写分卷标题')
    return
  }

  if (isEditingVolume.value) {
    // 编辑模式
    const index = volumes.value.findIndex(v => v.id === volumeForm.value.id)
    if (index > -1) {
      volumes.value[index] = {
        ...volumes.value[index],
        ...volumeForm.value
      }
      ElMessage.success('分卷已更新')
    }
  } else {
    // 新建模式
    const newVolume = {
      ...volumeForm.value,
      id: Date.now(), // 简单生成唯一ID
      chapterCount: 0,
      wordCount: 0
    }
    volumes.value.push(newVolume)
    ElMessage.success('分卷已创建')
  }

  showVolumeDialog.value = false
  volumeForm.value = {
    id: null,
    title: '',
    description: '',
    order: 1
  }
  isEditingVolume.value = false
}

const confirmDeleteVolume = (volume) => {
  const volumeId = volume.id.replace('volume-', '')
  const volumeData = volumes.value.find(v => v.id == volumeId)
  if (volumeData) {
    ElMessageBox.confirm(
      `确定要删除分卷"${volumeData.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      // 检查分卷下是否有章节
      const hasChapters = chapters.value.some(chapter => chapter.volumeId == volumeId)
      if (hasChapters) {
        ElMessage.warning('该分卷下还有章节，请先删除所有章节')
        return
      }

      // 删除分卷
      const index = volumes.value.findIndex(v => v.id == volumeId)
      if (index > -1) {
        volumes.value.splice(index, 1)
        ElMessage.success('分卷已删除')
      }
    }).catch(() => {
      // 用户取消删除
    })
  }
}

const addChapterToVolume = (volume) => {
  const volumeId = volume.id.replace('volume-', '')
  chapterForm.value = {
    id: null,
    title: '',
    volumeId: parseInt(volumeId),
    order: 1
  }
  isEditingChapter.value = false
  showChapterDialog.value = true
}

// 章节相关方法
const saveChapterForm = () => {
  if (!chapterForm.value.title) {
    ElMessage.warning('请填写章节标题')
    return
  }

  if (isEditingChapter.value) {
    // 编辑模式
    const index = chapters.value.findIndex(c => c.id === chapterForm.value.id)
    if (index > -1) {
      chapters.value[index] = {
        ...chapters.value[index],
        ...chapterForm.value,
        updated_at: new Date().toISOString()
      }
      ElMessage.success('章节已更新')
    }
  } else {
    // 新建模式
    const volume = volumes.value.find(v => v.id === chapterForm.value.volumeId)
    const newChapter = {
      ...chapterForm.value,
      id: Date.now(), // 简单生成唯一ID
      content: '<p>请输入章节内容...</p>',
      wordCount: 0,
      volumeTitle: volume ? volume.title : '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    chapters.value.push(newChapter)

    // 更新分卷章节数
    if (volume) {
      volume.chapterCount++
    }

    ElMessage.success('章节已创建')
  }

  showChapterDialog.value = false
  chapterForm.value = {
    id: null,
    title: '',
    volumeId: null,
    order: 1
  }
  isEditingChapter.value = false
}

const confirmDeleteChapter = (chapter) => {
  ElMessageBox.confirm(
    `确定要删除章节"${chapter.title}"吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 删除章节
    const index = chapters.value.findIndex(c => c.id === chapter.id)
    if (index > -1) {
      chapters.value.splice(index, 1)

      // 更新分卷章节数
      const volume = volumes.value.find(v => v.id === chapter.volumeId)
      if (volume) {
        volume.chapterCount = Math.max(0, volume.chapterCount - 1)
      }

      ElMessage.success('章节已删除')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 编辑器相关
const editorRef = ref(null)

const onEditorReady = () => {
  // 编辑器准备就绪后的回调
  console.log('编辑器已准备就绪')
}

// 拖动排序相关
const allowDrag = (node) => {
  // 允许所有节点拖动
  return true
}

const allowDrop = (draggingNode, dropNode, type) => {
  // 只允许在同一分卷内移动章节，或者移动分卷
  if (draggingNode.data.type === 'volume' && dropNode.data.type === 'volume') {
    return type !== 'inner'
  }

  if (draggingNode.data.type === 'chapter' && dropNode.data.type === 'chapter') {
    return type !== 'inner'
  }

  return false
}

const handleDragStart = (node, event) => {
  // 拖动开始
  console.log('拖动开始', node.data)
}

const handleDragEnd = (draggingNode, dropNode, dropType, event) => {
  // 拖动结束
  console.log('拖动结束', draggingNode.data, dropNode?.data, dropType)

  if (!dropNode) return

  // 更新数据
  if (draggingNode.data.type === 'volume' && dropNode.data.type === 'volume') {
    // 分卷排序
    const dragVolumeId = parseInt(draggingNode.data.id.replace('volume-', ''))
    const dropVolumeId = parseInt(dropNode.data.id.replace('volume-', ''))

    const dragVolume = volumes.value.find(v => v.id === dragVolumeId)
    const dropVolume = volumes.value.find(v => v.id === dropVolumeId)

    if (dragVolume && dropVolume) {
      // 临时保存原始顺序
      const originalOrder = dragVolume.order

      if (dropType === 'before') {
        dragVolume.order = dropVolume.order
        // 更新中间分卷的序号
        volumes.value.forEach(volume => {
          if (volume.id !== dragVolumeId && 
              volume.order >= dragVolume.order && 
              volume.order < originalOrder) {
            volume.order++
          }
        })
      } else if (dropType === 'after') {
        dragVolume.order = dropVolume.order + 1
        // 更新中间分卷的序号
        volumes.value.forEach(volume => {
          if (volume.id !== dragVolumeId && 
              volume.order > originalOrder && 
              volume.order <= dragVolume.order) {
            volume.order--
          }
        })
      }

      // 重新排序
      volumes.value.sort((a, b) => a.order - b.order)
    }
  } else if (draggingNode.data.type === 'chapter' && dropNode.data.type === 'chapter') {
    // 章节排序
    const dragChapterId = parseInt(draggingNode.data.id.replace('chapter-', ''))
    const dropChapterId = parseInt(dropNode.data.id.replace('chapter-', ''))

    const dragChapter = chapters.value.find(c => c.id === dragChapterId)
    const dropChapter = chapters.value.find(c => c.id === dropChapterId)

    if (dragChapter && dropChapter && dragChapter.volumeId === dropChapter.volumeId) {
      // 临时保存原始顺序
      const originalOrder = dragChapter.order

      if (dropType === 'before') {
        dragChapter.order = dropChapter.order
        // 更新中间章节的序号
        chapters.value.forEach(chapter => {
          if (chapter.id !== dragChapterId && 
              chapter.volumeId === dragChapter.volumeId &&
              chapter.order >= dragChapter.order && 
              chapter.order < originalOrder) {
            chapter.order++
          }
        })
      } else if (dropType === 'after') {
        dragChapter.order = dropChapter.order + 1
        // 更新中间章节的序号
        chapters.value.forEach(chapter => {
          if (chapter.id !== dragChapterId && 
              chapter.volumeId === dragChapter.volumeId &&
              chapter.order > originalOrder && 
              chapter.order <= dragChapter.order) {
            chapter.order--
          }
        })
      }

      // 重新排序
      chapters.value.sort((a, b) => {
        if (a.volumeId !== b.volumeId) {
          return a.volumeId - b.volumeId
        }
        return a.order - b.order
      })
    }
  }
}

// 生命周期钩子
onMounted(() => {
  // 初始化展开第一个分卷
  if (volumes.value.length > 0) {
    expandedKeys.value.push(`volume-${volumes.value[0].id}`)
  }

  // 设置侧边栏拖动调整宽度
  const resizeBar = document.querySelector('.resize-bar')
  if (resizeBar) {
    resizeBar.addEventListener('mousedown', (e) => {
      isResizing.value = true
      startX.value = e.clientX
      startWidth.value = sidebarWidth.value

      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    })
  }
})

const handleMouseMove = (e) => {
  if (!isResizing.value) return

  const diff = e.clientX - startX.value
  sidebarWidth.value = Math.max(200, Math.min(600, startWidth.value + diff))
}

const handleMouseUp = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}
</script>

<style scoped>
.chapters-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.no-project-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.content-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.content-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
}

.tree-container {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  border-radius: 4px;
}

.tree-node:hover {
  background-color: #f0f9ff;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.resize-bar {
  width: 4px;
  height: 100%;
  background-color: #dcdfe6;
  cursor: col-resize;
  position: relative;
}

.resize-bar:hover {
  background-color: #c0c4cc;
}

.editor-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.chapter-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-input {
  flex: 1;
}

.editor-content {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.empty-editor {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.volume-detail {
  padding: 16px;
}

.volume-stats {
  display: flex;
  gap: 40px;
  margin: 16px 0;
}
</style>
