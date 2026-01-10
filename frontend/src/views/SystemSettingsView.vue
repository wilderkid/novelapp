<template>
  <div class="system-settings-container">
    <h2>系统管理</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane name="genres" label="小说类型管理">
        <div class="genres-management">
          <el-button
            type="primary"
            @click="showGenreDialog = true"
            style="margin-bottom: 15px"
          >
            <el-icon><Plus /></el-icon> 新增类型
          </el-button>

          <el-table :data="genres" style="width: 100%">
            <el-table-column prop="name" label="类型名称" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="editGenre(scope.row)"
                  >编辑</el-button
                >
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteGenre(scope.row)"
                  >删除</el-button
                >
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane name="chat" label="AI对话默认设置">
        <el-form
          :model="chatDefaults"
          label-width="120px"
          class="settings-form"
        >
          <el-form-item label="默认AI模型">
            <el-select
              v-model="chatDefaults.aiModelId"
              placeholder="选择默认AI模型"
              style="width: 100%"
            >
              <el-option label="无默认模型" :value="null" />
              <el-option-group
                v-for="(models, providerName) in groupedAiModels"
                :key="providerName"
                :label="providerName"
              >
                <el-option
                  v-for="model in models"
                  :key="model.id"
                  :label="model.name"
                  :value="model.id"
                />
              </el-option-group>
            </el-select>
          </el-form-item>
          <el-form-item label="默认提示词">
            <el-select
              v-model="chatDefaults.promptTemplateId"
              placeholder="选择默认提示词"
              style="width: 100%"
            >
              <el-option label="无默认提示词" :value="null" />
              <el-option
                v-for="template in promptTemplates"
                :key="template.id"
                :label="template.name"
                :value="template.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="默认温度">
            <el-input-number
              v-model="chatDefaults.temperature"
              :min="0"
              :max="1"
              :step="0.1"
              :precision="1"
            />
            <div class="form-item-tip">控制输出的随机性，0-1之间</div>
          </el-form-item>
          <el-form-item label="默认最大Token">
            <el-input-number
              v-model="chatDefaults.maxTokens"
              :min="100"
              :max="1000000"
              :step="100"
            />
            <div class="form-item-tip">限制AI回复的最大长度</div>
          </el-form-item>
          <el-form-item label="默认记忆轮数">
            <el-input-number
              v-model="chatDefaults.memoryRounds"
              :min="1"
              :max="200"
              :step="1"
            />
            <div class="form-item-tip">保留最近N轮对话作为上下文</div>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveChatDefaults"
              >保存AI对话默认设置</el-button
            >
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane name="assistant" label="创作助手默认设置">
        <el-form
          :model="assistantDefaults"
          label-width="120px"
          class="settings-form"
        >
          <el-form-item label="默认AI模型">
            <el-select
              v-model="assistantDefaults.aiModelId"
              placeholder="选择默认AI模型"
              style="width: 100%"
            >
              <el-option label="无默认模型" :value="null" />
              <el-option-group
                v-for="(models, providerName) in groupedAiModels"
                :key="providerName"
                :label="providerName"
              >
                <el-option
                  v-for="model in models"
                  :key="model.id"
                  :label="model.name"
                  :value="model.id"
                />
              </el-option-group>
            </el-select>
          </el-form-item>
          <el-form-item label="默认提示词">
            <el-select
              v-model="assistantDefaults.promptTemplateId"
              placeholder="选择默认提示词"
              style="width: 100%"
            >
              <el-option label="无默认提示词" :value="null" />
              <el-option
                v-for="template in promptTemplates"
                :key="template.id"
                :label="template.name"
                :value="template.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="默认温度">
            <el-input-number
              v-model="assistantDefaults.temperature"
              :min="0"
              :max="1"
              :step="0.1"
              :precision="1"
            />
            <div class="form-item-tip">控制输出的随机性，0-1之间</div>
          </el-form-item>
          <el-form-item label="默认最大Token">
            <el-input-number
              v-model="assistantDefaults.maxTokens"
              :min="100"
              :max="1000000"
              :step="100"
            />
            <div class="form-item-tip">限制AI回复的最大长度</div>
          </el-form-item>
          <el-form-item label="默认记忆轮数">
            <el-input-number
              v-model="assistantDefaults.memoryRounds"
              :min="1"
              :max="200"
              :step="1"
            />
            <div class="form-item-tip">保留最近N轮对话作为上下文</div>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveAssistantDefaults"
              >保存创作助手默认设置</el-button
            >
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="showGenreDialog"
      :title="genreForm.id ? '编辑类型' : '新增类型'"
      width="400px"
    >
      <el-form :model="genreForm" label-width="80px">
        <el-form-item label="类型名称">
          <el-input v-model="genreForm.name" placeholder="请输入类型名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenreDialog = false">取消</el-button>
        <el-button type="primary" @click="saveGenre">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import { useSystemStore } from "@/stores/systemStore";
import axios from "axios";

const systemStore = useSystemStore();
const activeTab = ref("genres");

const promptTemplates = ref([]);
const aiModels = ref([]);
const genres = ref([]);
const showGenreDialog = ref(false);
const genreForm = reactive({
  id: null,
  name: "",
});

const chatDefaults = reactive({
  aiModelId: null,
  promptTemplateId: null,
  temperature: 0.7,
  maxTokens: 2000,
  memoryRounds: 10,
});

const assistantDefaults = reactive({
  aiModelId: null,
  promptTemplateId: null,
  temperature: 0.7,
  maxTokens: 2000,
  memoryRounds: 10,
});

const groupedAiModels = computed(() => {
  if (!aiModels.value) return {};
  return aiModels.value.reduce((acc, model) => {
    const providerName = model.provider.name;
    if (!acc[providerName]) {
      acc[providerName] = [];
    }
    acc[providerName].push(model);
    return acc;
  }, {});
});

const fetchPromptTemplates = async () => {
  try {
    const response = await axios.get("/api/prompt-templates");
    promptTemplates.value = response.data;
  } catch (error) {
    console.error("Failed to fetch prompt templates:", error);
    ElMessage.error("加载提示模板失败");
  }
};

const fetchAiModels = async () => {
  try {
    const response = await axios.get("/api/ai-models");
    aiModels.value = response.data;
  } catch (error) {
    console.error("Failed to fetch AI models:", error);
    ElMessage.error("加载AI模型失败");
  }
};

const saveChatDefaults = () => {
  systemStore.updateSettings({
    chatDefaults: { ...chatDefaults },
  });
  ElMessage.success("AI对话默认设置已保存");
};

const saveAssistantDefaults = () => {
  systemStore.updateSettings({
    assistantDefaults: { ...assistantDefaults },
  });
  ElMessage.success("创作助手默认设置已保存");
};

onMounted(async () => {
  await fetchPromptTemplates();
  await fetchAiModels();

  // 加载已保存的设置
  Object.assign(chatDefaults, systemStore.settings.chatDefaults);
  Object.assign(assistantDefaults, systemStore.settings.assistantDefaults);

  await fetchGenres();
});

const fetchGenres = async () => {
  try {
    const response = await axios.get("/api/novel-genres");
    genres.value = response.data;
  } catch (error) {
    console.error("Failed to fetch genres:", error);
    ElMessage.error("加载小说类型失败");
  }
};

const editGenre = (genre) => {
  genreForm.id = genre.id;
  genreForm.name = genre.name;
  showGenreDialog.value = true;
};

const saveGenre = async () => {
  if (!genreForm.name.trim()) {
    ElMessage.warning("请输入类型名称");
    return;
  }

  try {
    if (genreForm.id) {
      await axios.put(`/api/novel-genres/${genreForm.id}`, {
        name: genreForm.name,
      });
      ElMessage.success("类型已更新");
    } else {
      await axios.post("/api/novel-genres", { name: genreForm.name });
      ElMessage.success("类型已创建");
    }
    showGenreDialog.value = false;
    genreForm.id = null;
    genreForm.name = "";
    await fetchGenres();
  } catch (error) {
    console.error("Failed to save genre:", error);
    ElMessage.error("保存类型失败");
  }
};

const deleteGenre = async (genre) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除类型"${genre.name}"吗？`,
      "删除确认",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    await axios.delete(`/api/novel-genres/${genre.id}`);
    ElMessage.success("类型已删除");
    await fetchGenres();
  } catch (error) {
    if (error !== "cancel") {
      console.error("Failed to delete genre:", error);
      ElMessage.error("删除类型失败");
    }
  }
};
</script>

<style scoped>
.system-settings-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.system-settings-container h2 {
  margin-bottom: 20px;
  color: #303133;
  font-weight: 600;
}

.settings-form {
  max-width: 800px;
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

:deep(.el-tabs__header) {
  margin-bottom: 25px;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
}

@media (max-width: 768px) {
  .system-settings-container {
    padding: 10px;
  }

  .settings-form {
    padding: 15px;
  }
}

.genres-management {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
