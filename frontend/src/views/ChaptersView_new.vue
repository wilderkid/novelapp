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
          <el-tabs v-model="activeTab" type="card" closable @tab-remove="removeTab" @tab-click="handleTabClick" v-if="openChapters.length > 0">
            <el-tab-pane
              v-for="chapter in openChapters"
              :key="chapter.id"
              :label="chapter.title"
              :name="chapter.id.toString()"
            >
              <div class="chapter-editor">
                <div class="editor-header">
                  <el-input v-model="chapter.title" placeholder="章节标题" class="title-input" />
                  <div class="editor-actions">
                    <el-button @click="saveChapter(chapter)">保存</el-button>
                  </div>
                </div>
                <div class="editor-content">
                  <UEditorPlus 
                    :ref="(el) => editorRefs[chapter.id] = el"
                    v-model="chapter.content" 
                    :editor-id="`editor-${chapter.id}`"
                    @ready="onEditorReady"
                  />
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
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

// 打开章节（限制最多打开3个）
const openChapter = (chapter) => {
  // 检查是否已经打开
  const existingIndex = openChapters.value.findIndex(c => c.id === chapter.id)
  if (existingIndex > -1) {
    // 已打开，激活该标签页
    activeTab.value = chapter.id.toString()
    return
  }
  
  // 检查是否超过最大打开数量
  if (openChapters.value.length >= 3) {
    ElMessage.warning('最多只能同时打开3个章节进行编辑')
    return
  }
  
  // 添加到打开的章节列表
  openChapters.value.push({ ...chapter })
  activeTab.value = chapter.id.toString()
}

// 关闭标签页
const removeTab = (targetName) => {
  const index = openChapters.value.findIndex(c => c.id.toString() === targetName)
  if (index > -1) {
    openChapters.value.splice(index, 1)
    
    // 如果关闭的是当前激活的标签页，则激活另一个
    if (activeTab.value === targetName) {
      if (openChapters.value.length > 0) {
        activeTab.value = openChapters.value[Math.max(0, index - 1)].id.toString()
      } else {
        activeTab.value = ''
      }
    }
  }
}

// 格式化字数
const formatWordCount = (count) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万字'
  }
  return count + '字'
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

// 获取分卷下的章节
const getVolumeChapters = (volumeId) => {
  return chapters.value.filter(chapter => chapter.volumeId === volumeId)
}

// 查看分卷
const viewVolume = (volume) => {
  currentVolume.value = volume
  showVolumeDetailDialog.value = true
}

// 编辑分卷
const editVolume = (volume) => {
  isEditingVolume.value = true
  volumeForm.value = { ...volume }
  showVolumeDialog.value = true
}

// 保存分卷
const saveVolume = () => {
  if (!volumeForm.value.title) {
    ElMessage.warning('请填写分卷标题')
    return
  }

  if (isEditingVolume.value) {
    // 更新现有分卷
    const index = volumes.value.findIndex(v => v.id === volumeForm.value.id)
    if (index !== -1) {
      volumes.value[index] = { ...volumeForm.value }
      ElMessage.success('分卷信息已更新')
    }
  } else {
    // 创建新分卷
    const newVolume = {
      id: Date.now(), // 临时ID，实际应用中由后端生成
      ...volumeForm.value,
      chapterCount: 0,
      wordCount: 0
    }
    volumes.value.push(newVolume)
    ElMessage.success('分卷创建成功')
  }

  // 重置表单和关闭对话框
  resetVolumeForm()
  showVolumeDialog.value = false
}

// 确认删除分卷
const confirmDeleteVolume = (volume) => {
  ElMessageBox.confirm(
    `确定要删除分卷《${volume.title}》吗？此操作不可恢复！`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 删除分卷
    volumes.value = volumes.value.filter(v => v.id !== volume.id)
    // 同时删除该分卷下的所有章节
    chapters.value = chapters.value.filter(c => c.volumeId !== volume.id)
    ElMessage.success('分卷已删除')
  }).catch(() => {
    // 用户取消删除
  })
}

// 重置分卷表单
const resetVolumeForm = () => {
  volumeForm.value = {
    id: null,
    title: '',
    description: '',
    order: 1
  }
  isEditingVolume.value = false
}

// 向分卷添加章节
const addChapterToVolume = (volume) => {
  currentVolumeId.value = volume.id
  chapterForm.value.volumeId = volume.id
  showChapterDialog.value = true
}

// 编辑章节
const editChapter = (chapter) => {
  isEditingChapter.value = true
  chapterForm.value = { ...chapter }
  showChapterDialog.value = true
}

// 保存章节
const saveChapter = (chapter) => {
  if (!chapter.title) {
    ElMessage.warning('请填写章节标题')
    return
  }

  // 更新章节数据
  const index = chapters.value.findIndex(c => c.id === chapter.id)
  if (index !== -1) {
    chapters.value[index] = {
      ...chapters.value[index],
      ...chapter,
      updated_at: new Date().toISOString()
    }
    
    // 更新打开的章节数据
    const openIndex = openChapters.value.findIndex(c => c.id === chapter.id)
    if (openIndex > -1) {
      // 使用打开的章节数据更新，因为这里包含了最新的编辑内容
      chapters.value[index] = {
        ...chapters.value[index],
        ...openChapters.value[openIndex],
        updated_at: new Date().toISOString()
      }
    }
    
    ElMessage.success('章节已保存')
  }
}

// 保存章节表单
const saveChapterForm = () => {
  if (!chapterForm.value.title || !chapterForm.value.volumeId) {
    ElMessage.warning('请填写章节标题和所属分卷')
    return
  }

  if (isEditingChapter.value) {
    // 更新现有章节
    const index = chapters.value.findIndex(c => c.id === chapterForm.value.id)
    if (index !== -1) {
      chapters.value[index] = {
        ...chapters.value[index],
        ...chapterForm.value,
        volumeTitle: volumes.value.find(v => v.id === chapterForm.value.volumeId)?.title || '',
        updated_at: new Date().toISOString()
      }
      ElMessage.success('章节信息已更新')
    }
  } else {
    // 创建新章节
    const newChapter = {
      id: Date.now(), // 临时ID，实际应用中由后端生成
      ...chapterForm.value,
      volumeTitle: volumes.value.find(v => v.id === chapterForm.value.volumeId)?.title || '',
      content: '<p>请输入章节内容...</p>',
      wordCount: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    chapters.value.push(newChapter)
    ElMessage.success('章节创建成功')
    
    // 更新分卷的章节数
    const volume = volumes.value.find(v => v.id === chapterForm.value.volumeId)
    if (volume) {
      volume.chapterCount = (volume.chapterCount || 0) + 1
    }
  }

  // 重置表单和关闭对话框
  resetChapterForm()
  showChapterDialog.value = false
}

// 确认删除章节
const confirmDeleteChapter = (chapter) => {
  ElMessageBox.confirm(
    `确定要删除章节《${chapter.title}》吗？此操作不可恢复！`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 删除章节
    chapters.value = chapters.value.filter(c => c.id !== chapter.id)
    
    // 如果章节已打开，则关闭
    const openIndex = openChapters.value.findIndex(c => c.id === chapter.id)
    if (openIndex > -1) {
      removeTab(chapter.id.toString())
    }
    
    // 更新分卷的章节数
    const volume = volumes.value.find(v => v.id === chapter.volumeId)
    if (volume) {
      volume.chapterCount = Math.max(0, (volume.chapterCount || 0) - 1)
    }
    
    ElMessage.success('章节已删除')
  }).catch(() => {
    // 用户取消删除
  })
}

// 重置章节表单
const resetChapterForm = () => {
  chapterForm.value = {
    id: null,
    title: '',
    volumeId: currentVolumeId.value || null,
    order: 1
  }
  isEditingChapter.value = false
}





// 容器宽度调整方法
const initResize = () => {
  const resizeBar = document.querySelector('.resize-bar')
  if (!resizeBar) return
  
  resizeBar.addEventListener('mousedown', (e) => {
    isResizing.value = true
    startX.value = e.clientX
    startWidth.value = sidebarWidth.value
    
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    
    e.preventDefault()
  })
}

const handleMouseMove = (e) => {
  if (!isResizing.value) return
  
  const diff = e.clientX - startX.value
  const newWidth = startWidth.value + diff
  
  // 限制最小和最大宽度
  if (newWidth >= 200 && newWidth <= 500) {
    sidebarWidth.value = newWidth
  }
}

const handleMouseUp = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}



// 更新章节顺序
const updateChapterOrder = (volumeId) => {
  const volumeChapters = chapters.value
    .filter(c => c.volumeId === volumeId)
    .sort((a, b) => a.order - b.order)
  
  const treeElement = treeContainer.value.querySelector(`[data-id="volume-${volumeId}"] .el-tree-node__children`)
  if (!treeElement) return
  
  const chapterNodes = treeElement.querySelectorAll('.el-tree-node')
  
  chapterNodes.forEach((node, index) => {
    const nodeId = node.getAttribute('data-id')
    if (nodeId && nodeId.startsWith('chapter-')) {
      const chapterId = parseInt(nodeId.replace('chapter-', ''))
      const chapter = chapters.value.find(c => c.id === chapterId)
      if (chapter) {
        chapter.order = index + 1
      }
    }
  })
}

// 拖拽相关方法
const allowDrag = (draggingNode) => {
  // 只允许拖拽章节节点
  return draggingNode.data.type === 'chapter'
}

const allowDrop = (draggingNode, dropNode, type) => {
  // 只允许拖拽到章节列表中，不允许拖拽到分卷上
  if (type === 'inner') {
    return dropNode.data.type === 'volume'
  }
  return dropNode.data.type === 'chapter' || dropNode.data.type === 'volume'
}

const handleDragStart = (node, ev) => {
  // 设置拖拽样式
  ev.dataTransfer.effectAllowed = 'move'
}

const handleDragEnd = (draggingNode, dropNode, dropType, ev) => {
  if (!dropNode || dropType === null) return
  
  // 获取拖拽的章节ID
  const chapterId = parseInt(draggingNode.data.id.replace('chapter-', ''))
  
  // 获取目标分卷ID
  let targetVolumeId
  
  if (dropType === 'inner') {
    // 拖拽到分卷内部
    targetVolumeId = parseInt(dropNode.data.id.replace('volume-', ''))
  } else {
    // 拖拽到章节旁边
    const parentVolumeNode = dropNode.parent
    if (parentVolumeNode && parentVolumeNode.data.type === 'volume') {
      targetVolumeId = parseInt(parentVolumeNode.data.id.replace('volume-', ''))
    }
  }
  
  if (!targetVolumeId) return
  
  // 更新章节数据
  const chapter = chapters.value.find(c => c.id === chapterId)
  if (chapter) {
    // 如果分卷发生变化
    if (chapter.volumeId !== targetVolumeId) {
      // 更新旧分卷的章节数
      const oldVolume = volumes.value.find(v => v.id === chapter.volumeId)
      if (oldVolume) {
        oldVolume.chapterCount = Math.max(0, (oldVolume.chapterCount || 0) - 1)
      }
      
      // 更新新分卷的章节数
      const newVolume = volumes.value.find(v => v.id === targetVolumeId)
      if (newVolume) {
        newVolume.chapterCount = (newVolume.chapterCount || 0) + 1
      }
      
      // 更新章节所属分卷
      chapter.volumeId = targetVolumeId
      const volume = volumes.value.find(v => v.id === targetVolumeId)
      chapter.volumeTitle = volume ? volume.title : ''
    }
    
    // 更新章节顺序
    updateChapterOrder(targetVolumeId)
    
    ElMessage.success('章节位置已更新')
  }
}

// 编辑器准备就绪
const onEditorReady = (editor) => {
  // 编辑器准备就绪后的处理
  console.log('编辑器准备就绪', editor)
}

// 编辑器引用
const editorRefs = ref({})

// 标签页切换处理
const handleTabClick = (tab) => {
  // 强制刷新编辑器
  nextTick(() => {
    const chapterId = tab.props.name
    const editorRef = editorRefs.value[chapterId]
    if (editorRef) {
      editorRef.forceRefresh()
    }
  })
}

// 组件挂载时重置表单
onMounted(() => {
  resetVolumeForm()
  resetChapterForm()
  // 默认展开所有分卷
  expandedKeys.value = volumes.value.map(v => `volume-${v.id}`)
  
  // 初始化宽度调整
  nextTick(() => {
    initResize()
  })
})
</script>

<style scoped>
.chapters-container {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.content-header {
  margin-bottom: 20px;
}

.content-main {
  flex: 1;
  display: flex;
  gap: 20px;
  height: calc(100vh - 100px);
}

/* 左侧分卷和章节树形列表 */
.sidebar {
  min-width: 200px;
  max-width: 500px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 宽度调整条 */
.resize-bar {
  position: absolute;
  right: -5px;
  top: 0;
  bottom: 0;
  width: 10px;
  cursor: col-resize;
  z-index: 10;
  background-color: transparent;
}

.resize-bar:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.resize-bar:active {
  background-color: rgba(0, 0, 0, 0.2);
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.tree-container {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 8px;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-actions {
  display: none;
  gap: 4px;
}

.tree-node:hover .node-actions {
  display: flex;
}

/* 右侧编辑区域 */
.editor-area {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.chapter-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-content {
  flex: 1;
  overflow: hidden;
}

:deep(.el-tabs__content) {
  height: 100%;
}

:deep(.el-tab-pane) {
  height: 100%;
}

.editor-header {
  padding: 15px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-input {
  width: 300px;
}

.editor-content {
  flex: 1;
  padding: 15px;
}

.editor-container {
  height: 100%;
  width: 100%;
}

.empty-editor {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.no-project-selected {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.volume-detail {
  padding: 10px 0;
}

.volume-detail h3 {
  margin-top: 0;
  margin-bottom: 15px;
}

.volume-detail p {
  margin-bottom: 20px;
  color: #666;
}

.volume-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
}

.volume-detail h4 {
  margin-bottom: 10px;
}

/* 确保表格占满可用空间 */
:deep(.el-table) {
  width: 100% !important;
}

/* 确保表格容器占满可用空间 */
:deep(.el-table__body-wrapper) {
  width: 100% !important;
}

/* 树形组件样式调整 */
:deep(.el-tree-node__content) {
  height: 36px;
}

:deep(.el-tree-node__expand-icon) {
  padding: 6px;
}

/* 标签页样式调整 */
:deep(.el-tabs__content) {
  height: calc(100% - 40px);
}

:deep(.el-tab-pane) {
  height: 100%;
}

/* 拖拽相关样式 */
:deep(.el-tree-node__content) {
  transition: background-color 0.2s;
}

:deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}


:deep(.el-tree-node.is-drop-inner > .el-tree-node__content) {
  background-color: #e6f7ff;
  border: 1px dashed #1890ff;
  box-sizing: border-box;
}

:deep(.el-tree-node.is-drop-inner > .el-tree-node__content .el-tree-node__expand-icon) {
  color: #1890ff;
}
</style>
