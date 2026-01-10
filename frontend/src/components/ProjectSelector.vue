<template>
  <div class="project-selector">
    <el-dropdown @command="selectProject" trigger="click">
      <span class="project-dropdown">
        {{ currentProjectTitle || "请选择项目" }}
        <el-icon class="el-icon--right"><arrow-down /></el-icon>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item
            v-for="project in projects"
            :key="project.id"
            :command="project.id"
          >
            {{ project.title }}
          </el-dropdown-item>
          <el-dropdown-item divided command="new">新建项目</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 新建项目对话框 -->
    <el-dialog v-model="newProjectDialogVisible" title="新建项目" width="500px">
      <el-form :model="newProjectForm" label-width="80px">
        <el-form-item label="项目标题">
          <el-input
            v-model="newProjectForm.title"
            placeholder="请输入项目标题"
          />
        </el-form-item>
        <el-form-item label="项目类型">
          <el-select
            v-model="newProjectForm.genre"
            placeholder="请选择项目类型"
            style="width: 100%"
          >
            <el-option label="奇幻" value="奇幻" />
            <el-option label="科幻" value="科幻" />
            <el-option label="悬疑" value="悬疑" />
            <el-option label="言情" value="言情" />
            <el-option label="历史" value="历史" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input
            v-model="newProjectForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        <el-form-item label="作者">
          <el-input
            v-model="newProjectForm.author"
            placeholder="请输入作者名称"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="newProjectDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createProject">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowDown } from "@element-plus/icons-vue";
import { useProjectStore } from "../stores/projectStore";
import { useEditorStore } from "../stores/editorStore";

// 状态管理
const router = useRouter();
const projectStore = useProjectStore();
const editorStore = useEditorStore();

// 对话框状态
const newProjectDialogVisible = ref(false);

// 新建项目表单
const newProjectForm = ref({
  title: "",
  genre: "",
  description: "",
  author: "",
});

// 计算属性
const currentProjectTitle = computed(() => {
  return projectStore.currentProject?.title || "";
});

const projects = computed(() => {
  return projectStore.projects;
});

// 方法
const selectProject = (command) => {
  if (command === "new") {
    // 跳转到小说管理页面创建新小说
    router.push("/novels");
  } else {
    // 选择现有项目
    const projectId = parseInt(command);
    const project = projects.value.find((p) => p.id === projectId);
    if (project) {
      projectStore.setCurrentProject(project);
      // 切换项目时关闭所有打开的章节
      editorStore.closeAllChapters();
      // 跳转到章节管理页面
      router.push("/chapters");
      ElMessage.success(`已切换到项目: ${project.title}`);
    }
  }
};

const createProject = () => {
  if (!newProjectForm.value.title || !newProjectForm.value.genre) {
    ElMessage.warning("请填写项目标题和类型");
    return;
  }

  // 在实际应用中，这里会调用API创建项目
  const newProject = {
    id: Date.now(), // 临时ID，实际应用中由后端生成
    ...newProjectForm.value,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  // 添加到项目列表
  projectStore.addProject(newProject);

  // 设置为当前项目
  projectStore.setCurrentProject(newProject);

  // 关闭对话框
  newProjectDialogVisible.value = false;

  // 重置表单
  newProjectForm.value = {
    title: "",
    genre: "",
    description: "",
    author: "",
  };

  ElMessage.success("项目创建成功");
};
</script>

<style scoped>
.project-selector {
  margin-left: 20px;
}

.project-dropdown {
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
}

.project-dropdown:hover {
  color: #409eff;
}
</style>
