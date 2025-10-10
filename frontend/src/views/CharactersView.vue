<template>
  <div class="characters-container">
    <div class="page-header">
      <h2>角色设定</h2>
      <el-button type="primary" @click="addCharacter">
        <el-icon><Plus /></el-icon>
        新建角色
      </el-button>
    </div>

    <div class="characters-grid">
      <div
        v-for="character in characters"
        :key="character.id"
        class="character-card"
        @click="editCharacter(character)"
      >
        <div class="card-header">
          <h3>{{ character.name }}</h3>
          <el-dropdown @command="handleCommand">
            <el-button type="text">
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :command="{ action: 'edit', id: character.id }">编辑</el-dropdown-item>
                <el-dropdown-item :command="{ action: 'delete', id: character.id }">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="card-content">
          <div class="character-details">
            <div class="detail-item">
              <span class="detail-key">角色描述:</span>
              <span class="detail-value">{{ character.description }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-key">参与剧情:</span>
              <span class="detail-value">{{ character.plot }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加新角色卡片 -->
      <div class="character-card add-card" @click="addCharacter">
        <div class="add-icon">
          <el-icon><Plus /></el-icon>
        </div>
        <div class="add-text">添加新角色</div>
      </div>
    </div>

    <!-- 角色编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑角色' : '新建角色'"
      width="600px"
    >
      <el-form :model="currentCharacter" label-width="100px">
        <el-form-item label="角色姓名">
          <el-input v-model="currentCharacter.name" />
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input
            v-model="currentCharacter.description"
            type="textarea"
            :rows="4"
            placeholder="请输入角色描述"
          />
        </el-form-item>
        <el-form-item label="参与剧情">
          <el-input
            v-model="currentCharacter.plot"
            type="textarea"
            :rows="4"
            placeholder="请输入角色参与的剧情"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveCharacter">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, More, Delete } from '@element-plus/icons-vue'

// 角色数据
const characters = ref([
  {
    id: 1,
    name: '李昂',
    description: '勇敢、鲁莽。出身普通农家，从小就展现出与众不同的勇气。身材高大，黑发黑眸，眉宇间透着一股英气。',
    plot: '作为主角，推动了主要剧情的发展。'
  },
  {
    id: 2,
    name: '苏晴',
    description: '聪慧、冷静。来自学者世家，博学多才。容貌秀美，气质高雅，总是带着书卷气。',
    plot: '在主角困难时提供关键帮助，是智慧的象征。'
  }
])

// 对话框状态
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentCharacter = reactive({
  id: null,
  name: '',
  description: '',
  plot: ''
})

// 添加角色
const addCharacter = () => {
  isEdit.value = false
  currentCharacter.id = null
  currentCharacter.name = ''
  currentCharacter.description = ''
  currentCharacter.plot = ''
  dialogVisible.value = true
}

// 编辑角色
const editCharacter = (character) => {
  isEdit.value = true
  currentCharacter.id = character.id
  currentCharacter.name = character.name
  currentCharacter.description = character.description
  currentCharacter.plot = character.plot
  dialogVisible.value = true
}

// 保存角色
const saveCharacter = () => {
  if (!currentCharacter.name) {
    ElMessage.warning('请输入角色名称')
    return
  }

  if (isEdit.value) {
    // 更新现有角色
    const index = characters.value.findIndex(c => c.id === currentCharacter.id)
    if (index !== -1) {
      characters.value[index] = { ...currentCharacter }
      ElMessage.success('角色已更新')
    }
  } else {
    // 添加新角色
    const newId = Math.max(...characters.value.map(c => c.id), 0) + 1
    characters.value.push({
      ...currentCharacter,
      id: newId
    })
    ElMessage.success('角色已添加')
  }

  dialogVisible.value = false
}

// 删除角色
const deleteCharacter = (id) => {
  ElMessageBox.confirm('确定要删除该角色吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = characters.value.findIndex(c => c.id === id)
    if (index !== -1) {
      characters.value.splice(index, 1)
      ElMessage.success('角色已删除')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 处理下拉菜单命令
const handleCommand = (command) => {
  if (command.action === 'edit') {
    const character = characters.value.find(c => c.id === command.id)
    if (character) {
      editCharacter(character)
    }
  } else if (command.action === 'delete') {
    deleteCharacter(command.id)
  }
}
</script>

<style scoped>
.characters-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.character-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.character-card:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.card-header h3 {
  margin: 0;
}

.card-content {
  display: flex;
  gap: 15px;
}

.character-details {
  flex: 1;
}

.detail-item {
  margin-bottom: 8px;
}

.detail-key {
  font-weight: bold;
  margin-right: 8px;
}

.detail-value {
  word-break: break-word;
  color: #606266;
}

.add-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border: 1px dashed #c0c4cc;
  color: #909399;
}

.add-card:hover {
  border-color: #409eff;
  color: #409eff;
}

.add-icon {
  font-size: 30px;
  margin-bottom: 10px;
}

.add-text {
  font-size: 14px;
}
</style>