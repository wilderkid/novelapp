<template>
  <div class="chapter-tabs">
    <el-tabs v-model="activeTab" type="card" closable @tab-remove="removeTab">
      <el-tab-pane
        v-for="chapter in openChapters"
        :key="chapter.id"
        :label="chapter.title"
        :name="chapter.id.toString()"
      >
        <div class="chapter-editor">
          <div class="editor-header">
            <el-input
              v-model="chapter.title"
              placeholder="章节标题"
              class="chapter-title-input"
              @change="updateChapterTitle(chapter)"
            />
            <div class="editor-tools">
              <el-button type="text" @click="insertVariable">
                <el-icon><MagicStick /></el-icon>
                插入变量
              </el-button>
              <el-button type="text" @click="saveChapter(chapter)">
                <el-icon><Document /></el-icon>
                保存
              </el-button>
            </div>
          </div>
          <div class="editor-content">
            <vue-ueditor-wrap
              v-model="chapter.content"
              :editor-id="`editor-${chapter.id}`"
              :config="editorConfig"
              :editor-dependencies="['ueditor.config.js', 'ueditor.all.js']"
              style="height: calc(100% - 60px)"
              @ready="editorReady"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 插入变量对话框 -->
    <el-dialog v-model="variableDialogVisible" title="插入变量" width="500px">
      <el-tabs v-model="activeVariableTab">
        <el-tab-pane label="项目信息" name="project">
          <div class="variable-list">
            <div
              v-for="variable in projectVariables"
              :key="variable.name"
              class="variable-item"
              @click="selectVariable(variable)"
            >
              <div class="variable-name">{{ variable.name }}</div>
              <div class="variable-desc">{{ variable.description }}</div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="角色" name="character">
          <div class="variable-list">
            <div
              v-for="character in characters"
              :key="character.id"
              class="variable-item"
              @click="selectCharacterVariable(character)"
            >
              <div class="variable-name">{{ character.name }}</div>
              <div class="variable-desc">{{ character.description }}</div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="世界观" name="world">
          <div class="variable-list">
            <div
              v-for="world in worlds"
              :key="world.id"
              class="variable-item"
              @click="selectWorldVariable(world)"
            >
              <div class="variable-name">{{ world.name }}</div>
              <div class="variable-desc">{{ world.description }}</div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="variableDialogVisible = false">取消</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { ElMessage } from "element-plus";
import { MagicStick, Document } from "@element-plus/icons-vue";
import { useEditorStore } from "../stores/editorStore";
import { useProjectStore } from "../stores/projectStore";
import config from "../config.js";

// 状态管理
const editorStore = useEditorStore();
const projectStore = useProjectStore();

// 编辑器配置
const editorConfig = ref(config.editor);

// 计算属性
const openChapters = computed(() => editorStore.openChapters);
const activeTab = computed({
  get: () => editorStore.activeChapterId?.toString() || "",
  set: (value) => {
    editorStore.activeChapterId = parseInt(value);
  },
});

// 变量对话框
const variableDialogVisible = ref(false);
const activeVariableTab = ref("project");

// 示例数据 - 在实际应用中，这些数据应该从API获取
const projectVariables = ref([
  { name: "project.title", description: "项目标题" },
  { name: "project.genre", description: "项目类型" },
]);

const characters = ref([
  { id: 1, name: "李昂", description: "主角，勇敢而鲁莽的年轻人" },
  { id: 2, name: "苏晴", description: "女主角，聪慧而冷静的学者" },
]);

const worlds = ref([
  { id: 1, name: "霍格沃茨", description: "魔法学校，充满神秘与冒险" },
  { id: 2, name: "精灵森林", description: "古老精灵的栖息地" },
]);

// 方法
const removeTab = (targetName) => {
  const chapterId = parseInt(targetName);
  editorStore.closeChapter(chapterId);
};

const updateChapterTitle = (chapter) => {
  editorStore.updateChapter(chapter.id, { title: chapter.title });
  ElMessage.success("章节标题已更新");
};

const saveChapter = (chapter) => {
  // 在实际应用中，这里会调用API保存章节
  ElMessage.success("章节已保存");
};

const insertVariable = () => {
  variableDialogVisible.value = true;
};

const selectVariable = (variable) => {
  // 在实际应用中，这里会在编辑器中插入变量
  ElMessage.info(`已选择变量: ${variable.name}`);
  variableDialogVisible.value = false;
};

const selectCharacterVariable = (character) => {
  // 在实际应用中，这里会在编辑器中插入角色变量
  ElMessage.info(`已选择角色: ${character.name}`);
  variableDialogVisible.value = false;
};

const selectWorldVariable = (world) => {
  // 在实际应用中，这里会在编辑器中插入世界观变量
  ElMessage.info(`已选择世界观: ${world.name}`);
  variableDialogVisible.value = false;
};

const editorReady = (editor) => {
  // 编辑器准备就绪时的回调
  console.log("编辑器准备就绪:", editor);
};
</script>

<style scoped>
.chapter-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chapter-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #e6e6e6;
}

.chapter-title-input {
  width: 300px;
}

.editor-tools {
  display: flex;
  gap: 10px;
}

.editor-content {
  flex: 1;
  padding: 15px;
}

.variable-list {
  max-height: 300px;
  overflow-y: auto;
}

.variable-item {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.variable-item:hover {
  background-color: #f5f7fa;
}

.variable-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.variable-desc {
  font-size: 12px;
  color: #666;
}
</style>
