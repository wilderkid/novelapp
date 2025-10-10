<template>
  <div class="novels-container">
    <div class="novels-header">
      <h2>小说管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建小说
      </el-button>
    </div>

    <div class="novels-content">
      <el-table :data="novels" style="width: 100%" table-layout="fixed">
        <el-table-column prop="title" label="小说标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="genre" label="类型" width="80" />
        <el-table-column prop="author" label="作者" width="100" />
        <el-table-column prop="wordCount" label="字数" width="90">
          <template #default="scope">
            {{ formatWordCount(scope.row.wordCount || scope.row.word_count || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="chapterCount" label="章节数" width="80">
          <template #default="scope">
            {{ scope.row.chapterCount || scope.row.chapter_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="170">
          <template #default="scope">
            {{ formatDate(scope.row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button size="small" @click="openNovel(scope.row)">
                <el-icon><View /></el-icon>
                打开
              </el-button>
              <el-button size="small" type="primary" @click="editNovel(scope.row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="confirmDelete(scope.row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建/编辑小说对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="isEditing ? '编辑小说' : '新建小说'" 
      width="500px"
    >
      <el-form :model="novelForm" label-width="80px">
        <el-form-item label="小说标题">
          <el-input v-model="novelForm.title" placeholder="请输入小说标题" />
        </el-form-item>
        <el-form-item label="小说类型">
          <el-select v-model="novelForm.genre" placeholder="请选择小说类型" style="width: 100%">
            <el-option label="奇幻" value="奇幻" />
            <el-option label="科幻" value="科幻" />
            <el-option label="悬疑" value="悬疑" />
            <el-option label="言情" value="言情" />
            <el-option label="历史" value="历史" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="小说描述">
          <el-input v-model="novelForm.description" type="textarea" rows="3" placeholder="请输入小说描述" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="novelForm.author" placeholder="请输入作者名称" />
        </el-form-item>
        <el-form-item label="预计字数">
          <el-input-number v-model="novelForm.expectedWords" :min="1000" :max="10000000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="saveNovel">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Edit, Delete } from '@element-plus/icons-vue'
import { useProjectStore } from '../stores/projectStore'
import axios from 'axios'

// 状态管理
const projectStore = useProjectStore()
const router = useRouter()

// 对话框状态
const showCreateDialog = ref(false)
const isEditing = ref(false)

// 小说表单
const novelForm = ref({
  title: '',
  genre: '',
  description: '',
  author: '',
  expectedWords: 100000
})

// 小说列表
const novels = ref([])

// 方法
const formatWordCount = (count) => {
  // 处理undefined、null或0的情况
  if (count === undefined || count === null || count === 0) {
    return '0字'
  }
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万字'
  }
  return count + '字'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  // 使用更紧凑的日期格式，避免文字堆叠
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const openNovel = (novel) => {
  // 设置当前项目
  projectStore.setCurrentProject(novel)
  // 跳转到章节管理页面
  router.push('/chapters')
  ElMessage.success(`已打开小说: ${novel.title}`)
}

const editNovel = (novel) => {
  isEditing.value = true
  novelForm.value = { ...novel }
  showCreateDialog.value = true
}

const saveNovel = async () => {
  if (!novelForm.value.title || !novelForm.value.genre) {
    ElMessage.warning('请填写小说标题和类型')
    return
  }

  try {
    if (isEditing.value) {
      // 更新现有小说 - 调用后端API
      const response = await axios.put(`/api/projects/${novelForm.value.id}`, {
        title: novelForm.value.title,
        genre: novelForm.value.genre,
        description: novelForm.value.description,
        author: novelForm.value.author,
        expectedWords: novelForm.value.expectedWords
      })
      
      // 更新本地数据
      const index = novels.value.findIndex(n => n.id === novelForm.value.id)
      if (index !== -1) {
        novels.value[index] = {
          ...response.data,
          updated_at: new Date().toISOString()
        }
      }
      ElMessage.success('小说信息已更新')
    } else {
      // 创建新小说 - 调用后端API
      const response = await axios.post('/api/projects', {
        title: novelForm.value.title,
        genre: novelForm.value.genre,
        description: novelForm.value.description,
        author: novelForm.value.author,
        expectedWords: novelForm.value.expectedWords
      })
      
      // 添加到本地列表
      novels.value.push(response.data)
      ElMessage.success('小说创建成功')
    }

    // 重置表单和关闭对话框
    resetForm()
    showCreateDialog.value = false
  } catch (error) {
    console.error('保存小说失败:', error)
    ElMessage.error('保存小说失败: ' + (error.response?.data?.detail || error.message))
  }
}

const confirmDelete = async (novel) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除小说《${novel.title}》吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 调用后端API删除小说
    await axios.delete(`/api/projects/${novel.id}`)
    
    // 从本地列表中移除
    novels.value = novels.value.filter(n => n.id !== novel.id)
    ElMessage.success('小说已删除')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除小说失败:', error)
      ElMessage.error('删除小说失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const resetForm = () => {
  novelForm.value = {
    title: '',
    genre: '',
    description: '',
    author: '',
    expectedWords: 100000
  }
  isEditing.value = false
}

// 加载小说列表
const loadNovels = async () => {
  try {
    const response = await axios.get('/api/projects')
    
    console.log('后端返回的小说数据:', response.data)
    
    // 检查第一个项目的数据结构
    if (response.data && response.data.length > 0) {
      console.log('第一个项目完整数据:', JSON.stringify(response.data[0], null, 2))
      console.log('第一个项目字段:', Object.keys(response.data[0]))
    }
    
    novels.value = response.data
  } catch (error) {
    console.error('加载小说列表失败:', error)
    ElMessage.error('加载小说列表失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 组件挂载时加载数据和重置表单
onMounted(async () => {
  await loadNovels()
  resetForm()
})

// 组件被激活时重新加载数据
onActivated(async () => {
  await loadNovels()
})
</script>

<style scoped>
.novels-container {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.novels-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.novels-header h2 {
  margin: 0;
}

.novels-content {
  flex: 1;
  width: 100%;
}

/* 确保表格占满可用空间 */
:deep(.el-table) {
  width: 100% !important;
}

/* 确保表格容器占满可用空间 */
:deep(.el-table__body-wrapper) {
  width: 100% !important;
}

/* 优化时间列的显示 */
:deep(.el-table__cell) {
  padding: 8px 0;
}

/* 确保时间列文本不会换行 */
:deep(.el-table-column--created_at .cell),
:deep(.el-table-column--updated_at .cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 操作按钮组样式优化 */
:deep(.el-button-group) {
  display: flex;
  flex-wrap: nowrap;
}

:deep(.el-button-group .el-button) {
  padding: 5px 8px;
  font-size: 12px;
}
</style>
