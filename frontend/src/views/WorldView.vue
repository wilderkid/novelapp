<template>
  <div class="world-container">
    <div class="page-header">
      <h2>世界观设定</h2>
      <el-button type="primary" @click="addWorldSetting">
        <el-icon><Plus /></el-icon>
        新建设定
      </el-button>
    </div>

    <div class="world-categories">
      <el-tabs v-model="activeCategory" @tab-click="handleCategoryChange">
        <el-tab-pane label="全部" name="all"></el-tab-pane>
        <el-tab-pane label="地点" name="location"></el-tab-pane>
        <el-tab-pane label="组织" name="organization"></el-tab-pane>
        <el-tab-pane label="物品" name="item"></el-tab-pane>
        <el-tab-pane label="概念" name="concept"></el-tab-pane>
        <el-tab-pane label="历史" name="history"></el-tab-pane>
      </el-tabs>
    </div>

    <div class="world-grid">
      <div
        v-for="setting in filteredSettings"
        :key="setting.id"
        class="setting-card"
        @click="editSetting(setting)"
      >
        <div class="card-header">
          <h3>{{ setting.name }}</h3>
          <el-tag :type="getTagType(setting.type)">{{ getCategoryName(setting.type) }}</el-tag>
        </div>
        <div class="card-content">
          <div class="setting-description">
            {{ setting.description }}
          </div>
          <div class="setting-details" v-if="setting.details && setting.details.length > 0">
            <div class="detail-item" v-for="(detail, index) in setting.details" :key="index">
              <span class="detail-key">{{ detail.key }}:</span>
              <span class="detail-value">{{ detail.value }}</span>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <el-button type="text" @click.stop="editSetting(setting)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="text" @click.stop="deleteSetting(setting.id)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
      </div>

      <!-- 添加新设定卡片 -->
      <div class="setting-card add-card" @click="addWorldSetting">
        <div class="add-icon">
          <el-icon><Plus /></el-icon>
        </div>
        <div class="add-text">添加新设定</div>
      </div>
    </div>

    <!-- 设定编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑设定' : '新建设定'"
      width="700px"
    >
      <el-form :model="currentSetting" label-width="100px">
        <el-form-item label="设定名称">
          <el-input v-model="currentSetting.name" />
        </el-form-item>

        <el-form-item label="设定类型">
          <el-select v-model="currentSetting.type" placeholder="请选择设定类型">
            <el-option label="地点" value="location" />
            <el-option label="组织" value="organization" />
            <el-option label="物品" value="item" />
            <el-option label="概念" value="concept" />
            <el-option label="历史" value="history" />
          </el-select>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="currentSetting.description"
            type="textarea"
            :rows="3"
            placeholder="请输入设定描述"
          />
        </el-form-item>

        <el-divider content-position="left">详细属性</el-divider>

        <div class="dynamic-attributes">
          <div
            v-for="(attr, index) in currentSetting.details"
            :key="index"
            class="attribute-item"
          >
            <el-input v-model="attr.key" placeholder="属性名称" />
            <el-input v-model="attr.value" placeholder="属性值" />
            <el-button type="danger" size="small" @click="removeAttribute(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" plain @click="addAttribute">
            <el-icon><Plus /></el-icon>
            添加属性
          </el-button>
        </div>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveSetting">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

// 当前选中的类别
const activeCategory = ref('all')

// 世界观数据
const worldSettings = ref([
  {
    id: 1,
    name: '霍格沃茨',
    type: 'location',
    description: '魔法学校，充满神秘与冒险的地方，位于苏格兰高地，是世界上最著名的魔法学校。',
    details: [
      { key: '建立时间', value: '公元10世纪' },
      { key: '位置', value: '苏格兰高地' },
      { key: '创始人', value: '戈德里克·格兰芬多、赫尔加·赫奇帕奇、罗伊纳·拉文克劳、萨拉查·斯莱特林' },
      { key: '特征', value: '被魔法保护，对麻瓜不可见' }
    ]
  },
  {
    id: 2,
    name: '精灵森林',
    type: 'location',
    description: '古老精灵的栖息地，充满了魔法和神秘，凡人很难找到进入的路径。',
    details: [
      { key: '位置', value: '大陆中部，被群山环绕' },
      { key: '居民', value: '高等精灵、树精、森林精魄' },
      { key: '特征', value: '时间流速与外界不同，植物具有魔法属性' }
    ]
  },
  {
    id: 3,
    name: '魔法部',
    type: 'organization',
    description: '负责管理魔法世界的政府机构，维护魔法世界的秩序和安全。',
    details: [
      { key: '总部位置', value: '伦敦地下' },
      { key: '领导者', value: '魔法部长' },
      { key: '部门', value: '傲罗办公室、魔法法律执行司、神奇动物管理司等' }
    ]
  },
  {
    id: 4,
    name: '光明之剑',
    type: 'item',
    description: '传说中的神器，据说能够斩断一切黑暗，只有心地纯洁的人才能使用。',
    details: [
      { key: '材质', value: '未知金属，散发着柔和光芒' },
      { key: '能力', value: '破除黑暗魔法，净化邪恶' },
      { key: '持有人', value: '传说中的光明骑士' }
    ]
  },
  {
    id: 5,
    name: '魔法觉醒',
    type: 'concept',
    description: '指魔法能力在个体中显现的过程，通常发生在青少年时期，但也存在晚觉醒的情况。',
    details: [
      { key: '发生时间', value: '通常在11-17岁之间' },
      { key: '表现形式', value: '无法控制的魔法爆发、情绪波动引发魔法现象' },
      { key: '后续处理', value: '需要魔法教育机构进行引导和控制训练' }
    ]
  },
  {
    id: 6,
    name: '黑暗战争',
    type: 'history',
    description: '发生在五百年前的一场席卷整个魔法世界的战争，光明与黑暗两大阵营的决战。',
    details: [
      { key: '时间', value: '约500年前' },
      { key: '参战方', value: '光明联盟与黑暗势力' },
      { key: '结果', value: '黑暗势力被击败，但其首领并未被消灭' },
      { key: '影响', value: '魔法世界的格局被重新定义，许多魔法知识失传' }
    ]
  }
])

// 过滤后的设定
const filteredSettings = computed(() => {
  if (activeCategory.value === 'all') {
    return worldSettings.value
  }
  return worldSettings.value.filter(setting => setting.type === activeCategory.value)
})

// 对话框状态
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentSetting = reactive({
  id: null,
  name: '',
  type: 'location',
  description: '',
  details: []
})

// 类别名称映射
const categoryNames = {
  location: '地点',
  organization: '组织',
  item: '物品',
  concept: '概念',
  history: '历史'
}

// 获取类别名称
const getCategoryName = (type) => {
  return categoryNames[type] || '其他'
}

// 获取标签样式类型
const getTagType = (type) => {
  const typeMap = {
    location: '',
    organization: 'success',
    item: 'warning',
    concept: 'info',
    history: 'danger'
  }
  return typeMap[type] || ''
}

// 处理类别切换
const handleCategoryChange = () => {
  // 类别切换时的处理逻辑
}

// 添加设定
const addWorldSetting = () => {
  isEdit.value = false
  currentSetting.id = null
  currentSetting.name = ''
  currentSetting.type = 'location'
  currentSetting.description = ''
  currentSetting.details = []
  dialogVisible.value = true
}

// 编辑设定
const editSetting = (setting) => {
  isEdit.value = true
  currentSetting.id = setting.id
  currentSetting.name = setting.name
  currentSetting.type = setting.type
  currentSetting.description = setting.description
  currentSetting.details = JSON.parse(JSON.stringify(setting.details))
  dialogVisible.value = true
}

// 保存设定
const saveSetting = () => {
  if (!currentSetting.name) {
    ElMessage.warning('请输入设定名称')
    return
  }

  if (!currentSetting.type) {
    ElMessage.warning('请选择设定类型')
    return
  }

  if (isEdit.value) {
    // 更新现有设定
    const index = worldSettings.value.findIndex(s => s.id === currentSetting.id)
    if (index !== -1) {
      worldSettings.value[index] = { ...currentSetting }
      ElMessage.success('设定已更新')
    }
  } else {
    // 添加新设定
    const newId = Math.max(...worldSettings.value.map(s => s.id), 0) + 1
    worldSettings.value.push({
      ...currentSetting,
      id: newId
    })
    ElMessage.success('设定已添加')
  }

  dialogVisible.value = false
}

// 删除设定
const deleteSetting = (id) => {
  ElMessageBox.confirm('确定要删除该设定吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = worldSettings.value.findIndex(s => s.id === id)
    if (index !== -1) {
      worldSettings.value.splice(index, 1)
      ElMessage.success('设定已删除')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 添加属性
const addAttribute = () => {
  currentSetting.details.push({ key: '', value: '' })
}

// 删除属性
const removeAttribute = (index) => {
  currentSetting.details.splice(index, 1)
}
</script>

<style scoped>
.world-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.world-categories {
  margin-bottom: 20px;
}

.world-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.setting-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
}

.setting-card:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.card-header h3 {
  margin: 0;
}

.card-content {
  flex: 1;
  margin-bottom: 15px;
}

.setting-description {
  margin-bottom: 10px;
  color: #606266;
  line-height: 1.5;
}

.setting-details {
  margin-top: 10px;
}

.detail-item {
  margin-bottom: 8px;
  display: flex;
}

.detail-key {
  font-weight: bold;
  margin-right: 8px;
  min-width: 80px;
}

.detail-value {
  flex: 1;
  word-break: break-word;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
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

.dynamic-attributes {
  max-height: 300px;
  overflow-y: auto;
}

.attribute-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.attribute-item .el-input {
  flex: 1;
}
</style>
