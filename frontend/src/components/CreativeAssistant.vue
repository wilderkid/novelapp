<template>
  <el-aside
    :width="sidebarWidth + 'px'"
    class="creative-assistant-sidebar"
    v-if="creativeAssistantVisible"
    ref="assistantSidebar"
    data-version="20231201"
  >
    <div class="assistant-container">
      <div class="assistant-header">
        <h3>创作助手</h3>
        <div>
          <el-button
            type="text"
            @click="startNewConversation"
            title="开始新对话"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
          <el-button
            type="text"
            @click="clearCurrentMessages"
            title="清除当前对话"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
          <el-button type="text" @click="toggleCollapse">
            <el-icon><Right /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="assistant-content">
        <div class="chat-messages" ref="messagesContainer">
          <transition-group name="message" tag="div">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message-wrapper"
              :class="`message-wrapper-${msg.role}`"
            >
              <div class="message-content-wrapper">
                <div class="avatar" :class="`avatar-${msg.role}`">
                  <el-icon v-if="msg.role === 'assistant'" :size="20"
                    ><ChatLineRound
                  /></el-icon>
                  <el-icon v-else :size="20"><User /></el-icon>
                </div>
                <div class="message" :class="`message-${msg.role}`">
                  <!-- 最终回复 (Assistant) / 加载中 -->
                  <div v-if="msg.role === 'assistant'">
                    <!-- 思考过程 -->
                    <div
                      v-if="msg.hadThinkingProcess"
                      class="thinking-process-container"
                    >
                      <div
                        class="thinking-process-header"
                        @click="
                          msg.showThinkingProcess = !msg.showThinkingProcess
                        "
                      >
                        <div class="thinking-process-title">
                          <el-icon><Files /></el-icon>
                          <span>思考过程</span>
                        </div>
                        <el-button
                          v-if="!msg.isThinking"
                          type="primary"
                          link
                          size="small"
                          class="collapse-button"
                        >
                          {{ msg.showThinkingProcess ? "收起" : "展开" }}
                          <el-icon class="el-icon--right">
                            <ArrowUp v-if="msg.showThinkingProcess" />
                            <ArrowDown v-else />
                          </el-icon>
                        </el-button>
                      </div>
                      <el-collapse-transition>
                        <div v-show="msg.showThinkingProcess">
                          <div
                            class="thinking-process-content markdown-body"
                            :class="{ 'is-thinking': msg.isThinking }"
                            v-html="formatMessage(msg.thinkingContent)"
                          ></div>
                        </div>
                      </el-collapse-transition>
                    </div>

                    <div
                      v-if="msg.content"
                      v-html="formatMessage(msg.content)"
                      class="markdown-body final-answer"
                    ></div>
                    <!-- 加载中提示 -->
                    <div
                      v-if="msg.isThinking && !msg.hadThinkingProcess"
                      class="loading-indicator markdown-body"
                    >
                      <el-icon class="is-loading"><Loading /></el-icon>
                      <span>AI正在思考...</span>
                    </div>
                  </div>

                  <!-- 用户消息 -->
                  <span v-else-if="msg.role === 'user'">{{ msg.content }}</span>
                </div>
              </div>
              <div
                v-if="
                  (msg.role === 'assistant' || msg.role === 'user') &&
                  !isLoading
                "
                class="message-actions"
              >
                <el-button
                  v-if="msg.role === 'assistant'"
                  size="small"
                  circle
                  :icon="CopyDocument"
                  @click="copyMessage(msg.content)"
                  title="复制消息"
                ></el-button>
                <el-button
                  v-if="msg.role === 'assistant'"
                  size="small"
                  circle
                  :icon="Refresh"
                  @click="regenerateResponse(index)"
                  title="重新生成"
                ></el-button>
                <el-button
                  size="small"
                  circle
                  :icon="Delete"
                  @click="deleteMessage(index)"
                  title="删除消息"
                ></el-button>
              </div>
            </div>
          </transition-group>
        </div>
        <div class="chat-input">
          <!-- 已捕获的选中文字提示 -->
          <div v-if="cachedSelectedText" class="captured-text-hint">
            <span class="hint-label">已捕获：</span>
            <span class="hint-text"
              >{{ cachedSelectedText.substring(0, 5)
              }}{{ cachedSelectedText.length > 5 ? "..." : "" }}</span
            >
            <el-button
              type="text"
              :icon="Close"
              @click="clearSelectedText"
              class="clear-button"
              title="清除选中文字"
            ></el-button>
          </div>
          <div class="input-controls">
            <div class="control-buttons">
              <el-dropdown
                trigger="click"
                @command="selectAiModel"
                placement="top-start"
                popper-class="model-dropdown-popper"
              >
                <el-button :icon="Cpu" circle size="small" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="">默认模型</el-dropdown-item>
                    <div
                      v-for="(models, providerName) in groupedAiModels"
                      :key="providerName"
                      class="provider-group"
                    >
                      <div class="provider-group-title">{{ providerName }}</div>
                      <el-dropdown-item
                        v-for="model in models"
                        :key="model.id"
                        :command="model.id"
                        :class="{ 'is-active': selectedAiModelId === model.id }"
                      >
                        {{ model.name }}
                      </el-dropdown-item>
                    </div>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-dropdown
                trigger="click"
                @command="selectPromptTemplate"
                placement="top-start"
                popper-class="prompt-dropdown-popper"
              >
                <el-button :icon="ChatDotRound" circle size="small" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="">无提示词</el-dropdown-item>
                    <el-dropdown-item
                      v-for="item in promptTemplates"
                      :key="item.id"
                      :command="item.id"
                      :class="{
                        'is-active': selectedPromptTemplateId === item.id,
                      }"
                    >
                      {{ item.name }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-dropdown
                trigger="click"
                @command="insertReference"
                placement="top-start"
                popper-class="reference-dropdown-popper"
              >
                <el-button :icon="Link" circle size="small" title="引用库" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <div v-if="!currentProject" class="reference-empty">
                      请先选择项目
                    </div>
                    <template v-else>
                      <div class="provider-group">
                        <div class="provider-group-title">特殊引用</div>
                        <el-dropdown-item command="选择文字"
                          >选择文字</el-dropdown-item
                        >
                      </div>
                      <div v-if="references.worldview" class="provider-group">
                        <div class="provider-group-title">世界观</div>
                        <el-dropdown-item command="世界观"
                          >世界观</el-dropdown-item
                        >
                      </div>
                      <div
                        v-if="references.characters.length > 0"
                        class="provider-group"
                      >
                        <div class="provider-group-title">角色</div>
                        <el-dropdown-item
                          v-for="char in references.characters"
                          :key="char.id"
                          :command="char.name"
                        >
                          {{ char.name }}
                        </el-dropdown-item>
                      </div>
                      <div
                        v-if="references.organizations.length > 0"
                        class="provider-group"
                      >
                        <div class="provider-group-title">组织</div>
                        <el-dropdown-item
                          v-for="org in references.organizations"
                          :key="org.id"
                          :command="org.name"
                        >
                          {{ org.name }}
                        </el-dropdown-item>
                      </div>
                      <div
                        v-if="references.powers.length > 0"
                        class="provider-group"
                      >
                        <div class="provider-group-title">超自然力量</div>
                        <el-dropdown-item
                          v-for="power in references.powers"
                          :key="power.id"
                          :command="power.name"
                        >
                          {{ power.name }}
                        </el-dropdown-item>
                      </div>
                      <div
                        v-if="references.weapons.length > 0"
                        class="provider-group"
                      >
                        <div class="provider-group-title">武器</div>
                        <el-dropdown-item
                          v-for="weapon in references.weapons"
                          :key="weapon.id"
                          :command="weapon.name"
                        >
                          {{ weapon.name }}
                        </el-dropdown-item>
                      </div>
                      <div
                        v-if="references.dungeons.length > 0"
                        class="provider-group"
                      >
                        <div class="provider-group-title">副本</div>
                        <el-dropdown-item
                          v-for="dungeon in references.dungeons"
                          :key="dungeon.id"
                          :command="dungeon.name"
                        >
                          {{ dungeon.name }}
                        </el-dropdown-item>
                      </div>
                    </template>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button
                :icon="Setting"
                circle
                size="small"
                @click="showSettingsDialog = true"
              />
            </div>
            <div class="control-item">
              <span class="control-label" v-if="selectedAiModelId">
                {{ getAiModelName(selectedAiModelId) }}
              </span>
              <span class="control-label" v-if="selectedPromptTemplateId">
                {{ getPromptTemplateName(selectedPromptTemplateId) }}
              </span>
            </div>
          </div>
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="4"
            placeholder="请输入提示词... (Shift+Enter 换行)"
            @keydown.enter.prevent="handleEnter"
          />
          <div class="input-actions">
            <el-button
              type="primary"
              @click.stop="sendMessage()"
              :loading="isLoading"
              :disabled="isLoading"
              :icon="Promotion"
            >
              <span v-if="!isLoading">发送</span>
              <span v-else>AI正在输出...</span>
            </el-button>
            <el-button
              @click.stop="insertIntoEditor"
              :disabled="!activeEditorInstance || !lastAiResponse"
              title="将最后一条AI回复插入编辑器"
              :icon="DocumentCopy"
            >
              写入编辑器
            </el-button>
          </div>
        </div>
      </div>
    </div>
    <div class="resize-bar"></div>

    <!-- AI参数设置对话框 -->
    <el-dialog
      v-model="showSettingsDialog"
      title="AI调用参数设置"
      width="400px"
    >
      <el-form label-width="100px">
        <el-form-item label="温度">
          <el-input-number
            v-model="aiSettings.temperature"
            :min="0"
            :max="1"
            :step="0.1"
            :precision="1"
          />
          <div class="form-item-tip">控制输出的随机性，0-1之间</div>
        </el-form-item>
        <el-form-item label="最大Token">
          <el-input-number
            v-model="aiSettings.maxTokens"
            :min="100"
            :max="1000000"
            :step="100"
          />
          <div class="form-item-tip">限制AI回复的最大长度</div>
        </el-form-item>
        <el-form-item label="记忆轮数">
          <el-input-number
            v-model="aiSettings.memoryRounds"
            :min="1"
            :max="200"
            :step="1"
          />
          <div class="form-item-tip">保留最近N轮对话作为上下文</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSettingsDialog = false">取消</el-button>
        <el-button type="primary" @click="showSettingsDialog = false"
          >确定</el-button
        >
      </template>
    </el-dialog>
  </el-aside>
</template>

<script setup>
import {
  ref,
  computed,
  onMounted,
  onUnmounted,
  nextTick,
  watch,
  getCurrentInstance,
} from "vue";
import { useEditorStore } from "../stores/editorStore";
import { useProjectStore } from "../stores/projectStore";
import { useConversationStore } from "../stores/conversationStore";
import { useSystemStore } from "../stores/systemStore";
import { ElMessage, ElMessageBox } from "element-plus";
import axios from "axios";
import {
  Right,
  ChatDotRound,
  Setting,
  CopyDocument,
  Refresh,
  ChatLineRound,
  User,
  Delete,
  Promotion,
  DocumentCopy,
  Files,
  ArrowDown,
  ArrowUp,
  Loading,
  Close,
  Cpu,
  Link,
} from "@element-plus/icons-vue";
import MarkdownIt from "markdown-it";
import {
  worldviewService,
  characterService,
  organizationService,
  supernaturalPowerService,
  weaponService,
  dungeonService,
} from "../services/resourceService";

const editorStore = useEditorStore();
const projectStore = useProjectStore();
const conversationStore = useConversationStore();
const systemStore = useSystemStore();
const userInput = ref("");
// Add a conversation ID to track the conversation in the creative assistant
const conversationId = ref(null);
const messages = ref([]); // Keep local messages for the temporary creative assistant session
const isLoading = ref(false);
const messagesContainer = ref(null);
const instance = getCurrentInstance();
const forceUpdate = () => {
  instance?.proxy?.$forceUpdate();
};

const promptTemplates = ref([]);
const aiModels = ref([]);
const selectedPromptTemplateId = ref(null);
const selectedAiModelId = ref(null);

// AI调用参数设置
const showSettingsDialog = ref(false);
const aiSettings = ref({
  temperature: systemStore.settings.assistantDefaults?.temperature ?? 0.7,
  maxTokens: systemStore.settings.assistantDefaults?.maxTokens ?? 2000,
  memoryRounds: systemStore.settings.assistantDefaults?.memoryRounds ?? 10,
});

const activeEditorInstance = computed(() => editorStore.activeEditorInstance);
const creativeAssistantVisible = computed(
  () => editorStore.creativeAssistantVisible,
);
const currentProject = computed(() => projectStore.currentProject);
const cachedSelectedText = computed(() => editorStore.cachedSelectedText);

// 引用库数据
const references = ref({
  worldview: null,
  characters: [],
  organizations: [],
  powers: [],
  weapons: [],
  dungeons: [],
});

const lastAiResponse = computed(() => {
  const aiMessages = messages.value.filter((m) => m.role === "assistant");
  return aiMessages.length > 0
    ? aiMessages[aiMessages.length - 1].content
    : null;
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

const md = new MarkdownIt();

const formatMessage = (content) => {
  return md.render(content);
};

const toggleCollapse = () => {
  editorStore.toggleCreativeAssistant();
};

// When creative assistant is hidden, optionally keep the conversation or reset it
// For now, we keep the conversation in the component but you could add logic to clear it

const fetchPromptTemplates = async () => {
  try {
    const response = await axios.get(`/api/prompt-templates`);
    promptTemplates.value = response.data;
  } catch (error) {
    console.error("Failed to fetch prompt templates:", error);
    ElMessage.error("加载提示模板失败");
  }
};

const fetchAiModels = async () => {
  try {
    const response = await axios.get(`/api/ai-models`);
    // 后端已过滤，前端直接使用返回的数据
    aiModels.value = response.data;
  } catch (error) {
    console.error("Failed to fetch AI models:", error);
    ElMessage.error("加载AI模型失败");
  }
};

onMounted(() => {
  fetchPromptTemplates();
  fetchAiModels();
  loadReferences();

  // 应用默认设置（如果存在）
  if (systemStore.settings.assistantDefaults) {
    selectedAiModelId.value =
      systemStore.settings.assistantDefaults.aiModelId ?? null;
    selectedPromptTemplateId.value =
      systemStore.settings.assistantDefaults.promptTemplateId ?? null;
  }

  messages.value.push({
    role: "assistant",
    content: "你好！有什么可以帮助你的吗？",
    isThinking: false,
    hadThinkingProcess: false,
    showThinkingProcess: false,
  });

  // Initialize resize if the assistant is already visible
  if (creativeAssistantVisible.value) {
    nextTick(() => {
      initResize();
    });
  }
});

// 监听项目变化，重新加载引用库
watch(currentProject, () => {
  loadReferences();
});

// 监听侧边栏可见性，在可见时初始化拖动功能
watch(
  creativeAssistantVisible,
  (newValue) => {
    if (newValue) {
      nextTick(() => {
        initResize();
      });
    }
  },
  { immediate: true },
); // Initialize immediately when component mounts if already visible

const selectPromptTemplate = (templateId) => {
  selectedPromptTemplateId.value = templateId;
};

const selectAiModel = (modelId) => {
  selectedAiModelId.value = modelId;
};

const getPromptTemplateName = (templateId) => {
  const template = promptTemplates.value.find((t) => t.id === templateId);
  return template ? template.name : "";
};

const getAiModelName = (modelId) => {
  const model = aiModels.value.find((m) => m.id === modelId);
  return model ? model.name : "";
};

// 加载引用库数据
const loadReferences = async () => {
  if (!currentProject.value) {
    references.value = {
      worldview: null,
      characters: [],
      organizations: [],
      powers: [],
      weapons: [],
      dungeons: [],
    };
    return;
  }

  try {
    const projectId = currentProject.value.id;

    // 加载世界观
    try {
      const worldviewRes = await worldviewService.get(projectId);
      references.value.worldview = worldviewRes.data;
    } catch (e) {
      references.value.worldview = null;
    }

    // 加载其他资源
    const [charsRes, orgsRes, powersRes, weaponsRes, dungeonsRes] =
      await Promise.all([
        characterService.getAll(projectId).catch(() => ({ data: [] })),
        organizationService.getAll(projectId).catch(() => ({ data: [] })),
        supernaturalPowerService.getAll(projectId).catch(() => ({ data: [] })),
        weaponService.getAll(projectId).catch(() => ({ data: [] })),
        dungeonService.getAll(projectId).catch(() => ({ data: [] })),
      ]);

    references.value.characters = charsRes.data;
    references.value.organizations = orgsRes.data;
    references.value.powers = powersRes.data;
    references.value.weapons = weaponsRes.data;
    references.value.dungeons = dungeonsRes.data;
  } catch (error) {
    console.error("Failed to load references:", error);
  }
};

// 插入引用
const insertReference = (name) => {
  userInput.value += `{{${name}}}`;
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// Modify sendMessageStream function to support updating existing messages
const testUserInput = () => {
  console.log("[CreativeAssistant] Testing userInput:");
  console.log("[CreativeAssistant] Current userInput value:", userInput.value);
  console.log("[CreativeAssistant] Current isLoading state:", isLoading.value);
  console.log("[CreativeAssistant] Messages count:", messages.value.length);
};

// A unified function to handle sending messages and regenerating responses
const sendMessage = async (
  messageContent = null,
  updateMessageIndex = null,
) => {
  const content = messageContent || userInput.value;
  if (!content.trim()) {
    ElMessage.warning("消息不能为空");
    return;
  }
  if (isLoading.value) return;

  // 检查用户输入和提示词模板中是否包含变量，如果包含，则必须有项目上下文
  const selectedTemplate = promptTemplates.value.find(
    (t) => t.id === selectedPromptTemplateId.value,
  );
  const templateContent = selectedTemplate ? selectedTemplate.content : "";
  const fullContentToCheck = content + templateContent; // 检查用户输入和模板内容

  if (fullContentToCheck.includes("{{") && !currentProject.value) {
    ElMessage.warning(
      '您似乎使用了变量，请先在"小说管理"中选择一个项目以正确渲染它们。',
    );
    return;
  }

  isLoading.value = true;

  // 如果是新消息（非重新生成），则添加到消息列表
  if (updateMessageIndex === null) {
    messages.value.push({ role: "user", content });
    userInput.value = "";
  }

  scrollToBottom();

  let aiMessageIndex;
  // 如果是更新现有消息，则更新该消息内容；否则添加新消息
  if (updateMessageIndex !== null) {
    aiMessageIndex = updateMessageIndex;
    const msg = messages.value[aiMessageIndex];
    msg.content = "";
    msg.thinkingContent = "";
    msg.rawContent = "";
    msg.isThinking = true;
    msg.showThinkingProcess = true;
    msg.hadThinkingProcess = false; // 重置思考过程标志
  } else {
    messages.value.push({
      role: "assistant",
      content: "",
      thinkingContent: "",
      rawContent: "",
      isThinking: true,
      showThinkingProcess: true,
      hadThinkingProcess: false, // 新增：用于标记是否曾有过思考过程
    });
    aiMessageIndex = messages.value.length - 1;
  }
  scrollToBottom();

  let processedUserInput = content;

  // 如果用户输入包含变量，则先进行渲染
  if (content.includes("{{")) {
    try {
      const renderPayload = {
        content: content,
        project_id: currentProject.value ? currentProject.value.id : null,
        selected_text: cachedSelectedText.value || null,
      };
      const response = await axios.post("/api/prompts/render", renderPayload);
      processedUserInput = response.data.rendered_content;
    } catch (error) {
      console.error("Failed to render user input:", error);
      ElMessage.error("渲染用户输入中的变量失败。");
      messages.value.pop(); // 移除已添加的AI消息
      if (updateMessageIndex === null) {
        messages.value.pop(); // 移除已添加的用户消息
      }
      userInput.value = content; // 恢复用户输入
      isLoading.value = false;
      return;
    }
  }

  try {
    // Build history based on whether it's a new message or a regeneration
    let actualHistory;
    if (updateMessageIndex !== null) {
      // Regeneration: history is everything before the user message that led to the response being updated.
      actualHistory = messages.value.slice(0, updateMessageIndex - 1);
    } else {
      // New message: history is everything before the new user message.
      const tempHistory = [...messages.value];
      tempHistory.pop(); // remove assistant placeholder
      tempHistory.pop(); // remove user message
      actualHistory = tempHistory;
    }

    // 限制历史消息轮数
    const limitedHistory = actualHistory.slice(
      -aiSettings.value.memoryRounds * 2,
    );

    // 获取编辑器中选中的文字
    const selectedText = editorStore.getSelectedText();

    const payload = {
      message: processedUserInput,
      conversation_id: conversationId.value,
      history: limitedHistory.map((m) => ({
        role: m.role,
        content: m.content,
      })),
      prompt_template_id: selectedPromptTemplateId.value,
      ai_model_id: selectedAiModelId.value,
      project_id: currentProject.value ? currentProject.value.id : null,
      proxy_url: systemStore.settings.proxyUrl || null,
      selected_text: selectedText || null,
      temperature: aiSettings.value.temperature,
      max_tokens: aiSettings.value.maxTokens,
    };

    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 获取响应流
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const msg = messages.value[aiMessageIndex];

    // 处理流式数据
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const dataStr = line.substring(6);
            if (dataStr.trim() === "[DONE]") continue;

            const data = JSON.parse(dataStr);
            if (!msg) continue;

            if (data.type === "conversation_id") {
              if (!conversationId.value) {
                conversationId.value = data.conversation_id;
              }
              continue;
            }

            if (data.type === "error") {
              msg.content = data.message;
              ElMessage.error("AI响应失败");
              continue;
            }

            if (data.type === "done") continue;

            if (data.content) {
              if (msg.rawContent === undefined) msg.rawContent = "";
              msg.rawContent += data.content;

              const thinkRegex = /<think>(.*?)<\/think>/s;
              const match = msg.rawContent.match(thinkRegex);

              if (match) {
                msg.hadThinkingProcess = true;
                // Ensure it's expanded while thinking
                if (!msg.showThinkingProcess) {
                  msg.showThinkingProcess = true;
                }
                msg.thinkingContent = match[1];
                msg.content = msg.rawContent.replace(thinkRegex, "").trim();
              } else {
                msg.content = msg.rawContent;
              }
              scrollToBottom();
            }
          } catch (e) {
            // Ignore JSON parsing errors
          }
        }
      }
    }

    // 缓冲区逻辑已移除，无需处理
  } catch (error) {
    console.error("AI request failed:", error);
    if (messages.value[aiMessageIndex]) {
      messages.value[aiMessageIndex].content = "抱歉，与AI连接时出现错误。";
    }
    ElMessage.error("AI响应失败");
  } finally {
    if (messages.value[aiMessageIndex]) {
      const msg = messages.value[aiMessageIndex];
      msg.isThinking = false;

      // 回复完成后，总是将思考过程折叠起来
      if (msg.hadThinkingProcess) {
        msg.showThinkingProcess = false;
      }

      // Clean up
    }
    isLoading.value = false;
    scrollToBottom();
  }
};

const handleEnter = (e) => {
  if (e.shiftKey) {
    return; // Allow new line on Shift+Enter
  }
  sendMessage();
};

const insertIntoEditor = () => {
  if (!lastAiResponse.value) {
    ElMessage.warning("没有可供写入的AI内容");
    return;
  }
  const result = editorStore.insertContent(lastAiResponse.value);
  if (result.success) {
    ElMessage.success("内容已成功写入编辑器");
  } else {
    ElMessage.error(result.message);
  }
};

// Function to clear only the current messages but keep the conversation context

// Function to clear only the current messages but keep the conversation context
const clearCurrentMessages = () => {
  ElMessageBox.confirm(
    "确定要清除当前对话内容吗？这将清除所有消息记录，但保持当前的AI设置继续对话。",
    "清除对话确认",
    {
      confirmButtonText: "确定清除",
      cancelButtonText: "取消",
      type: "warning",
    },
  )
    .then(() => {
      // Reset to initial state with just the assistant greeting
      messages.value = [
        {
          role: "assistant",
          content: "你好！有什么可以帮助你的吗？",
          isThinking: false,
          hadThinkingProcess: false,
          showThinkingProcess: false,
        },
      ];
      userInput.value = "";
      ElMessage.success("对话内容已清除");
    })
    .catch(() => {
      // User cancelled
      ElMessage.info("已取消清除操作");
    });
};

// Add a function to start a new conversation
const startNewConversation = () => {
  conversationId.value = null;
  messages.value = [
    {
      role: "assistant",
      content: "你好！有什么可以帮助你的吗？",
      isThinking: false,
      hadThinkingProcess: false,
      showThinkingProcess: false,
    },
  ];
  userInput.value = "";
};

// Regenerate AI response
const regenerateResponse = async (aiMessageIndex) => {
  const userMessageIndex = aiMessageIndex - 1;
  if (
    userMessageIndex < 0 ||
    messages.value[userMessageIndex].role !== "user"
  ) {
    ElMessage.error("找不到对应的用户提问");
    return;
  }
  const userMessageContent = messages.value[userMessageIndex].content;

  // Call sendMessage, which will handle updating the message at aiMessageIndex
  await sendMessage(userMessageContent, aiMessageIndex);
};

// Delete specific message
const deleteMessage = async (messageIndex) => {
  ElMessageBox.confirm("确定要删除这条消息吗？此操作不可恢复！", "删除确认", {
    confirmButtonText: "确定删除",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        // If it's a user message, delete the following AI response as well
        const message = messages.value[messageIndex];
        if (
          message.role === "user" &&
          messageIndex + 1 < messages.value.length
        ) {
          const nextMessage = messages.value[messageIndex + 1];
          if (nextMessage.role === "assistant") {
            // Delete user message and AI response
            messages.value.splice(messageIndex, 2);
            ElMessage.success("消息对已删除");
            return;
          }
        }

        // Delete single message
        messages.value.splice(messageIndex, 1);
        ElMessage.success("消息已删除");
      } catch (error) {
        ElMessage.error("删除消息失败");
        console.error(error);
      }
    })
    .catch(() => {
      ElMessage.info("已取消删除");
    });
};

// Copy message to clipboard
const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content);
    ElMessage.success("已复制到剪贴板");
  } catch (err) {
    ElMessage.error("复制失败");
  }
};

// 清除选中文字
const clearSelectedText = () => {
  editorStore.clearCachedSelectedText();
};

// 侧边栏宽度调整
const assistantSidebar = ref(null);
const sidebarWidth = ref(350); // 默认宽度
const isResizing = ref(false);
const startX = ref(0);
const startWidth = ref(0);

const initResize = () => {
  // Use nextTick to ensure DOM is rendered before accessing elements
  nextTick(() => {
    const resizeBar = assistantSidebar.value?.$el.querySelector(".resize-bar");
    if (!resizeBar) {
      console.warn("Resize bar not found in CreativeAssistant component");
      return;
    }

    resizeBar.addEventListener("mousedown", startResize);
  });
};

const startResize = (e) => {
  isResizing.value = true;
  startX.value = e.clientX;
  startWidth.value = sidebarWidth.value;

  document.addEventListener("mousemove", handleMouseMove);
  document.addEventListener("mouseup", stopResize);

  e.preventDefault();
};

const handleMouseMove = (e) => {
  if (!isResizing.value) return;

  const diff = e.clientX - startX.value;
  // For a right-side sidebar, dragging the left edge of the sidebar to the left
  // makes the sidebar wider, so we subtract the negative diff (which increases width)
  // Dragging the left edge to the right makes the sidebar narrower
  // diff = positive when dragging right -> startWidth - positive = smaller width
  // diff = negative when dragging left -> startWidth - negative = larger width
  const newWidth = startWidth.value - diff;

  // 限制最小和最大宽度
  if (newWidth >= 200 && newWidth <= 600) {
    sidebarWidth.value = newWidth;
  }
};

const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener("mousemove", handleMouseMove);
  document.removeEventListener("mouseup", stopResize);
};

// Clean up event listeners on component unmount
onUnmounted(() => {
  document.removeEventListener("mousemove", handleMouseMove);
  document.removeEventListener("mouseup", stopResize);
});
</script>

<style scoped>
/* --- 动画 --- */
.message-enter-active {
  transition: all 0.4s ease-out;
}
.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* --- 主布局 --- */
.creative-assistant-sidebar {
  background-color: var(--bg-color-base);
  border-left: 1px solid var(--border-color);
  transition: width 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  /* 强制刷新样式 */
  transform: translateZ(0);
}
.assistant-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  flex-grow: 1;
}
.assistant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  height: 60px;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-color-card);
  flex-shrink: 0;
}
.assistant-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
}
.assistant-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* --- 消息区域 --- */
.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 20px;
}
/* 外层 wrapper，用于控制整体左右对齐和垂直排列 */
.message-wrapper {
  display: flex;
  margin-bottom: 24px;
  flex-direction: column; /* 核心：内容和按钮垂直堆叠 */
}
.message-wrapper-assistant {
  align-items: flex-start; /* AI消息（内容+按钮）整体左对齐 */
}
.message-wrapper-user {
  align-items: flex-end; /* 用户消息（内容+按钮）整体右对齐 */
}

/* 包裹头像和消息气泡的容器 */
.message-content-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-start; /* 垂直方向上，头像和气泡顶部对齐 */
  max-width: 100%; /* 创作助手中空间较小，允许占满 */
}
/* 用户消息的内容 wrapper，头像在右边 */
.message-wrapper-user .message-content-wrapper {
  flex-direction: row-reverse; /* 头像和气泡反向排列 */
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
.avatar-user {
  background-color: var(--primary-color);
}
.avatar-assistant {
  background: linear-gradient(135deg, #67c23a, #4caf50);
}

.message {
  max-width: 100%;
}

.message .markdown-body,
.message-user span {
  padding: 8px 14px;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  word-break: break-word;
}
.message-user span {
  background: var(--primary-color);
  color: white;
  border-radius: 12px 4px 12px 12px;
}
.message-assistant .markdown-body {
  background-color: var(--bg-color-card);
  color: var(--text-color-primary);
  border-radius: 4px 12px 12px 12px;
}

/* --- 思考过程样式 --- */
.thinking-process-container {
  background-color: #f7f8fa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}

.thinking-process-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background-color: #f0f2f5;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.thinking-process-header:hover {
  background-color: #e9ebee;
}

.thinking-process-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.collapse-button {
  font-size: 12px;
}

.thinking-process-content {
  padding: 12px;
  font-size: 0.9em;
  color: #909399; /* 浅灰色字体 */
  background-color: #fdfdfd;
  border-top: 1px dashed #e4e7ed;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  line-height: 1.7;
}

/* 由于内容是通过 v-html 渲染的，我们需要使用 :deep() 来确保样式能正确应用到内部的 markdown 元素 */
.thinking-process-content :deep(p),
.thinking-process-content :deep(ul),
.thinking-process-content :deep(ol),
.thinking-process-content :deep(code),
.thinking-process-content :deep(pre),
.thinking-process-content :deep(span) {
  color: #909399 !important;
}

.thinking-process-content :deep(pre) {
  background-color: #f0f2f5;
}

.message-assistant .thinking-process-container + .final-answer {
  margin-top: 12px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  color: var(--text-color-secondary);
}

/* 消息操作按钮 */
.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px; /* 与消息气泡的间距 */
}

/* 根据角色调整 message-actions 的边距，使其与消息气泡对齐 */
.message-wrapper-assistant .message-actions {
  margin-left: 48px; /* avatar width (36px) + gap (12px) */
}

.message-wrapper-user .message-actions {
  margin-right: 48px; /* avatar width (36px) + gap (12px) */
}

/* --- 输入区域 --- */
.chat-input {
  padding: 16px;
  background-color: var(--bg-color-card);
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

/* 已捕获文字提示 */
.captured-text-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background-color: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  margin-bottom: 10px;
  font-size: 13px;
}

.hint-label {
  color: #3b82f6;
  font-weight: 500;
}

.hint-text {
  color: #1e40af;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.clear-button {
  padding: 0;
  min-width: auto;
  color: #6b7280;
}

.clear-button:hover {
  color: #ef4444;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.input-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.control-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}
.control-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.control-label {
  font-size: 12px;
  color: var(--text-color-secondary);
  background-color: var(--bg-color-hover);
  padding: 2px 8px;
  border-radius: 12px;
}
.chat-input .el-textarea__inner {
  border-radius: 8px;
  border-color: var(--border-color);
}
.chat-input .el-textarea__inner:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color-light);
}
.input-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.input-actions .el-button {
  flex-grow: 1;
}

/* 宽度调整条 */
.resize-bar {
  position: absolute;
  left: -5px;
  top: 0;
  bottom: 0;
  width: 10px;
  cursor: col-resize;
  z-index: 10;
  background-color: transparent;
}
.resize-bar:hover,
.resize-bar:active {
  background-color: var(--primary-color-light);
}

/* --- 下拉菜单分组标题样式 --- */
.provider-group-title {
  color: #909399;
  font-size: 12px;
  padding: 8px 20px 4px;
  font-weight: 600;
  pointer-events: none;
  user-select: none;
}

.provider-group:not(:first-child) .provider-group-title {
  margin-top: 8px;
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}

/* 选中项高亮样式 */
:deep(.el-dropdown-menu__item.is-active) {
  background-color: var(--primary-color-light);
  color: var(--primary-color);
  font-weight: 600;
}

/* 引用库空状态 */
.reference-empty {
  padding: 12px 20px;
  color: #909399;
  font-size: 13px;
  text-align: center;
}

/* 模型下拉菜单最大高度和滚动 */
.model-dropdown-popper {
  max-height: 50vh !important;
  overflow-y: auto !important;
}

.model-dropdown-popper .el-dropdown-menu {
  max-height: 50vh !important;
}

.model-dropdown-popper .el-dropdown-menu__list {
  max-height: 48vh !important;
  overflow-y: auto !important;
}

/* 引用库下拉菜单最大高度和滚动 */
.reference-dropdown-popper {
  max-height: 400px !important;
}

.reference-dropdown-popper .el-dropdown-menu {
  max-height: 400px !important;
  overflow-y: auto !important;
}

/* 提示词库下拉菜单最大高度和滚动 */
.prompt-dropdown-popper {
  max-height: 400px !important;
}

.prompt-dropdown-popper .el-dropdown-menu {
  max-height: 400px !important;
  overflow-y: auto !important;
}
</style>
