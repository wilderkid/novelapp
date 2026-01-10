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
          <el-breadcrumb-item :to="{ path: '/novels' }"
            >小说管理</el-breadcrumb-item
          >
          <el-breadcrumb-item>{{
            projectStore.currentProject.title
          }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <div class="content-main">
        <!-- 侧边栏收缩按钮 -->
        <div class="sidebar-toggle" @click="toggleSidebar">
          <el-icon>
            <DArrowLeft v-if="sidebarCollapsed" />
            <DArrowRight v-else />
          </el-icon>
        </div>

        <!-- 左侧分卷和章节树形列表 -->
        <div
          class="sidebar"
          v-show="!sidebarCollapsed"
          :style="{ width: sidebarWidth + 'px' }"
        >
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
                    <el-dropdown-item @click="showVolumeDialog = true"
                      >新建分卷</el-dropdown-item
                    >
                    <el-dropdown-item
                      @click="handleNewChapter(null)"
                      :disabled="volumes.length === 0"
                      >新建章节</el-dropdown-item
                    >
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
                  <div
                    class="node-actions"
                    v-if="!data.isFolder || data.id !== 'root'"
                  >
                    <!-- 分卷操作按钮 -->
                    <template v-if="data.type === 'volume'">
                      <el-button
                        size="small"
                        text
                        @click.stop="viewVolume(data)"
                      >
                        <el-icon><View /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        @click.stop="editVolume(data)"
                      >
                        <el-icon><Edit /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        type="danger"
                        @click.stop="confirmDeleteVolume(data)"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        @click.stop="handleNewChapter(data)"
                      >
                        <el-icon><Plus /></el-icon>
                      </el-button>
                    </template>
                    <!-- 章节操作按钮 -->
                    <template v-else-if="data.type === 'chapter'">
                      <el-button
                        size="small"
                        text
                        @click.stop="openChapter(data.chapterData || data)"
                      >
                        <el-icon><View /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        type="danger"
                        @click.stop="
                          confirmDeleteChapter(data.chapterData || data)
                        "
                      >
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
              <el-input
                v-model="currentChapter.title"
                placeholder="章节标题"
                class="title-input"
              />
              <div class="editor-actions">
                <el-button @click="showResourceDrawer = true" :icon="View"
                  >查看资源</el-button
                >
                <el-button @click="saveCurrentChapter">保存</el-button>
              </div>
            </div>
            <div class="editor-content">
              <UEditorPlus
                ref="editorRef"
                v-model="currentChapter.content"
                editor-id="chapter-editor"
                @ready="onEditorReady"
                @auto-save="autoSaveChapter"
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
            <el-input
              v-model="volumeForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入分卷简介"
            />
          </el-form-item>
          <!-- 分卷序号现在由系统自动计算，无需手动输入 -->
          <!-- <el-form-item label="分卷序号">
            <el-input-number v-model="volumeForm.order" :min="1" />
          </el-form-item> -->
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
            <el-input
              v-model="chapterForm.title"
              placeholder="请输入章节标题"
            />
          </el-form-item>
          <el-form-item label="所属分卷">
            <el-select
              v-model="chapterForm.volume_id"
              placeholder="请选择分卷"
              style="width: 100%"
              :disabled="!isVolumeSelectable"
            >
              <el-option
                v-for="volume in volumes"
                :key="volume.id"
                :label="volume.title"
                :value="volume.id"
              />
            </el-select>
          </el-form-item>
          <!-- 章节序号现在由系统自动计算，无需手动输入 -->
          <!-- <el-form-item label="章节序号">
            <el-input-number v-model="chapterForm.order" :min="1" />
          </el-form-item> -->
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
          <div class="volume-header">
            <h3>{{ currentVolume.title }}</h3>
            <el-tag type="info" size="small"
              >第{{ currentVolume.order }}卷</el-tag
            >
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="分卷简介">
              {{ currentVolume.description || "暂无简介" }}
            </el-descriptions-item>
            <el-descriptions-item label="章节数量">
              <el-tag type="success"
                >{{ currentVolume.chapterCount }} 章</el-tag
              >
            </el-descriptions-item>
            <el-descriptions-item label="总字数">
              <el-tag type="warning">{{
                formatWordCount(currentVolume.wordCount)
              }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <div class="chapter-list-section">
            <h4>章节列表</h4>
            <el-table
              :data="getVolumeChapters(currentVolume.id)"
              style="width: 100%"
              size="small"
            >
              <el-table-column type="index" label="序号" width="60">
                <template #header>
                  <el-icon><List /></el-icon> 序号
                </template>
              </el-table-column>
              <el-table-column prop="title" label="章节标题">
                <template #header>
                  <el-icon><Document /></el-icon> 章节标题
                </template>
              </el-table-column>
              <el-table-column prop="wordCount" label="字数" width="100">
                <template #header>
                  <el-icon><DocumentCopy /></el-icon> 字数
                </template>
                <template #default="scope">
                  {{
                    formatWordCount(
                      scope.row.wordCount || scope.row.word_count || 0,
                    )
                  }}
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="更新时间" width="150">
                <template #header>
                  <el-icon><Timer /></el-icon> 更新时间
                </template>
                <template #default="scope">
                  {{ formatDate(scope.row.updated_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-dialog>

      <!-- 资源查看侧边栏 -->
      <el-drawer
        v-model="showResourceDrawer"
        title="资源管理"
        direction="rtl"
        size="400px"
      >
        <div class="resource-drawer-content">
          <el-collapse v-model="activeResourceTypes" accordion>
            <el-collapse-item title="角色" name="characters">
              <ul class="resource-readonly-list">
                <li
                  v-for="item in resourceData.characters"
                  :key="item.id"
                  @click="viewResourceDetail('characters', item)"
                >
                  <span class="resource-name">{{ item.name }}</span>
                  <el-icon><ArrowRight /></el-icon>
                </li>
              </ul>
            </el-collapse-item>
            <el-collapse-item title="组织" name="organizations">
              <ul class="resource-readonly-list">
                <li
                  v-for="item in resourceData.organizations"
                  :key="item.id"
                  @click="viewResourceDetail('organizations', item)"
                >
                  <span class="resource-name">{{ item.name }}</span>
                  <el-icon><ArrowRight /></el-icon>
                </li>
              </ul>
            </el-collapse-item>
            <el-collapse-item title="超凡力量" name="powers">
              <ul class="resource-readonly-list">
                <li
                  v-for="item in resourceData.powers"
                  :key="item.id"
                  @click="viewResourceDetail('powers', item)"
                >
                  <span class="resource-name">{{ item.name }}</span>
                  <el-icon><ArrowRight /></el-icon>
                </li>
              </ul>
            </el-collapse-item>
            <el-collapse-item title="武器" name="weapons">
              <ul class="resource-readonly-list">
                <li
                  v-for="item in resourceData.weapons"
                  :key="item.id"
                  @click="viewResourceDetail('weapons', item)"
                >
                  <span class="resource-name">{{ item.name }}</span>
                  <el-icon><ArrowRight /></el-icon>
                </li>
              </ul>
            </el-collapse-item>
            <el-collapse-item title="副本" name="dungeons">
              <ul class="resource-readonly-list">
                <li
                  v-for="item in resourceData.dungeons"
                  :key="item.id"
                  @click="viewResourceDetail('dungeons', item)"
                >
                  <span class="resource-name">{{ item.name }}</span>
                  <el-icon><ArrowRight /></el-icon>
                </li>
              </ul>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-drawer>

      <!-- 资源详情对话框 -->
      <el-dialog
        v-model="showResourceDetailDialog"
        :title="currentResourceDetail?.name"
        width="600px"
        class="resource-detail-dialog"
      >
        <el-descriptions :column="1" border v-if="currentResourceDetail">
          <el-descriptions-item
            v-for="(value, key) in getResourceFields(currentResourceDetail)"
            :key="key"
            :label="key"
          >
            <div class="resource-field-content" v-html="value"></div>
          </el-descriptions-item>
        </el-descriptions>
      </el-dialog>
    </template>
  </div>
</template>

<script setup>
import {
  ref,
  reactive,
  onMounted,
  watch,
  computed,
  nextTick,
  onBeforeUnmount,
} from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  View,
  Edit,
  Delete,
  List,
  Document,
  DocumentCopy,
  Timer,
  DArrowLeft,
  DArrowRight,
  ArrowRight,
} from "@element-plus/icons-vue";
import { useEditorStore } from "../stores/editorStore";
import { useProjectStore } from "../stores/projectStore";
import UEditorPlus from "../components/UEditorPlus_New.vue";
import chapterService from "../services/chapterService";
import volumeService from "../services/volumeService";
import {
  characterService,
  organizationService,
  supernaturalPowerService,
  weaponService,
  dungeonService,
} from "../services/resourceService";

// 状态管理
const router = useRouter();
const editorStore = useEditorStore();
const projectStore = useProjectStore();

// 对话框状态
const showVolumeDialog = ref(false);
const showChapterDialog = ref(false);
const showVolumeDetailDialog = ref(false);
const isEditingVolume = ref(false);
const isEditingChapter = ref(false);
const isVolumeSelectable = ref(true);

// 资源侧边栏状态
const showResourceDrawer = ref(false);
const activeResourceTypes = ref(["characters"]);
const resourceData = ref({
  characters: [],
  organizations: [],
  powers: [],
  weapons: [],
  dungeons: [],
});

// 资源详情对话框
const showResourceDetailDialog = ref(false);
const currentResourceDetail = ref(null);

// 分卷表单
const volumeForm = ref({
  id: null,
  title: "",
  description: "",
  order: 1, // 这个将由系统自动计算
  project_id: null,
});

// 计算下一个分卷序号
const getNextVolumeOrder = () => {
  if (volumes.value.length === 0) {
    return 1;
  }
  const maxOrder = Math.max(...volumes.value.map((v) => v.order || 0));
  return maxOrder + 1;
};

// 章节表单
const chapterForm = ref({
  id: null,
  title: "",
  volume_id: null,
  order: 1, // 这个将由系统自动计算
  project_id: null,
});

// 计算指定分卷下的下一个章节序号
const getNextChapterOrder = (volumeId) => {
  const volumeChapters = chapters.value.filter((chapter) => {
    const chapterVolumeId = chapter.volumeId || chapter.volume_id;
    return chapterVolumeId === volumeId;
  });

  if (volumeChapters.length === 0) {
    return 1;
  }

  const maxOrder = Math.max(...volumeChapters.map((c) => c.order || 0));
  return maxOrder + 1;
};

// 当前查看的分卷
const currentVolume = ref(null);

// 当前选中的分卷ID（用于新建章节）
const currentVolumeId = ref(null);

// 当前编辑的章节
const currentChapter = ref(null);

// 自动保存相关
const isSaving = ref(false);
const lastSaveTime = ref(null);

// 分卷数据
const volumes = ref([
  {
    id: 1,
    title: "第一卷：初入江湖",
    description: "主角初入江湖，结识伙伴，开始冒险旅程",
    order: 1,
    chapterCount: 2,
    wordCount: 11000,
  },
  {
    id: 2,
    title: "第二卷：风云变幻",
    description: "江湖风波四起，主角面临重大考验",
    order: 2,
    chapterCount: 1,
    wordCount: 5500,
  },
]);

// 章节数据
const chapters = ref([
  {
    id: 1,
    title: "第一章：初出茅庐",
    content: "<p>这是第一章的内容...</p>",
    wordCount: 5000,
    volumeId: 1,
    volumeTitle: "第一卷：初入江湖",
    order: 1,
    created_at: "2023-01-01T00:00:00Z",
    updated_at: "2023-01-02T00:00:00Z",
  },
  {
    id: 2,
    title: "第二章：奇遇",
    content: "<p>这是第二章的内容...</p>",
    wordCount: 6000,
    volumeId: 1,
    volumeTitle: "第一卷：初入江湖",
    order: 2,
    created_at: "2023-01-03T00:00:00Z",
    updated_at: "2023-01-04T00:00:00Z",
  },
  {
    id: 3,
    title: "第三章：危机四伏",
    content: "<p>这是第三章的内容...</p>",
    wordCount: 5500,
    volumeId: 2,
    volumeTitle: "第二卷：风云变幻",
    order: 1,
    created_at: "2023-02-01T00:00:00Z",
    updated_at: "2023-02-02T00:00:00Z",
  },
]);

// 打开的章节数据（用于标签页）
const openChapters = ref([]);
const activeTab = ref("");

// 树形展开的节点
const expandedKeys = ref([]);

// 编辑器容器引用
const editorContainer = ref(null);

// 容器宽度调整
const sidebarWidth = ref(300);
const sidebarCollapsed = ref(false);
const isResizing = ref(false);
const startX = ref(0);
const startWidth = ref(0);

// 切换侧边栏显示/隐藏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

// 拖动排序相关
const treeContainer = ref(null);

// 计算属性
// 构建树形数据
const volumeTreeData = computed(() => {
  console.log("=== 构建树形数据 ===");
  console.log("volumes数据:", volumes.value);
  console.log("chapters数据:", chapters.value);

  const tree = [];

  volumes.value.forEach((volume) => {
    console.log(`处理分卷 ${volume.id}:`, volume);
    const volumeNode = {
      id: `volume-${volume.id}`,
      label: volume.title,
      type: "volume",
      children: [],
    };

    // 获取该分卷下的章节
    const volumeChapters = chapters.value
      .filter((chapter) => {
        // 检查字段名 - 可能是 volume_id 而不是 volumeId
        const chapterVolumeId = chapter.volumeId || chapter.volume_id;
        const match = chapterVolumeId === volume.id;
        console.log(
          `章节 ${chapter.id} volumeId/volume_id: ${chapterVolumeId}, 分卷ID: ${volume.id}, 匹配: ${match}`,
        );
        console.log(`章节完整数据:`, chapter);
        return match;
      })
      .sort((a, b) => a.order - b.order);

    console.log(`分卷 ${volume.id} 下的章节:`, volumeChapters);

    volumeChapters.forEach((chapter) => {
      volumeNode.children.push({
        id: `chapter-${chapter.id}`,
        label: chapter.title,
        type: "chapter",
        chapterData: chapter,
      });
    });

    tree.push(volumeNode);
    console.log(`分卷 ${volume.id} 节点:`, volumeNode);
  });

  console.log("最终树形数据:", tree);
  return tree;
});

// 方法
const goToNovels = () => {
  router.push("/novels");
};

// 处理树节点点击
const handleNodeClick = (data) => {
  if (data.type === "volume") {
    // 点击分卷，展开/折叠
    const volumeId = data.id;
    const index = expandedKeys.value.indexOf(volumeId);
    if (index > -1) {
      expandedKeys.value.splice(index, 1);
    } else {
      expandedKeys.value.push(volumeId);
    }
  } else if (data.type === "chapter") {
    // 点击章节，打开章节编辑
    openChapter(data.chapterData);
  }
};

// 打开章节
const openChapter = async (chapter) => {
  try {
    // 从数据库加载完整的章节数据
    const chapterData = await chapterService.getChapter(chapter.id);

    // 设置当前编辑的章节
    currentChapter.value = { ...chapterData };
  } catch (error) {
    console.error("加载章节数据失败:", error);
    ElMessage.error(
      "加载章节数据失败: " + (error.response?.data?.message || error.message),
    );

    // 如果加载失败，使用本地数据
    currentChapter.value = { ...chapter };
  }
};

// 加载分卷和章节数据
const loadVolumesAndChapters = async () => {
  if (!projectStore.currentProject) {
    console.log("没有当前项目，跳过数据加载");
    return;
  }

  try {
    console.log("=== 开始加载分卷和章节数据 ===");
    console.log("当前项目ID:", projectStore.currentProject.id);

    // 加载分卷数据
    console.log("加载分卷数据...");
    const volumesData = await volumeService.getVolumes(
      projectStore.currentProject.id,
    );
    console.log("分卷数据加载成功:", volumesData);
    volumes.value = volumesData;

    // 加载所有分卷的章节数据
    console.log("加载章节数据...");
    const chaptersData = [];
    for (const volume of volumesData) {
      console.log(`加载分卷 ${volume.id} 的章节...`);
      const volumeChapters = await chapterService.getChapters(volume.id);
      console.log(`分卷 ${volume.id} 章节数据:`, volumeChapters);
      console.log(`分卷 ${volume.id} 章节数量:`, volumeChapters.length);

      // 检查章节数据格式
      if (volumeChapters.length > 0) {
        console.log("第一个章节数据格式:", volumeChapters[0]);
        console.log("章节字段:", Object.keys(volumeChapters[0]));
      }

      chaptersData.push(...volumeChapters);
    }
    console.log("所有章节数据:", chaptersData);
    console.log("总章节数量:", chaptersData.length);
    chapters.value = chaptersData;

    // 默认展开第一个分卷
    if (volumesData.length > 0) {
      expandedKeys.value = [`volume-${volumesData[0].id}`];
      console.log("默认展开分卷:", `volume-${volumesData[0].id}`);
    }

    console.log("=== 数据加载完成 ===");
  } catch (error) {
    console.error("加载数据失败:", error);
    ElMessage.error(
      "加载数据失败: " + (error.response?.data?.message || error.message),
    );
  }
};

// 加载资源数据
const loadResourceData = async () => {
  if (!projectStore.currentProject) return;

  try {
    const [characters, organizations, powers, weapons, dungeons] =
      await Promise.all([
        characterService.getAll(projectStore.currentProject.id),
        organizationService.getAll(projectStore.currentProject.id),
        supernaturalPowerService.getAll(projectStore.currentProject.id),
        weaponService.getAll(projectStore.currentProject.id),
        dungeonService.getAll(projectStore.currentProject.id),
      ]);

    resourceData.value = {
      characters: characters.data,
      organizations: organizations.data,
      powers: powers.data,
      weapons: weapons.data,
      dungeons: dungeons.data,
    };
  } catch (error) {
    console.error("加载资源数据失败:", error);
  }
};

// 自动保存章节
const autoSaveChapter = async () => {
  if (!currentChapter.value || isSaving.value) return;

  try {
    isSaving.value = true;

    // 计算字数
    const content = currentChapter.value.content || "";
    const textContent = content.replace(/<[^>]*>/g, "").trim();
    const wordCount = textContent.length || 0;
    currentChapter.value.wordCount = wordCount;

    // 保存到数据库
    await chapterService.saveChapter(currentChapter.value);

    lastSaveTime.value = new Date();
    ElMessage.success({
      message: "自动保存成功",
      duration: 1000,
      showClose: false,
    });
  } catch (error) {
    console.error("自动保存失败:", error);
  } finally {
    isSaving.value = false;
  }
};

// 保存当前章节（手动保存）
const saveCurrentChapter = async () => {
  if (!currentChapter.value) return;

  if (!currentChapter.value.title) {
    ElMessage.warning("请填写章节标题");
    return;
  }

  try {
    isSaving.value = true;

    // 计算字数（移除HTML标签后）
    const content = currentChapter.value.content || "";
    const textContent = content.replace(/<[^>]*>/g, "").trim();
    const wordCount = textContent.length || 0;

    // 更新字数
    currentChapter.value.wordCount = wordCount;

    // 保存到数据库
    const savedChapter = await chapterService.saveChapter(currentChapter.value);

    // 重新加载数据以确保数据同步
    await loadVolumesAndChapters();

    // 更新当前编辑的章节
    currentChapter.value = savedChapter;

    lastSaveTime.value = new Date();
    ElMessage.success("章节已保存到数据库");
  } catch (error) {
    console.error("保存章节失败:", error);
    ElMessage.error(
      "保存章节失败: " + (error.response?.data?.message || error.message),
    );
  } finally {
    isSaving.value = false;
  }
};

// 关闭标签页
const removeTab = (targetName) => {
  const index = openChapters.value.findIndex(
    (c) => c.id.toString() === targetName,
  );
  if (index > -1) {
    openChapters.value.splice(index, 1);

    // 如果关闭的是当前激活的标签页，则激活另一个
    if (activeTab.value === targetName) {
      if (openChapters.value.length > 0) {
        activeTab.value =
          openChapters.value[Math.max(0, index - 1)].id.toString();
      } else {
        activeTab.value = "";
      }
    }
  }
};

// 格式化字数
const formatWordCount = (count) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + "万字";
  }
  return count + "字";
};

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString() + " " + date.toLocaleTimeString();
};

// 获取分卷下的章节
const getVolumeChapters = (volumeId) => {
  return chapters.value
    .filter((chapter) => {
      const chapterVolumeId = chapter.volumeId || chapter.volume_id;
      return chapterVolumeId === volumeId;
    })
    .map((chapter) => {
      // 确保章节有正确的字数数据
      const content = chapter.content || "";
      const textContent = content.replace(/<[^>]*>/g, "").trim();
      const calculatedWordCount = textContent.length || 0;

      return {
        ...chapter,
        wordCount:
          chapter.wordCount || chapter.word_count || calculatedWordCount,
      };
    });
};

// 查看分卷
const viewVolume = (volume) => {
  // 从树节点ID中提取真实的分卷ID
  const volumeId = volume.id.replace("volume-", "");

  // 找到对应的分卷数据
  const volumeData = volumes.value.find((v) => v.id.toString() === volumeId);

  if (volumeData) {
    // 计算该分卷的章节数和总字数
    const volumeChapters = chapters.value.filter((chapter) => {
      const chapterVolumeId = chapter.volumeId || chapter.volume_id;
      return chapterVolumeId.toString() === volumeId;
    });

    const chapterCount = volumeChapters.length;
    const wordCount = volumeChapters.reduce((total, chapter) => {
      // 计算章节内容的实际字数
      const content = chapter.content || "";
      // 移除HTML标签后计算字数
      const textContent = content.replace(/<[^>]*>/g, "").trim();
      const chapterWordCount = textContent.length || chapter.wordCount || 0;
      return total + chapterWordCount;
    }, 0);

    // 创建包含统计信息的分卷对象
    currentVolume.value = {
      ...volumeData,
      chapterCount: chapterCount,
      wordCount: wordCount,
    };

    console.log("查看分卷详情:", currentVolume.value);
    showVolumeDetailDialog.value = true;
  } else {
    ElMessage.error("找不到分卷数据");
  }
};

// 编辑分卷
const editVolume = (volume) => {
  // 从树节点ID中提取真实的分卷ID
  const volumeId = volume.id.replace("volume-", "");

  // 找到对应的分卷数据
  const volumeData = volumes.value.find((v) => v.id.toString() === volumeId);

  if (volumeData) {
    isEditingVolume.value = true;
    volumeForm.value = { ...volumeData };
    showVolumeDialog.value = true;
    console.log("编辑分卷:", volumeForm.value);
  } else {
    ElMessage.error("找不到分卷数据");
  }
};

// 保存分卷
const saveVolume = async () => {
  if (!volumeForm.value.title) {
    ElMessage.warning("请填写分卷标题");
    return;
  }

  try {
    // 自动计算分卷序号（仅在创建新分卷时）
    let nextOrder = volumeForm.value.order;
    if (!isEditingVolume.value) {
      nextOrder = getNextVolumeOrder();
      console.log("自动计算分卷序号:", nextOrder);
    }

    // 准备保存数据
    let volumeData;
    if (isEditingVolume.value) {
      // 编辑模式：保留id字段
      volumeData = {
        ...volumeForm.value,
        order: nextOrder,
        project_id: projectStore.currentProject.id,
      };
    } else {
      // 创建模式：移除id字段
      const { id, ...volumeDataWithoutId } = volumeForm.value;
      volumeData = {
        ...volumeDataWithoutId,
        order: nextOrder,
        project_id: projectStore.currentProject.id,
      };
    }

    // 保存到数据库
    const savedVolume = await volumeService.saveVolume(volumeData);

    // 重新加载数据以确保数据同步
    await loadVolumesAndChapters();

    if (isEditingVolume.value) {
      ElMessage.success("分卷信息已更新");
    } else {
      ElMessage.success(`分卷创建成功，序号为第${nextOrder}卷`);
      // 展开新创建的分卷
      expandedKeys.value.push(`volume-${savedVolume.id}`);
    }

    // 重置表单和关闭对话框
    resetVolumeForm();
    showVolumeDialog.value = false;
  } catch (error) {
    console.error("保存分卷失败:", error);
    ElMessage.error(
      "保存分卷失败: " + (error.response?.data?.message || error.message),
    );
  }
};

// 确认删除分卷
const confirmDeleteVolume = async (volume) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分卷《${volume.title}》吗？此操作不可恢复！`,
      "删除确认",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    // 从树节点ID中提取真实的分卷ID
    const volumeId = volume.id.replace("volume-", "");

    // 调用后端API删除分卷
    await volumeService.deleteVolume(volumeId);

    // 重新加载数据
    await loadVolumesAndChapters();

    ElMessage.success("分卷已删除");
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除分卷失败:", error);
      ElMessage.error(
        "删除分卷失败: " + (error.response?.data?.message || error.message),
      );
    }
  }
};

// 重置分卷表单
const resetVolumeForm = () => {
  volumeForm.value = {
    id: null,
    title: "",
    description: "",
    order: getNextVolumeOrder(), // 自动计算下一个序号
    project_id: null,
  };
  isEditingVolume.value = false;
};

// 处理新建章节（全局或指定分卷）
const handleNewChapter = (volumeNode = null) => {
  resetChapterForm();
  isEditingChapter.value = false;

  if (volumeNode) {
    // 从分卷节点添加章节
    const volumeId = parseInt(volumeNode.id.replace("volume-", ""));
    chapterForm.value.volume_id = volumeId;
    isVolumeSelectable.value = false; // 锁定分卷选择
  } else {
    // 从全局按钮添加章节
    isVolumeSelectable.value = true; // 开放分卷选择
  }
  showChapterDialog.value = true;
};

// 编辑章节
const editChapter = (chapter) => {
  isEditingChapter.value = true;
  chapterForm.value = { ...chapter };
  showChapterDialog.value = true;
};

// 保存章节
const saveChapter = (chapter) => {
  if (!chapter.title) {
    ElMessage.warning("请填写章节标题");
    return;
  }

  // 更新章节数据
  const index = chapters.value.findIndex((c) => c.id === chapter.id);
  if (index !== -1) {
    chapters.value[index] = {
      ...chapters.value[index],
      ...chapter,
      updated_at: new Date().toISOString(),
    };

    // 更新打开的章节数据
    const openIndex = openChapters.value.findIndex((c) => c.id === chapter.id);
    if (openIndex > -1) {
      // 使用打开的章节数据更新，因为这里包含了最新的编辑内容
      chapters.value[index] = {
        ...chapters.value[index],
        ...openChapters.value[openIndex],
        updated_at: new Date().toISOString(),
      };
    }

    ElMessage.success("章节已保存");
  }
};

// 保存章节表单
const saveChapterForm = async () => {
  if (!chapterForm.value.title || !chapterForm.value.volume_id) {
    ElMessage.warning("请填写章节标题和所属分卷");
    return;
  }

  try {
    console.log("=== 开始保存章节 ===");
    console.log("章节表单数据:", chapterForm.value);
    console.log("当前项目ID:", projectStore.currentProject?.id);

    if (isEditingChapter.value) {
      // 更新现有章节 - 调用后端API
      console.log("更新现有章节，ID:", chapterForm.value.id);

      // 计算字数（移除HTML标签后）
      const content = chapterForm.value.content || "";
      const textContent = content.replace(/<[^>]*>/g, "").trim();
      const wordCount = textContent.length || 0;

      const updatedChapterData = {
        ...chapterForm.value,
        wordCount: wordCount,
      };

      const updatedChapter =
        await chapterService.saveChapter(updatedChapterData);
      console.log("更新成功，返回数据:", updatedChapter);
      ElMessage.success("章节信息已更新");

      // 重新加载数据以确保树形组件正确更新
      await loadVolumesAndChapters();
    } else {
      // 创建新章节 - 调用后端API
      console.log("创建新章节");

      // 自动计算章节序号
      const nextOrder = getNextChapterOrder(chapterForm.value.volume_id);
      console.log("自动计算章节序号:", nextOrder);

      // 创建新章节时，移除id字段（因为id由数据库自动生成）
      const { id, ...chapterDataWithoutId } = chapterForm.value;
      const chapterData = {
        ...chapterDataWithoutId,
        order: nextOrder, // 使用自动计算的序号
        project_id: projectStore.currentProject.id,
        content: "<p>请输入章节内容...</p>",
        wordCount: 0,
      };

      console.log("发送的章节数据:", chapterData);
      const newChapter = await chapterService.saveChapter(chapterData);
      console.log("创建成功，返回数据:", newChapter);
      console.log("新章节ID:", newChapter.id);
      console.log("新章节标题:", newChapter.title);
      console.log("新章节volume_id:", newChapter.volume_id);
      console.log("新章节完整字段:", Object.keys(newChapter));
      ElMessage.success(`章节创建成功，序号为第${nextOrder}章`);

      // 重新加载数据以确保树形组件正确更新
      await loadVolumesAndChapters();

      // 展开包含新章节的分卷
      expandedKeys.value.push(`volume-${newChapter.volume_id}`);
      console.log("展开分卷:", `volume-${newChapter.volume_id}`);
    }

    // 重置表单和关闭对话框
    resetChapterForm();
    showChapterDialog.value = false;
    console.log("=== 保存章节完成 ===");
  } catch (error) {
    console.error("保存章节失败:", error);
    console.error("错误详情:", error.response?.data);
    ElMessage.error(
      "保存章节失败: " + (error.response?.data?.message || error.message),
    );
  }
};

// 确认删除章节
const confirmDeleteChapter = async (chapter) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除章节《${chapter.title}》吗？此操作不可恢复！`,
      "删除确认",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    // 从树节点ID中提取真实的章节ID
    const chapterId = chapter.id.toString().replace("chapter-", "");

    // 调用后端API删除章节
    await chapterService.deleteChapter(chapterId);

    // 重新加载数据
    await loadVolumesAndChapters();

    // 如果章节已打开，则关闭
    const openIndex = openChapters.value.findIndex((c) => c.id === chapter.id);
    if (openIndex > -1) {
      removeTab(chapter.id.toString());
    }

    // 更新分卷的章节数（使用正确的字段名）
    const chapterVolumeId = chapter.volumeId || chapter.volume_id;
    const volume = volumes.value.find((v) => v.id === chapterVolumeId);
    if (volume) {
      volume.chapterCount = Math.max(0, (volume.chapterCount || 0) - 1);
    }

    ElMessage.success("章节已删除");
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除章节失败:", error);
      ElMessage.error(
        "删除章节失败: " + (error.response?.data?.message || error.message),
      );
    }
  }
};

// 重置章节表单
const resetChapterForm = () => {
  // 自动计算章节序号（仅在创建新章节时）
  let nextOrder = 1;
  if (!isEditingChapter.value && currentVolumeId.value) {
    nextOrder = getNextChapterOrder(currentVolumeId.value);
    console.log("自动计算章节序号:", nextOrder);
  }

  chapterForm.value = {
    id: null,
    title: "",
    volume_id: currentVolumeId.value || null,
    order: nextOrder, // 使用自动计算的序号
    project_id: projectStore.currentProject?.id || null,
  };
  isEditingChapter.value = false;
};

// 容器宽度调整方法
const initResize = () => {
  const resizeBar = document.querySelector(".resize-bar");
  if (!resizeBar) return;

  resizeBar.addEventListener("mousedown", (e) => {
    isResizing.value = true;
    startX.value = e.clientX;
    startWidth.value = sidebarWidth.value;

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    e.preventDefault();
  });
};

const handleMouseMove = (e) => {
  if (!isResizing.value) return;

  const diff = e.clientX - startX.value;
  const newWidth = startWidth.value + diff;

  // 限制最小和最大宽度
  if (newWidth >= 200 && newWidth <= 500) {
    sidebarWidth.value = newWidth;
  }
};

const handleMouseUp = () => {
  isResizing.value = false;
  document.removeEventListener("mousemove", handleMouseMove);
  document.removeEventListener("mouseup", handleMouseUp);
};

// 更新章节顺序
const updateChapterOrder = (volumeId) => {
  const volumeChapters = chapters.value
    .filter((c) => c.volumeId === volumeId)
    .sort((a, b) => a.order - b.order);

  const treeElement = treeContainer.value.querySelector(
    `[data-id="volume-${volumeId}"] .el-tree-node__children`,
  );
  if (!treeElement) return;

  const chapterNodes = treeElement.querySelectorAll(".el-tree-node");

  chapterNodes.forEach((node, index) => {
    const nodeId = node.getAttribute("data-id");
    if (nodeId && nodeId.startsWith("chapter-")) {
      const chapterId = parseInt(nodeId.replace("chapter-", ""));
      const chapter = chapters.value.find((c) => c.id === chapterId);
      if (chapter) {
        chapter.order = index + 1;
      }
    }
  });
};

// 拖拽相关方法
const allowDrag = (draggingNode) => {
  // 只允许拖拽章节节点
  return draggingNode.data.type === "chapter";
};

const allowDrop = (draggingNode, dropNode, type) => {
  // 只允许拖拽到章节列表中，不允许拖拽到分卷上
  if (type === "inner") {
    return dropNode.data.type === "volume";
  }
  return dropNode.data.type === "chapter" || dropNode.data.type === "volume";
};

const handleDragStart = (node, ev) => {
  // 设置拖拽样式
  ev.dataTransfer.effectAllowed = "move";
};

const handleDragEnd = (draggingNode, dropNode, dropType, ev) => {
  if (!dropNode || dropType === null) return;

  // 获取拖拽的章节ID
  const chapterId = parseInt(draggingNode.data.id.replace("chapter-", ""));

  // 获取目标分卷ID
  let targetVolumeId;

  if (dropType === "inner") {
    // 拖拽到分卷内部
    targetVolumeId = parseInt(dropNode.data.id.replace("volume-", ""));
  } else {
    // 拖拽到章节旁边
    const parentVolumeNode = dropNode.parent;
    if (parentVolumeNode && parentVolumeNode.data.type === "volume") {
      targetVolumeId = parseInt(
        parentVolumeNode.data.id.replace("volume-", ""),
      );
    }
  }

  if (!targetVolumeId) return;

  // 更新章节数据
  const chapter = chapters.value.find((c) => c.id === chapterId);
  if (chapter) {
    // 如果分卷发生变化
    if (chapter.volumeId !== targetVolumeId) {
      // 更新旧分卷的章节数
      const oldVolume = volumes.value.find((v) => v.id === chapter.volumeId);
      if (oldVolume) {
        oldVolume.chapterCount = Math.max(0, (oldVolume.chapterCount || 0) - 1);
      }

      // 更新新分卷的章节数
      const newVolume = volumes.value.find((v) => v.id === targetVolumeId);
      if (newVolume) {
        newVolume.chapterCount = (newVolume.chapterCount || 0) + 1;
      }

      // 更新章节所属分卷
      chapter.volumeId = targetVolumeId;
      const volume = volumes.value.find((v) => v.id === targetVolumeId);
      chapter.volumeTitle = volume ? volume.title : "";
    }

    // 更新章节顺序
    updateChapterOrder(targetVolumeId);

    ElMessage.success("章节位置已更新");
  }
};

// 编辑器准备就绪
const onEditorReady = (editor) => {
  // 编辑器准备就绪后的处理
  console.log("编辑器准备就绪", editor);
};

// 编辑器引用
const editorRefs = ref({});

// 标签页切换处理
const handleTabClick = (tab) => {
  // 获取当前章节
  const chapterId = tab.props.name;
  const chapter = openChapters.value.find((c) => c.id.toString() === chapterId);

  if (chapter) {
    // 强制刷新编辑器
    nextTick(() => {
      const editorRef = editorRefs.value[chapterId];
      if (editorRef) {
        // 先销毁旧编辑器
        editorRef.forceRefresh();

        // 确保内容已更新
        setTimeout(() => {
          if (editorRef && editorRef.setContent) {
            editorRef.setContent(chapter.content || "");
          }
        }, 300);
      }
    });
  }
};

// 组件挂载时重置表单
onMounted(() => {
  resetVolumeForm();
  resetChapterForm();
  // 默认展开所有分卷
  expandedKeys.value = volumes.value.map((v) => `volume-${v.id}`);

  // 初始化宽度调整
  nextTick(() => {
    initResize();
  });

  // 加载数据
  if (projectStore.currentProject) {
    loadVolumesAndChapters();
  }
});

// 监听当前项目变化，加载数据
watch(
  () => projectStore.currentProject,
  (newProject) => {
    if (newProject) {
      loadVolumesAndChapters();
    }
  },
  { immediate: true },
);

// 监听资源侧边栏打开，加载资源数据
watch(showResourceDrawer, (newVal) => {
  if (newVal) {
    loadResourceData();
  }
});

// 查看资源详情
const viewResourceDetail = async (type, item) => {
  try {
    let service;
    switch (type) {
      case "characters":
        service = characterService;
        break;
      case "organizations":
        service = organizationService;
        break;
      case "powers":
        service = supernaturalPowerService;
        break;
      case "weapons":
        service = weaponService;
        break;
      case "dungeons":
        service = dungeonService;
        break;
    }

    const response = await service.get(item.id);
    currentResourceDetail.value = response.data;
    showResourceDetailDialog.value = true;
  } catch (error) {
    console.error("加载资源详情失败:", error);
    ElMessage.error("加载资源详情失败");
  }
};

// 获取资源字段（过滤掉不需要显示的字段）
const getResourceFields = (resource) => {
  const excludeFields = [
    "id",
    "project_id",
    "created_at",
    "updated_at",
    "display_order",
  ];
  const fieldLabels = {
    name: "名称",
    description: "描述",
    age: "年龄",
    gender: "性别",
    appearance: "外貌",
    personality: "性格",
    background: "背景",
    abilities: "能力",
    relationships: "关系",
    leader: "领导者",
    members: "成员",
    goals: "目标",
    history: "历史",
    type: "类型",
    effects: "效果",
    limitations: "限制",
    damage: "伤害",
    range: "范围",
    special_properties: "特殊属性",
    location: "位置",
    difficulty: "难度",
    monsters: "怪物",
    rewards: "奖励",
    notes: "备注",
  };

  const fields = {};
  for (const [key, value] of Object.entries(resource)) {
    if (!excludeFields.includes(key) && value !== null && value !== "") {
      fields[fieldLabels[key] || key] = value;
    }
  }
  return fields;
};
</script>

<style scoped>
.chapters-container {
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background-color: #f5f7fa;
}

.content-header {
  margin-bottom: 20px;
  padding: 10px 0;
}

.content-main {
  flex: 1;
  display: flex;
  gap: 20px;
  height: calc(100vh - 100px);
}

/* 左侧分卷和章节树形列表 */
.sidebar {
  min-width: 250px;
  max-width: 400px;
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
  background-color: #fafafa;
  border-radius: 8px 8px 0 0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.tree-container {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  background-color: #fff;
}

.tree-node {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 5px 8px;
  border-radius: 4px;
}

.tree-node:hover {
  background-color: #f5f7fa;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-actions {
  display: none;
  gap: 4px; /* Reduced gap */
  align-items: center;
}

/* Reduce padding on action buttons to make them more compact */
.node-actions :deep(.el-button) {
  padding: 4px;
  margin: 0;
  min-height: auto;
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
  background-color: #fafafa;
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
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.volume-detail {
  padding: 0;
}

.volume-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e6e6e6;
}

.volume-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.volume-detail .el-descriptions {
  margin-bottom: 25px;
}

.chapter-list-section {
  margin-top: 25px;
}

.chapter-list-section h4 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.volume-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
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
  padding: 0 5px;
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

:deep(
  .el-tree-node.is-drop-inner
    > .el-tree-node__content
    .el-tree-node__expand-icon
) {
  color: #1890ff;
}

/* 资源详情对话框 */
.resource-detail-dialog :deep(.el-dialog) {
  max-width: 600px;
}

.resource-detail-dialog :deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
}

/* 强制表格使用固定布局 */
.resource-detail-dialog :deep(.el-descriptions) {
  width: 100%;
  overflow: hidden;
}

.resource-detail-dialog :deep(.el-descriptions__table) {
  table-layout: fixed !important;
  width: 100% !important;
}

/* 标签列固定宽度 */
.resource-detail-dialog :deep(.el-descriptions__label) {
  width: 100px !important;
  word-wrap: break-word !important;
  word-break: break-all !important;
  white-space: normal !important;
  overflow: hidden !important;
}

/* 内容列自动换行 */
.resource-detail-dialog :deep(.el-descriptions__content) {
  word-wrap: break-word !important;
  word-break: break-all !important;
  overflow-wrap: anywhere !important;
  white-space: normal !important;
  overflow: hidden !important;
}

.resource-detail-dialog :deep(.el-descriptions__cell) {
  overflow: hidden !important;
}

/* 资源详情内容 */
.resource-field-content {
  word-wrap: break-word !important;
  word-break: break-all !important;
  overflow-wrap: anywhere !important;
  white-space: normal !important;
  max-width: 100% !important;
  overflow: hidden !important;
  display: block !important;
}

/* 强制所有HTML元素换行 */
.resource-field-content :deep(*) {
  max-width: 100% !important;
  word-wrap: break-word !important;
  word-break: break-all !important;
  white-space: normal !important;
  overflow-wrap: anywhere !important;
  box-sizing: border-box !important;
}

/* 强制图片和其他媒体元素适应容器 */
.resource-field-content :deep(img),
.resource-field-content :deep(video),
.resource-field-content :deep(iframe) {
  max-width: 100% !important;
  height: auto !important;
  display: block !important;
}

/* 强制表格适应容器 */
.resource-field-content :deep(table) {
  max-width: 100% !important;
  table-layout: fixed !important;
  width: 100% !important;
}

/* 强制pre和code标签换行 */
.resource-field-content :deep(pre),
.resource-field-content :deep(code) {
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  overflow-wrap: anywhere !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chapters-container {
    padding: 10px;
  }

  .content-main {
    flex-direction: column;
    height: auto;
  }

  .sidebar {
    min-width: unset;
    max-width: unset;
    width: 100%;
  }

  .editor-area {
    min-height: 500px;
  }

  .editor-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .title-input {
    width: 100%;
  }
}

/* 资源侧边栏样式 */
.resource-drawer-content {
  padding: 0;
}

.resource-readonly-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.resource-readonly-list li {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resource-readonly-list li:last-child {
  border-bottom: none;
}

.resource-readonly-list li:hover {
  background-color: #f5f7fa;
}

.resource-name {
  flex: 1;
}
</style>
