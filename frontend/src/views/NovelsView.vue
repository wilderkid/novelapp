<template>
  <div class="novels-container" role="main" aria-label="小说管理页面">
    <PageHeader
      title="小说管理"
      :actions="[
        {
          text: '新建小说',
          icon: Plus,
          loading: isLoading,
          handler: () => (showCreateDialog = true),
        },
        {
          text: '导入小说',
          icon: Upload,
          handler: importNovel,
        },
      ]"
    />

    <div class="novels-content">
      <el-table
        ref="novelTable"
        :data="novels"
        style="width: 100%"
        table-layout="fixed"
        v-loading="isLoading"
        element-loading-text="加载小说数据中..."
        element-loading-background="rgba(255, 255, 255, 0.8)"
        aria-label="小说列表"
        role="table"
        row-key="id"
      >
        <el-table-column prop="title" label="小说标题" show-overflow-tooltip>
          <template #header>
            <el-icon><Reading /></el-icon> 小说标题
          </template>
        </el-table-column>
        <el-table-column prop="genre" label="类型" width="80">
          <template #header>
            <el-icon><Collection /></el-icon> 类型
          </template>
        </el-table-column>
        <el-table-column prop="author" label="作者" width="100">
          <template #header>
            <el-icon><User /></el-icon> 作者
          </template>
        </el-table-column>
        <el-table-column prop="wordCount" label="字数" width="90">
          <template #header>
            <el-icon><Document /></el-icon> 字数
          </template>
          <template #default="scope">
            {{
              formatWordCount(scope.row.wordCount || scope.row.word_count || 0)
            }}
          </template>
        </el-table-column>
        <el-table-column prop="chapterCount" label="章节数" width="100">
          <template #header>
            <el-icon><Tickets /></el-icon> 章节数
          </template>
          <template #default="scope">
            {{ scope.row.chapterCount || scope.row.chapter_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column
          prop="created_at"
          label="创建时间"
          width="170"
          sortable
        >
          <template #header>
            <el-icon><Clock /></el-icon> 创建时间
          </template>
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="updated_at"
          label="更新时间"
          width="170"
          sortable
        >
          <template #header>
            <el-icon><Timer /></el-icon> 更新时间
          </template>
          <template #default="scope">
            {{ formatDate(scope.row.updated_at || scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #header>
            <el-icon><Operation /></el-icon> 操作
          </template>
          <template #default="scope">
            <el-button-group role="group" aria-label="小说操作按钮组">
              <el-button
                size="small"
                @click="openNovel(scope.row)"
                :loading="activeNovelId === scope.row.id && isLoading"
                :aria-label="`打开小说 ${scope.row.title}`"
              >
                <el-icon><View /></el-icon>
                打开
              </el-button>
              <el-button
                size="small"
                type="primary"
                @click="editNovel(scope.row)"
                :loading="activeNovelId === scope.row.id && isLoading"
                :aria-label="`编辑小说 ${scope.row.title}`"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                size="small"
                type="success"
                @click="exportNovel(scope.row)"
                :aria-label="`导出小说 ${scope.row.title}`"
              >
                <el-icon><Download /></el-icon>
                导出
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="confirmDelete(scope.row)"
                :loading="activeNovelId === scope.row.id && isDeleting"
                :aria-label="`删除小说 ${scope.row.title}`"
              >
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
      :close-on-click-modal="false"
      :aria-label="isEditing ? '编辑小说对话框' : '新建小说对话框'"
      role="dialog"
      :modal="true"
    >
      <el-form :model="novelForm" label-width="80px">
        <el-form-item label="小说标题" aria-label="小说标题输入框">
          <el-input
            v-model="novelForm.title"
            placeholder="请输入小说标题"
            :disabled="isSaving"
            aria-label="小说标题输入框"
          />
        </el-form-item>
        <el-form-item label="小说类型" aria-label="小说类型选择框">
          <el-select
            v-model="novelForm.genre"
            placeholder="请选择小说类型"
            style="width: 100%"
            :disabled="isSaving"
            aria-label="小说类型选择框"
            allow-create
            filterable
          >
            <el-option
              v-for="genre in genreOptions"
              :key="genre.id"
              :label="genre.name"
              :value="genre.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="小说描述" aria-label="小说描述输入框">
          <el-input
            v-model="novelForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入小说描述"
            :disabled="isSaving"
            aria-label="小说描述输入框"
          />
        </el-form-item>
        <el-form-item label="作者" aria-label="作者输入框">
          <el-input
            v-model="novelForm.author"
            placeholder="请输入作者名称"
            :disabled="isSaving"
            aria-label="作者输入框"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button
            @click="showCreateDialog = false"
            :disabled="isSaving"
            aria-label="取消按钮"
          >
            取消
          </el-button>
          <el-button
            type="primary"
            @click="saveNovel"
            :loading="isSaving"
            aria-label="确认保存按钮"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, nextTick } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  View,
  Edit,
  Delete,
  Reading,
  Collection,
  User,
  Document,
  Tickets,
  Clock,
  Timer,
  Operation,
  Upload,
  Download,
} from "@element-plus/icons-vue";
import { useProjectStore } from "../stores/projectStore";
import PageHeader from "../components/PageHeader.vue";
import axios from "axios";
import Sortable from "sortablejs";

// 状态管理
const projectStore = useProjectStore();
const router = useRouter();

// 对话框状态
const showCreateDialog = ref(false);
const isEditing = ref(false);

// 小说表单
const novelForm = ref({
  title: "",
  genre: "",
  description: "",
  author: "",
});

// 小说列表
const novels = ref([]);
const genreOptions = ref([]);

// 加载状态
const isLoading = ref(false);
const isSaving = ref(false);
const isDeleting = ref(false);
const activeNovelId = ref(null);
const novelTable = ref(null);
let sortableInstance = null;

// 方法
const formatWordCount = (count) => {
  // 处理undefined、null或0的情况
  if (count === undefined || count === null || count === 0) {
    return "0字";
  }
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + "万字";
  }
  return count + "字";
};

const formatDate = (dateString) => {
  if (!dateString) {
    return "—";
  }
  const date = new Date(dateString);
  if (isNaN(date.getTime())) {
    return "—";
  }
  // 使用更紧凑的日期格式，避免文字堆叠
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");

  return `${year}-${month}-${day} ${hours}:${minutes}`;
};

const openNovel = (novel) => {
  activeNovelId.value = novel.id;
  isLoading.value = true;
  try {
    // 设置当前项目
    projectStore.setCurrentProject(novel);
    // 跳转到章节管理页面
    router.push("/chapters");
    ElMessage.success(`已打开小说: ${novel.title}`);
  } finally {
    isLoading.value = false;
    activeNovelId.value = null;
  }
};

const editNovel = (novel) => {
  isEditing.value = true;
  novelForm.value = { ...novel };
  showCreateDialog.value = true;
};

const saveNovel = async () => {
  if (!novelForm.value.title || !novelForm.value.genre) {
    ElMessage.warning("请填写小说标题和类型");
    return;
  }

  isSaving.value = true;
  try {
    if (isEditing.value) {
      // 更新现有小说 - 调用后端API
      const response = await axios.put(`/api/projects/${novelForm.value.id}`, {
        title: novelForm.value.title,
        genre: novelForm.value.genre,
        description: novelForm.value.description,
        author: novelForm.value.author,
      });

      // 更新本地数据
      const index = novels.value.findIndex((n) => n.id === novelForm.value.id);
      if (index !== -1) {
        novels.value[index] = {
          ...response.data,
          updated_at: new Date().toISOString(),
        };
      }
      ElMessage.success("小说信息已更新");
    } else {
      // 创建新小说 - 调用后端API
      const response = await axios.post("/api/projects", {
        title: novelForm.value.title,
        genre: novelForm.value.genre,
        description: novelForm.value.description,
        author: novelForm.value.author,
      });

      // 添加到本地列表
      novels.value.push(response.data);
      ElMessage.success("小说创建成功");
    }

    // 重置表单和关闭对话框
    resetForm();
    showCreateDialog.value = false;
  } catch (error) {
    console.error("保存小说失败:", error);
    ElMessage.error(
      "保存小说失败: " + (error.response?.data?.detail || error.message),
    );
  } finally {
    isSaving.value = false;
  }
};

const confirmDelete = async (novel) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除小说《${novel.title}》吗？此操作不可恢复！`,
      "删除确认",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    activeNovelId.value = novel.id;
    isDeleting.value = true;

    // 调用后端API删除小说
    await axios.delete(`/api/projects/${novel.id}`);

    // 从本地列表中移除
    novels.value = novels.value.filter((n) => n.id !== novel.id);
    ElMessage.success("小说已删除");
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除小说失败:", error);
      ElMessage.error(
        "删除小说失败: " + (error.response?.data?.detail || error.message),
      );
    }
  } finally {
    isDeleting.value = false;
    activeNovelId.value = null;
  }
};

const resetForm = () => {
  novelForm.value = {
    title: "",
    genre: "",
    description: "",
    author: "",
  };
  isEditing.value = false;
};

// 加载小说列表
const loadNovels = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get("/api/projects");

    console.log("后端返回的小说数据:", response.data);

    // 检查第一个项目的数据结构
    if (response.data && response.data.length > 0) {
      console.log(
        "第一个项目完整数据:",
        JSON.stringify(response.data[0], null, 2),
      );
      console.log("第一个项目字段:", Object.keys(response.data[0]));
    }

    novels.value = response.data;
  } catch (error) {
    console.error("加载小说列表失败:", error);
    ElMessage.error(
      "加载小说列表失败: " + (error.response?.data?.detail || error.message),
    );
  } finally {
    isLoading.value = false;
  }

  // 初始化拖拽排序
  await nextTick();
  initSortable();
};

const initSortable = () => {
  if (!novelTable.value) return;

  const tbody = novelTable.value.$el.querySelector(
    ".el-table__body-wrapper tbody",
  );
  if (!tbody) return;

  if (sortableInstance) {
    sortableInstance.destroy();
  }

  sortableInstance = Sortable.create(tbody, {
    animation: 150,
    handle: ".el-table__row",
    onEnd: async (evt) => {
      const { oldIndex, newIndex } = evt;
      if (oldIndex === newIndex) return;

      // 更新本地数组
      const movedItem = novels.value.splice(oldIndex, 1)[0];
      novels.value.splice(newIndex, 0, movedItem);

      // 发送新的排序到后端
      try {
        const projectIds = novels.value.map((n) => n.id);
        await axios.put("/api/projects/reorder", projectIds);
        ElMessage.success("排序已保存");
      } catch (error) {
        console.error("保存排序失败:", error);
        ElMessage.error("保存排序失败");
        // 重新加载以恢复原始顺序
        await loadNovels();
      }
    },
  });
};

const loadGenres = async () => {
  try {
    const response = await axios.get("/api/novel-genres");
    genreOptions.value = response.data;
  } catch (error) {
    console.error("加载小说类型失败:", error);
  }
};

const exportNovel = async (novel) => {
  try {
    ElMessage.info(`正在导出小说《${novel.title}》，请稍候...`);

    const volumesResponse = await axios.get(
      `/api/projects/${novel.id}/volumes`,
    );
    const volumes = volumesResponse.data;

    const volumesWithChapters = [];

    for (const volume of volumes) {
      const chaptersResponse = await axios.get(
        `/api/volumes/${volume.id}/chapters`,
      );
      const chapters = chaptersResponse.data.map((c) => ({
        title: c.title,
        content: c.content,
        order: c.order,
      }));
      volumesWithChapters.push({
        title: volume.title,
        order: volume.order,
        chapters: chapters,
      });
    }

    const novelData = {
      title: novel.title,
      genre: novel.genre,
      description: novel.description,
      author: novel.author,
      volumes: volumesWithChapters,
    };

    const jsonStr = JSON.stringify(novelData, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${novel.title}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    ElMessage.success(`小说《${novel.title}》导出成功`);
  } catch (error) {
    console.error("导出小说失败:", error);
    ElMessage.error(
      "导出小说失败: " + (error.response?.data?.detail || error.message),
    );
  }
};

const importNovel = () => {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".json";
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const novelData = JSON.parse(event.target.result);
        await axios.post("/api/projects/import", novelData);
        ElMessage.success(`小说《${novelData.title}》导入成功`);
        await loadNovels();
      } catch (error) {
        console.error("导入小说失败:", error);
        ElMessage.error(
          "导入小说失败: " + (error.response?.data?.detail || error.message),
        );
      }
    };
    reader.readAsText(file);
  };
  input.click();
};

// 组件挂载时加载数据和重置表单
onMounted(async () => {
  await loadNovels();
  await loadGenres();
  resetForm();
});

// 组件被激活时重新加载数据
onActivated(async () => {
  await loadNovels();
  await loadGenres();
});

// 组件卸载时销毁 Sortable 实例
import { onBeforeUnmount } from "vue";
onBeforeUnmount(() => {
  if (sortableInstance) {
    sortableInstance.destroy();
  }
});
</script>

<style scoped>
.novels-container {
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background-color: #f5f7fa;
}

.novels-content {
  flex: 1;
  width: 100%;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-top: 12px;
}

/* 确保表格占满可用空间 */
:deep(.el-table) {
  width: 100% !important;
  border-radius: 8px;
  overflow: hidden;
}

/* 确保表格容器占满可用空间 */
:deep(.el-table__body-wrapper) {
  width: 100% !important;
}

/* 优化时间列的显示 */
:deep(.el-table__cell) {
  padding: 12px 0;
}

:deep(.el-table th.el-table__cell) {
  background-color: #f8f9fa;
  color: #606266;
  font-weight: 600;
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
  padding: 6px 10px;
  font-size: 12px;
}

/* 拖拽排序样式 */
:deep(.el-table__row) {
  cursor: move;
}

:deep(.sortable-ghost) {
  opacity: 0.4;
  background: #f0f9ff;
}

:deep(.sortable-drag) {
  opacity: 0.8;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .novels-container {
    padding: 10px;
  }

  .novels-header {
    flex-direction: column;
    align-items: stretch;
  }

  .novels-header h2 {
    font-size: 20px;
  }

  /* 在小屏幕上隐藏某些列 */
  :deep(.el-table__header-wrapper),
  :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }

  :deep(.el-table) {
    min-width: 600px;
  }
}
</style>
