<template>
  <div class="game-chat-container">
    <!-- 登录弹窗 -->
    <transition name="fade">
      <div v-if="!isAuthenticated" class="login-modal-overlay">
        <div class="login-modal">
          <div class="login-modal-header">
            <div class="logo">
              <span class="logo-icon">🤖</span>
              <span class="logo-text">DreamCoder</span>
            </div>
          </div>
          
          <div class="login-modal-body">
            <div class="mode-switch">
              <button
                class="mode-btn"
                :class="{ active: isLoginMode }"
                @click="switchMode(true)"
              >
                登录
              </button>
              <button
                class="mode-btn"
                :class="{ active: !isLoginMode }"
                @click="switchMode(false)"
              >
                注册
              </button>
            </div>
            
            <!-- 登录表单 -->
            <div v-if="isLoginMode" class="auth-form">
              <div class="form-group">
                <label>用户名</label>
                <input
                  v-model="loginForm.username"
                  type="text"
                  placeholder="请输入用户名"
                  :class="{ 'input-error': loginError }"
                />
              </div>

              <div class="form-group">
                <label>密码</label>
                <div class="password-wrapper">
                  <input
                    v-model="loginForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="请输入密码"
                    :class="{ 'input-error': loginError }"
                  />
                  <button class="password-toggle" @click="showPassword = !showPassword">
                    <font-awesome-icon :icon="showPassword ? faEye : faEyeSlash" />
                  </button>
                </div>
              </div>

              <div v-if="loginError" class="error-message">{{ loginError }}</div>

              <button class="submit-btn" @click="handleLogin" :disabled="isLoading">
                {{ isLoading ? '登录中...' : '登录' }}
              </button>
            </div>
            
            <!-- 注册表单 -->
            <div v-else class="auth-form">
              <div class="form-group">
                <label>用户名</label>
                <input
                  v-model="registerForm.username"
                  type="text"
                  placeholder="3-20个字符"
                  :class="{ 'input-error': registerError }"
                />
              </div>

              <div class="form-group">
                <label>密码</label>
                <div class="password-wrapper">
                  <input
                    v-model="registerForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="至少6个字符"
                    :class="{ 'input-error': registerError }"
                  />
                  <button class="password-toggle" @click="showPassword = !showPassword">
                    <font-awesome-icon :icon="showPassword ? faEye : faEyeSlash" />
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label>确认密码</label>
                <div class="password-wrapper">
                  <input
                    v-model="registerForm.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="再次输入密码"
                    :class="{ 'input-error': registerError }"
                  />
                  <button class="password-toggle" @click="showConfirmPassword = !showConfirmPassword">
                    <font-awesome-icon :icon="showConfirmPassword ? faEye : faEyeSlash" />
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label>联系方式</label>
                <div class="contact-wrapper">
                  <input
                    v-model="registerForm.contact"
                    type="text"
                    placeholder="请输入邮箱或手机号"
                    :class="{ 'input-error': registerError }"
                    :style="{ 'padding-right': (countdown > 0 || sendingCode) ? '130px' : '110px' }"
                  />
                  <button 
                    class="verify-btn" 
                    :disabled="countdown > 0 || sendingCode" 
                    @click="sendVerificationCode"
                  >
                    {{ countdown > 0 ? `${countdown}s` : (sendingCode ? '发送中...' : '发送验证码') }}
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label>验证码</label>
                <input
                  v-model="registerForm.verificationCode"
                  type="text"
                  placeholder="请输入验证码"
                  :class="{ 'input-error': registerError }"
                />
              </div>

              <div v-if="registerError" class="error-message">{{ registerError }}</div>

              <button class="submit-btn" @click="handleRegister" :disabled="isLoading">
                {{ isLoading ? '注册中...' : '注册并登录' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 左侧边栏：项目列表 -->
    <div class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <div class="sidebar-header">
        <h3 v-if="!isSidebarCollapsed">我的项目</h3>
        <div class="sidebar-controls">
          <button v-if="!isSidebarCollapsed" class="icon-btn" @click="showNewProjectModal = true" title="新建项目">
            <font-awesome-icon :icon="faPlus" />
          </button>
          <button class="icon-btn" @click="isSidebarCollapsed = !isSidebarCollapsed" :title="isSidebarCollapsed ? '展开侧边栏' : '收起侧边栏'">
            <font-awesome-icon :icon="isSidebarCollapsed ? faExpand : faCompress" />
          </button>
        </div>
      </div>
      
      <div v-if="!isSidebarCollapsed" class="project-list">
        <div
          v-for="project in projects"
          :key="project.id"
          class="project-item"
          :class="{ active: currentProject?.id === project.id }"
          @click="selectProject(project)"
        >
          <div class="project-info">
            <div class="project-title">{{ project.title }}</div>
            <div class="project-meta">
              <span class="project-time">{{ formatTime(project.created_at) }}</span>
              <span class="project-status" :class="project.status">
                {{ getStatusText(project.status) }}
              </span>
            </div>
          </div>
          <button class="delete-btn" @click.stop="deleteProject(project.id)" title="删除项目">
            <font-awesome-icon :icon="faTimes" />
          </button>
        </div>
        
        <div v-if="projectsLoading" class="loading-state">
          <p>加载中...</p>
        </div>

        <div v-if="!projectsLoading && projects.length === 0" class="empty-state">
          <p>暂无项目</p>
          <p class="empty-hint">点击 + 号创建新项目</p>
        </div>
      </div>
      
      <!-- 个人信息区域 -->
      <div v-if="!isSidebarCollapsed" class="user-section">
        <div class="user-profile" @click="toggleUserMenu">
          <div class="user-avatar">
            <img v-if="user.avatar" :src="user.avatar" :alt="user.username" />
            <font-awesome-icon v-else :icon="faUser" class="default-avatar" />
          </div>
          <div class="user-info">
            <div class="user-name">{{ user.username }}</div>
            <div class="user-email">{{ user.email || user.phone }}</div>
          </div>
          <font-awesome-icon :icon="faEllipsisV" class="user-menu-icon" />
        </div>
        
        <div class="user-dropdown" v-if="showUserMenu">
          <div class="dropdown-item" @click="openProfileModal">
            <font-awesome-icon :icon="faUserCog" />
            <span>账号管理</span>
          </div>
          <div class="dropdown-item" @click="handleLogout">
            <font-awesome-icon :icon="faSignOutAlt" />
            <span>退出登录</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 中间：聊天区域 -->
    <div class="chat-container">
      <!-- 顶部工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <h2 v-if="currentProject">{{ currentProject.title }}</h2>
          <h2 v-else>选择一个项目或创建新项目</h2>
        </div>
        <div class="toolbar-right">
        </div>
      </div>
      
      <!-- 消息列表 -->
      <div class="messages-section">
        <div class="messages-container" ref="messagesContainer">
          <div v-if="!currentProject || messages.length === 0" class="empty-messages">
            <div class="empty-icon">
              <font-awesome-icon :icon="faCommentDots" size="3x" />
            </div>
            <h3>开始对话</h3>
            <p>选择一个项目或创建新项目，然后描述你的游戏需求</p>
          </div>
          
          <div v-else class="message-list">
            <div
              v-for="msg in messages"
              :key="msg.id"
              class="message"
              :class="msg.role"
            >
              <!-- 用户消息 (头像在右边) -->
              <template v-if="msg.role === 'user'">
                <div class="message-wrapper user">
                  <div class="message-content user-message">
                    <div class="message-text">{{ msg.content }}</div>
                    <div class="message-time">{{ formatTime(msg.created_at) }}</div>
                  </div>
                  <!-- 用户头像 (在右边) -->
                  <div class="message-avatar user-avatar">
                    <font-awesome-icon :icon="faUser" />
                  </div>
                </div>
              </template>

              <!-- 系统消息 (头像在左边) -->
              <template v-else-if="msg.role === 'assistant'">
                <div class="message-content assistant-message">
                  <div class="message-avatar assistant-avatar">
                    <font-awesome-icon :icon="faRobot" />
                  </div>
                  <div class="message-body">
                    <div v-if="msg.message_type === 'log'" class="log-message">
                      <div class="log-header">
                        <span class="log-step">{{ msg.extra_data?.step || '步骤' }}</span>
                        <span class="log-status" :class="msg.extra_data?.status">
                          {{ msg.extra_data?.status || 'processing' }}
                        </span>
                      </div>
                      <div class="log-body">{{ msg.content }}</div>
                    </div>
                    <div v-else class="text-message">{{ msg.content }}</div>
                  </div>
                  <div class="message-time">{{ formatTime(msg.created_at) }}</div>
                </div>
              </template>
            </div>
            
            <!-- 加载状态 -->
            <div v-if="isGenerating" class="message assistant">
              <div class="message-content">
                <div class="message-avatar">
                  <font-awesome-icon :icon="faSpinner" spin />
                </div>
                <div class="message-body">
                  <div class="text-message">正在生成...</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-wrapper">
          <textarea 
            v-model="userInput" 
            class="message-input"
            placeholder="描述你的游戏需求... (Shift + Enter 换行，Enter 发送)"
            @keydown.enter.prevent="handleEnter"
            :disabled="!currentProject || isGenerating"
            rows="3"
            ref="inputRef"
          ></textarea>
          <button 
            class="send-btn" 
            @click="sendMessage"
            :disabled="!currentProject || !userInput.trim() || isGenerating"
            title="发送消息"
          >
            <font-awesome-icon :icon="isGenerating ? faSpinner : faPaperPlane" :spin="isGenerating" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- 右侧：代码预览面板 -->
    <transition name="slide-fade">
      <div class="code-panel" :style="{ width: sidebarWidth + 'px' }">
        <!-- 拖拽条 -->
        <div 
          class="resize-handle"
          @mousedown="startResize"
          :class="{ resizing: isResizing }"
          title="拖动调整宽度"
        ></div>
        <div class="code-panel-header">
          <div class="code-panel-tabs">
            <button
              class="tab-btn"
              :class="{ active: previewMode === 'code' }"
              @click="previewMode = 'code'"
            >
              <font-awesome-icon :icon="faCode" />
              <span>代码</span>
            </button>
            <button
              v-if="canPreview"
              class="tab-btn"
              :class="{ active: previewMode === 'preview' }"
              @click="previewMode = 'preview'"
            >
              <font-awesome-icon :icon="faGamepad" />
              <span>试玩</span>
            </button>
          </div>
          <div class="code-panel-actions">
            <input
              v-if="previewMode === 'code'"
              type="text"
              class="file-search"
              placeholder="搜索文件..."
              v-model="fileSearchQuery"
            />
            <button
              v-if="previewMode === 'preview' && isFullscreen"
              class="icon-btn"
              @click="exitFullscreen"
              title="退出全屏"
            >
              <font-awesome-icon :icon="faCompress" />
            </button>
            <button
              v-if="previewMode === 'preview' && !isFullscreen"
              class="icon-btn"
              @click="enterFullscreen"
              title="全屏试玩"
            >
              <font-awesome-icon :icon="faExpand" />
            </button>
            <button
              v-if="previewMode === 'preview' && !canLivePreview"
              class="icon-btn"
              @click="downloadProject"
              title="下载项目"
            >
              <font-awesome-icon :icon="faDownload" />
            </button>

          </div>
        </div>

        <div class="code-panel-content">
          <!-- 代码模式 -->
          <div v-if="previewMode === 'code'">
            <!-- 文件树 -->
            <div class="file-tree" v-if="filteredFiles.length > 0">
              <div
                v-for="file in filteredFiles"
                :key="file.path"
                class="file-tree-item"
                :class="{ active: selectedFile?.path === file.path }"
                @click="selectFile(file)"
              >
                <font-awesome-icon :icon="getFileIcon(file.path)" />
                <span class="file-name">{{ getFileName(file.path) }}</span>
              </div>
            </div>

            <!-- 代码预览 -->
            <div class="code-preview-container">
              <div v-if="!selectedFile" class="empty-code-preview">
                <font-awesome-icon :icon="faFileCode" size="3x" />
                <p>选择一个文件查看代码</p>
              </div>
              <div v-else class="code-preview">
                <div class="code-preview-header">
                  <span class="file-path">{{ selectedFile.path }}</span>
                  <button class="icon-btn" @click="copyCode" title="复制代码">
                    <font-awesome-icon :icon="faCopy" />
                  </button>
                </div>
                <pre><code class="language-{{ getLanguage(selectedFile.path) }}">{{ selectedFile.content }}</code></pre>
              </div>
            </div>
          </div>

          <!-- 预览/试玩模式 -->
          <div v-else-if="previewMode === 'preview'" class="preview-container">
            <!-- HTML/CSS/JS 直接预览 -->
            <div v-if="gameType === 'web'" class="preview-iframe-container" :class="{ fullscreen: isFullscreen }">
              <iframe
                ref="previewFrame"
                class="preview-iframe"
                :srcdoc="previewContent"
                sandbox="allow-scripts allow-same-origin allow-modals allow-forms"
              ></iframe>
              <div v-if="previewLoading" class="preview-loading">
                <font-awesome-icon :icon="faSpinner" spin size="2x" />
                <p>正在加载预览...</p>
              </div>
            </div>

            <!-- Python/C++/Java 等后端游戏 -->
            <div v-else class="backend-game-preview">
              <div class="backend-game-info">
                <font-awesome-icon :icon="faInfoCircle" size="2x" />
                <h3>{{ getGameTypeLabel(gameType) }} 游戏</h3>
                <p>该游戏需要后端环境运行。您可以选择以下方式：</p>
                <div class="preview-options">
                  <button class="preview-option-btn" @click="showConsole = true">
                    <font-awesome-icon :icon="faTerminal" />
                    <span>在线运行（沙箱）</span>
                  </button>
                  <button class="preview-option-btn" @click="downloadProject">
                    <font-awesome-icon :icon="faDownload" />
                    <span>下载到本地运行</span>
                  </button>
                  <button class="preview-option-btn" @click="showInstructions = true">
                    <font-awesome-icon :icon="faBook" />
                    <span>运行说明</span>
                  </button>
                </div>
              </div>

              <!-- 控制台输出区域 -->
              <transition name="fade">
                <div v-if="showConsole" class="console-panel">
                  <div class="console-header">
                    <span>运行输出</span>
                    <button class="icon-btn" @click="showConsole = false">
                      <font-awesome-icon :icon="faTimes" />
                    </button>
                  </div>
                  <div class="console-output">
                    <pre>{{ consoleOutput }}</pre>
                  </div>
                  <div class="console-input">
                    <input
                      type="text"
                      v-model="consoleInput"
                      placeholder="输入命令..."
                      @keydown.enter="runConsoleCommand"
                    />
                    <button @click="runConsoleCommand">执行</button>
                  </div>
                </div>
              </transition>

              <!-- 运行说明弹窗 -->
              <transition name="fade">
                <div v-if="showInstructions" class="modal-overlay" @click.self="showInstructions = false">
                  <div class="modal instructions-modal">
                    <div class="modal-header">
                      <h3>运行说明</h3>
                      <button class="icon-btn" @click="showInstructions = false">
                        <font-awesome-icon :icon="faTimes" />
                      </button>
                    </div>
                    <div class="modal-body instructions-content">
                      <h4>{{ getGameTypeLabel(gameType) }} 游戏运行指南</h4>
                      <div v-html="getRunInstructions()"></div>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>
    </transition>
    
    <!-- 账号管理弹窗 -->
    <ProfileModal v-model:visible="showProfileModal" />
    
    <!-- 新建项目弹窗 -->
    <transition name="fade">
      <div v-if="showNewProjectModal" class="modal-overlay" @click.self="showNewProjectModal = false">
        <div class="modal">
          <div class="modal-header">
            <h3>新建项目</h3>
            <button class="icon-btn" @click="showNewProjectModal = false">
              <font-awesome-icon :icon="faTimes" />
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>项目名称</label>
              <input 
                v-model="newProjectTitle" 
                type="text" 
                placeholder="输入项目名称"
                class="form-input"
                ref="modalInputRef"
              />
            </div>
            <div class="form-group">
              <label>初始需求</label>
              <textarea 
                v-model="newProjectMessage" 
                placeholder="描述你的游戏需求..."
                class="form-textarea"
                rows="4"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showNewProjectModal = false">取消</button>
            <button class="btn btn-primary" @click="createProject" :disabled="!newProjectTitle.trim()">
              创建
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import apiClient from '@/utils/axios';
import { generatePreviewHTML } from '@/utils/htmlGenerator';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faUser, faPlus, faTimes, faEllipsisV, faSignOutAlt,
  faCode, faCommentDots, faRobot, faSpinner, faPaperPlane,
  faFileCode, faFolderOpen, faCopy, faFolder, faFile,
  faEye, faEyeSlash, faGamepad, faExpand, faCompress,
  faDownload, faTerminal, faInfoCircle, faBook, faUserCog
} from '@fortawesome/free-solid-svg-icons';
import ProfileModal from '@/components/ProfileModal.vue';


library.add(
  faUser, faPlus, faTimes, faEllipsisV, faSignOutAlt,
  faCode, faCommentDots, faRobot, faSpinner, faPaperPlane,
  faFileCode, faFolderOpen, faCopy, faFolder, faFile,
  faEye, faEyeSlash, faGamepad, faExpand, faCompress,
  faDownload, faTerminal, faInfoCircle, faBook, faUserCog
);

const router = useRouter();
const authStore = useAuthStore();

// 用户信息
const user = computed(() => authStore.user || {});
const isAuthenticated = computed(() => authStore.isAuthenticated);

// 登录弹窗
const isLoginMode = ref(true);
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const isLoading = ref(false);
const sendingCode = ref(false);
const countdown = ref(0);
const loginForm = ref({
  username: '',
  password: ''
});
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  contact: '',
  verificationCode: ''
});
const loginError = ref('');
const registerError = ref('');

// 项目相关
const projects = ref([]);
const currentProject = ref(null);
const projectsLoading = ref(false);
const showNewProjectModal = ref(false);
const newProjectTitle = ref('');
const newProjectMessage = ref('');

// 聊天相关
const messages = ref([]);
const userInput = ref('');
const isGenerating = ref(false);
const messagesContainer = ref(null);
const inputRef = ref(null);
const modalInputRef = ref(null);

// 代码面板
const showCodePanel = ref(true);
const previewMode = ref('code'); // 'code' 或 'preview'
const generatedFiles = ref([]);
const selectedFile = ref(null);
const fileSearchQuery = ref('');

// 预览相关
const previewFrame = ref(null);
const previewLoading = ref(false);
const isFullscreen = ref(false);
const gameType = ref('web'); // 'web', 'python', 'java', 'cpp'
const showConsole = ref(false);
const consoleOutput = ref('');
const consoleInput = ref('');
const showInstructions = ref(false);

// 用户菜单
const showUserMenu = ref(false);
const showProfileModal = ref(false);

// 左侧边栏状态
const isSidebarCollapsed = ref(false);

// 右侧侧边栏拖拽状态
const isResizing = ref(false);
const sidebarWidth = ref(450); // 默认宽度
const minSidebarWidth = 300; // 最小宽度
const maxSidebarWidth = 800; // 最大宽度

// 计算属性：过滤文件
const filteredFiles = computed(() => {
  if (!fileSearchQuery.value) return generatedFiles.value;
  const query = fileSearchQuery.value.toLowerCase();
  return generatedFiles.value.filter(file =>
    file.path.toLowerCase().includes(query)
  );
});

// 计算属性：是否可以预览
const canPreview = computed(() => {
  return generatedFiles.value.length > 0;
});

// 计算属性：是否可以实时预览（HTML/CSS/JS）
const canLivePreview = computed(() => {
  return gameType.value === 'web';
});

// 计算属性：预览内容
const previewContent = computed(() => {
  if (!canPreview.value || gameType.value !== 'web') return '';
  return generatePreviewHTML(generatedFiles.value);
});

// 加载项目列表
const loadProjects = async () => {
  projectsLoading.value = true;
  try {
    const response = await apiClient.get('/game/projects');
    projects.value = response.data || [];

    if (projects.value.length > 0 && !currentProject.value) {
      await selectProject(projects.value[0]);
    }
  } catch (error) {
    console.error('加载项目错误:', error);
  } finally {
    projectsLoading.value = false;
  }
};

// 选择项目
const selectProject = async (project) => {
  currentProject.value = project;
  showNewProjectModal.value = false;
  await loadMessages();
  // 加载项目的生成代码
  await loadGeneratedFiles();
};

// 加载消息
const loadMessages = async () => {
  if (!currentProject.value) return;

  try {
    const response = await apiClient.get(`/game/projects/${currentProject.value.id}/chat`);

    messages.value = response.data || [];
    await scrollToBottom();
  } catch (error) {
    console.error('加载消息错误:', error);
  }
};

// 加载生成的文件
const loadGeneratedFiles = async () => {
  if (!currentProject.value) return;

  try {
    const response = await apiClient.get(`/game/projects/${currentProject.value.id}/files`);

    // 将字典格式的 files 转换为数组格式
    const filesDict = response.data.files || {};
    generatedFiles.value = Object.entries(filesDict).map(([path, content]) => ({
      path,
      content
    }));

    // 自动检测游戏类型
    detectGameType();

    // 自动选择第一个文件
    if (generatedFiles.value.length > 0 && !selectedFile.value) {
      selectedFile.value = generatedFiles.value[0];
    }
  } catch (error) {
    console.error('加载文件错误:', error);
    generatedFiles.value = [];
  }
};

// 检测游戏类型
const detectGameType = () => {
  const files = generatedFiles.value;
  const extensions = files.map(f => f.path.split('.').pop().toLowerCase());

  if (extensions.includes('html') || extensions.includes('js') || extensions.includes('css')) {
    gameType.value = 'web';
  } else if (extensions.includes('py')) {
    gameType.value = 'python';
  } else if (extensions.includes('java')) {
    gameType.value = 'java';
  } else if (extensions.includes('cpp') || extensions.includes('c') || extensions.includes('h')) {
    gameType.value = 'cpp';
  } else {
    gameType.value = 'web'; // 默认
  }
};

// 创建项目
const createProject = async () => {
  if (!newProjectTitle.value.trim()) return;

  try {
    const response = await apiClient.post('/game/generate', {
      project_id: null,
      title: newProjectTitle.value.trim(),
      message: newProjectMessage.value.trim() || '创建新项目'
    });

    showNewProjectModal.value = false;
    newProjectTitle.value = '';
    newProjectMessage.value = '';
    await loadProjects();
  } catch (error) {
    console.error('创建项目错误:', error);
    alert('创建项目错误');
  }
};

// 删除项目
const deleteProject = async (projectId) => {
  if (!confirm('确定要删除这个项目吗？')) return;

  try {
    await apiClient.delete(`/game/projects/${projectId}`);

    if (currentProject.value?.id === projectId) {
      currentProject.value = null;
      messages.value = [];
      generatedFiles.value = [];
      selectedFile.value = null;
    }
    await loadProjects();
  } catch (error) {
    console.error('删除项目错误:', error);
    alert('删除项目错误');
  }
};

// 发送消息
const sendMessage = async () => {
  if (!currentProject.value || !userInput.value.trim() || isGenerating.value) return;

  const message = userInput.value.trim();
  userInput.value = '';
  isGenerating.value = true;

  try {
    messages.value.push({
      id: Date.now(),
      role: 'user',
      content: message,
      created_at: new Date().toISOString()
    });
    await scrollToBottom();

    // 使用 /game/generate 接口继续对话
    const response = await apiClient.post('/game/generate', {
      project_id: currentProject.value.id,
      message: message
    });

    // 添加临时消息提示正在生成
    const generatingMsgId = Date.now();
    messages.value.push({
      id: generatingMsgId,
      role: 'assistant',
      content: '正在处理您的需求...',
      created_at: new Date().toISOString()
    });
    await scrollToBottom();

    // 轮询检查项目状态
    const checkInterval = setInterval(async () => {
      try {
        const projectResponse = await apiClient.get(`/game/projects/${currentProject.value.id}`);
        const project = projectResponse.data;

        if (project.status === 'completed') {
          clearInterval(checkInterval);
          // 重新加载消息
          await loadMessages();
          await loadGeneratedFiles();
          isGenerating.value = false;
        } else if (project.status === 'failed') {
          clearInterval(checkInterval);
          messages.value = messages.value.filter(m => m.id !== generatingMsgId);
          messages.value.push({
            id: Date.now(),
            role: 'assistant',
            content: '生成失败，请重试',
            created_at: new Date().toISOString()
          });
          isGenerating.value = false;
        }
      } catch (error) {
        console.error('检查项目状态失败:', error);
      }
    }, 2000);

    // 最多轮询5分钟
    setTimeout(() => {
      clearInterval(checkInterval);
      if (isGenerating.value) {
        isGenerating.value = false;
      }
    }, 300000);

  } catch (error) {
    console.error('发送消息错误:', error);
    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: '抱歉，出现错误，请重试',
      created_at: new Date().toISOString()
    });
    isGenerating.value = false;
  }
};

// 切换用户菜单
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

// 打开账号管理弹窗
const openProfileModal = () => {
  showUserMenu.value = false;
  showProfileModal.value = true;
};

// 选择文件
const selectFile = (file) => {
  selectedFile.value = file;
};

// 复制代码
const copyCode = async () => {
  if (!selectedFile.value) return;
  try {
    await navigator.clipboard.writeText(selectedFile.value.content);
    alert('代码已复制到剪贴板');
  } catch (error) {
    console.error('复制失败:', error);
  }
};

// 全屏操作
const enterFullscreen = () => {
  isFullscreen.value = true;
  document.body.style.overflow = 'hidden';
  
  // 延迟设置位置，确保DOM已更新
  nextTick(() => {
    const previewContainer = document.querySelector('.preview-iframe-container.fullscreen');
    if (previewContainer) {
      if (isSidebarCollapsed.value) {
        previewContainer.style.left = '40px';
      } else {
        previewContainer.style.left = '260px';
      }
      previewContainer.style.width = `calc(100vw - ${sidebarWidth.value}px)`;
    }
  });
};

const exitFullscreen = () => {
  isFullscreen.value = false;
  document.body.style.overflow = '';
};

// 获取游戏类型标签
const getGameTypeLabel = (type) => {
  const labels = {
    'web': 'Web',
    'python': 'Python',
    'java': 'Java',
    'cpp': 'C/C++'
  };
  return labels[type] || type;
};

// 获取运行说明
const getRunInstructions = () => {
  const instructions = {
    'python': `
      <h5>运行 Python 游戏</h5>
      <p><strong>前提条件：</strong></p>
      <ul>
        <li>安装 Python 3.7+</li>
        <li>安装依赖库：pip install pygame（如使用 pygame）</li>
      </ul>
      <p><strong>运行步骤：</strong></p>
      <ol>
        <li>下载游戏代码</li>
        <li>打开终端或命令行</li>
        <li>进入游戏目录</li>
        <li>运行：python main.py（或对应的入口文件）</li>
      </ol>
    `,
    'java': `
      <h5>运行 Java 游戏</h5>
      <p><strong>前提条件：</strong></p>
      <ul>
        <li>安装 JDK 11+</li>
        <li>配置 JAVA_HOME 环境变量</li>
      </ul>
      <p><strong>运行步骤：</strong></p>
      <ol>
        <li>下载游戏代码</li>
        <li>使用 IDE（如 IntelliJ IDEA, Eclipse）打开项目</li>
        <li>找到主类（包含 main 方法的类）</li>
        <li>运行主类</li>
      </ol>
      <p><strong>命令行运行：</strong></p>
      <pre>javac Main.java\njava Main</pre>
    `,
    'cpp': `
      <h5>运行 C/C++ 游戏</h5>
      <p><strong>前提条件：</strong></p>
      <ul>
        <li>安装 GCC 或 MSVC 编译器</li>
        <li>Windows: 可安装 MinGW 或 Visual Studio</li>
        <li>Linux/Mac: 安装 build-essential</li>
      </ul>
      <p><strong>运行步骤：</strong></p>
      <ol>
        <li>下载游戏代码</li>
        <li>编译：g++ main.cpp -o game</li>
        <li>运行：./game（Linux/Mac）或 game.exe（Windows）</li>
      </ol>
    `
  };

  return instructions[gameType.value] || '<p>暂无运行说明</p>';
};

// 运行控制台命令
const runConsoleCommand = () => {
  if (!consoleInput.value.trim()) return;

  const cmd = consoleInput.value.trim();
  consoleOutput.value += `$ ${cmd}\n`;

  // 模拟命令执行（实际应该调用后端）
  if (cmd === 'run' || cmd === 'start') {
    consoleOutput.value += '正在启动游戏...\n';
    consoleOutput.value += '注意：完整的游戏运行需要后端支持。\n';
    consoleOutput.value += '建议下载到本地运行。\n';
  } else if (cmd === 'help') {
    consoleOutput.value += '可用命令：\n';
    consoleOutput.value += '  run/start - 启动游戏\n';
    consoleOutput.value += '  clear - 清空控制台\n';
    consoleOutput.value += '  help - 显示帮助\n';
  } else if (cmd === 'clear') {
    consoleOutput.value = '';
  } else {
    consoleOutput.value += `未知命令: ${cmd}\n`;
    consoleOutput.value += '输入 "help" 查看可用命令\n';
  }

  consoleInput.value = '';
};

// 下载项目
const downloadProject = () => {
  if (!generatedFiles.value.length) return;

  // 创建 ZIP 文件（简化版，实际可以使用 JSZip 库）
  let content = '';
  generatedFiles.value.forEach(file => {
    content += `=== ${file.path} ===\n${file.content}\n\n`;
  });

  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${currentProject.value?.title || 'game'}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// 监听预览模式变化
watch(previewMode, (newMode) => {
  if (newMode === 'preview' && gameType.value === 'web') {
    previewLoading.value = true;
    setTimeout(() => {
      previewLoading.value = false;
    }, 500);
  }
});

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 处理回车
const handleEnter = (e) => {
  if (!e.shiftKey) {
    sendMessage();
  }
};

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  const now = new Date();
  const diff = now - date;
  
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'completed': '已完成',
    'in_progress': '进行中',
    'failed': '失败'
  };
  return statusMap[status] || status;
};

// 获取文件图标
const getFileIcon = (path) => {
  if (path.endsWith('.vue')) return faFileCode;
  if (path.endsWith('.js')) return faFileCode;
  if (path.endsWith('.ts')) return faFileCode;
  if (path.endsWith('.css')) return faFileCode;
  if (path.endsWith('.html')) return faFileCode;
  if (path.endsWith('.json')) return faFileCode;
  return faFile;
};

// 获取文件名
const getFileName = (path) => {
  const parts = path.split('/');
  return parts[parts.length - 1];
};

// 获取代码语言
const getLanguage = (path) => {
  if (path.endsWith('.vue')) return 'html';
  if (path.endsWith('.js')) return 'javascript';
  if (path.endsWith('.ts')) return 'typescript';
  if (path.endsWith('.css')) return 'css';
  if (path.endsWith('.html')) return 'html';
  if (path.endsWith('.json')) return 'json';
  return 'plaintext';
};

// 点击外部关闭用户菜单
document.addEventListener('click', (e) => {
  if (!e.target.closest('.user-section')) {
    showUserMenu.value = false;
  }
});

// 监听弹窗显示，自动聚焦
watch(showNewProjectModal, (newVal) => {
  if (newVal) {
    nextTick(() => {
      modalInputRef.value?.focus();
    });
  }
});

// 登录相关函数
const switchMode = (login) => {
  isLoginMode.value = login;
  loginError.value = '';
  registerError.value = '';
};

// 发送验证码
const sendVerificationCode = async () => {
  if (!registerForm.value.contact.trim()) {
    registerError.value = '请输入联系方式';
    return;
  }

  // 验证联系方式格式（邮箱或手机号）
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const phoneRegex = /^1[3-9]\d{9}$/;

  const isEmail = emailRegex.test(registerForm.value.contact);
  const isPhone = phoneRegex.test(registerForm.value.contact);

  if (!isEmail && !isPhone) {
    registerError.value = '请输入有效的邮箱或手机号';
    return;
  }

  sendingCode.value = true;
  registerError.value = '';

  try {
    const body = isEmail
      ? { email: registerForm.value.contact }
      : { phone: registerForm.value.contact };

    await apiClient.post('/auth/verification', body);

    // 开始倒计时
    countdown.value = 60;
    const timer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);
  } catch (error) {
    console.error('发送验证码错误:', error);
    registerError.value = error.response?.data?.detail || '发送验证码失败';
  } finally {
    sendingCode.value = false;
  }
};

const handleLogin = async () => {
  if (!loginForm.value.username.trim() || !loginForm.value.password) {
    loginError.value = '请输入用户名和密码';
    return;
  }

  isLoading.value = true;
  loginError.value = '';

  try {
    const response = await apiClient.post('/auth/login', {
      username: loginForm.value.username,
      password: loginForm.value.password
    });

    await authStore.initAuth(response.data.access_token, response.data.user);
    loginForm.value = { username: '', password: '' };
    loginError.value = '';
    await loadProjects();
  } catch (error) {
    console.error('登录错误:', error);
    loginError.value = error.response?.data?.detail || '网络错误，请稍后重试';
  } finally {
    isLoading.value = false;
  }
};

const handleRegister = async () => {
  if (!registerForm.value.username.trim()) {
    registerError.value = '请输入用户名';
    return;
  }

  if (registerForm.value.username.length < 3 || registerForm.value.username.length > 20) {
    registerError.value = '用户名长度应为 3-20 个字符';
    return;
  }

  if (!registerForm.value.password || registerForm.value.password.length < 6) {
    registerError.value = '密码至少需要 6 个字符';
    return;
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    registerError.value = '两次输入的密码不一致';
    return;
  }

  if (!registerForm.value.contact.trim()) {
    registerError.value = '请输入联系方式';
    return;
  }

  if (!registerForm.value.verificationCode.trim()) {
    registerError.value = '请输入验证码';
    return;
  }

  isLoading.value = true;
  registerError.value = '';

  try {
    const response = await apiClient.post('/auth/register', {
      username: registerForm.value.username,
      password: registerForm.value.password,
      contact: registerForm.value.contact,
      verification_code: registerForm.value.verificationCode
    });

    await authStore.initAuth(response.data.access_token, response.data.user);
    registerForm.value = { username: '', password: '', confirmPassword: '', contact: '', verificationCode: '' };
    registerError.value = '';
    countdown.value = 0;
    await loadProjects();
  } catch (error) {
    console.error('注册错误:', error);
    registerError.value = error.response?.data?.detail || '网络错误，请稍后重试';
  } finally {
    isLoading.value = false;
  }
};

// 退出登录
const handleLogout = async () => {
  showUserMenu.value = false;
  try {
    await authStore.logout();
    // 清空所有数据
    currentProject.value = null;
    messages.value = [];
    generatedFiles.value = [];
    selectedFile.value = null;
    projects.value = [];
    fileSearchQuery.value = '';
    newProjectTitle.value = '';
    newProjectMessage.value = '';
    // 不需要手动设置 showLoginModal，因为 !isAuthenticated 会自动显示登录弹窗
  } catch (error) {
    console.error('退出登录错误:', error);
  }
};

// 右侧侧边栏拖拽功能
const startResize = (e) => {
  e.preventDefault();
  isResizing.value = true;
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
  // 改变鼠标样式
  document.body.style.cursor = 'ew-resize';
};

const handleResize = (e) => {
  if (!isResizing.value) return;
  
  const containerWidth = window.innerWidth;
  const newWidth = containerWidth - e.clientX;
  
  // 限制宽度在最小和最大值之间
  if (newWidth >= minSidebarWidth && newWidth <= maxSidebarWidth) {
    sidebarWidth.value = newWidth;
  }
};

const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  // 恢复鼠标样式
  document.body.style.cursor = '';
};

onMounted(() => {
  // 检查是否已登录
  const token = localStorage.getItem('access_token');
  const userData = localStorage.getItem('user');
  
  if (token && userData) {
    try {
      const parsedUser = JSON.parse(userData);
      authStore.setAuth(token, parsedUser);
      loadProjects();
    } catch (error) {
      console.error('解析用户数据失败:', error);
    }
  }
  // 登录弹窗会根据 isAuthenticated 自动显示
});
</script>

<style scoped>
.game-chat-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #0d1117;
  color: #e6edf3;
}

/* 登录弹窗 */
.login-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(5px);
}

.login-modal {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  width: 100%;
  max-width: 440px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.login-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #30363d;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 28px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #e6edf3;
}

.login-modal-body {
  padding: 16px 24px;
}

.mode-switch {
  display: flex;
  background: transparent;
  border-radius: 8px;
  margin-bottom: 14px;
}

.mode-btn {
  flex: 1;
  background: transparent;
  color: #8b949e;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 6px;
  height: fit-content;
  transition: all 0.3s;
}

.mode-btn.active {
  background: #21262d;
  color: #e6edf3;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #e6edf3;
}

.form-group input {
  padding: 12px 14px;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #e6edf3;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #58a6ff;
}

.form-group input.input-error {
  border-color: #f85149;
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrapper input {
  width: 100%;
  padding-right: 40px;
}

.password-toggle {
  position: absolute;
  right: 10px;
  top: -40%;
  height: 30px;
  width: 30px;
  background: none;
  color: #8b949e;
  cursor: pointer;
  padding: 4px;
  font-size: 14px;
}

.password-toggle:hover {
  color: #58a6ff;
  background: none;
}

.error-message {
  color: #f85149;
  font-size: 13px;
  text-align: center;
  padding: 8px;
  background: rgba(248, 81, 73, 0.1);
  border-radius: 6px;
}

.submit-btn {
  padding: 12px 24px;
  background: #1f6feb;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  background: #1f88ff;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.contact-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.contact-wrapper input {
  width: 100%;
  padding-right: 110px;
}

.verify-btn {
  position: absolute;
  right: 10px;
  top: -45%;
  width: fit-content;
  padding: 6px 6px;
  background: #238636;
  color: #fff;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.verify-btn:hover:not(:disabled) {
  background: #2ea043;
}

.verify-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #30363d;
  color: #8b949e;
}

/* 左侧边栏 */
.sidebar {
  width: 260px;
  background: #161b22;
  border-right: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 40px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #30363d;
  min-height: 56px;
}

.sidebar-controls {
  display: flex;
  gap: 8px;
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #e6edf3;
}

.icon-btn {
  background: none;
  border: none;
  color: #8b949e;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
  width: auto;
}

.icon-btn:hover {
  background: #21262d;
  color: #e6edf3;
}

.project-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.project-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 4px;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.project-item:hover {
  background: #21262d;
}

.project-item.active {
  background: #1f6feb;
  color: #fff;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-title {
  font-weight: 500;
  font-size: 13px;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-meta {
  display: flex;
  gap: 6px;
  font-size: 11px;
}

.project-time {
  color: #8b949e;
}

.project-item.active .project-time {
  color: rgba(255, 255, 255, 0.7);
}

.project-status {
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
}

.project-status.completed {
  background: #238636;
  color: #fff;
}

.project-status.in_progress {
  background: #d29922;
  color: #000;
}

.project-status.failed {
  background: #f85149;
  color: #fff;
}

.delete-btn {
  background: none;
  border: none;
  color: #8b949e;
  cursor: pointer;
  padding: 4px;
  opacity: 0;
  transition: all 0.2s;
  width: auto;
}

.project-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #f85149;
  background: transparent;
}

.empty-state {
  text-align: center;
  padding: 40px 16px;
  color: #8b949e;
}

.empty-state p {
  margin: 6px 0;
}

.empty-hint {
  font-size: 12px;
}

.loading-state {
  text-align: center;
  padding: 40px 16px;
  color: #8b949e;
}

.loading-state p {
  margin: 6px 0;
}

/* 用户区域 */
.user-section {
  position: relative;
  border-top: 1px solid #30363d;
}

.user-profile {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.user-profile:hover {
  background: #21262d;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #21262d;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatar {
  color: #8b949e;
  font-size: 14px;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 500;
  color: #e6edf3;
  font-size: 13px;
  margin-bottom: 2px;
}

.user-email {
  font-size: 11px;
  color: #8b949e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-menu-icon {
  color: #8b949e;
  font-size: 12px;
}

.user-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
  color: #e6edf3;
}

.dropdown-item:hover {
  background: #30363d;
}

.dropdown-item span {
  font-size: 13px;
}

/* 中间聊天容器 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #0d1117;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #161b22;
  border-bottom: 1px solid #30363d;
}

.toolbar-left h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #e6edf3;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #e6edf3;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
}

.toolbar-btn:hover {
  background: #21262d;
}

.toolbar-btn.active {
  background: #1f6feb;
  border-color: #1f6feb;
}

/* 消息区域 */
.messages-section {
  flex: 1;
  overflow: hidden;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

.empty-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #8b949e;
}

.empty-icon {
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-messages h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #e6edf3;
}

.empty-messages p {
  margin: 0;
  font-size: 14px;
}

.message-list {
  max-width: 800px;
  margin: 0 auto;
}

.message {
  margin-bottom: 20px;
}

.message-wrapper.user {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  gap: 12px;
}

.message-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.message-content.user-message {
  flex-direction: column;
  align-items: flex-end;
  max-width: 70%;
}

.message-content.assistant-message {
  flex-direction: row;
  max-width: 70%;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 14px;
}

.user-avatar {
  background: #1f6feb;
  color: #fff;
}

.assistant-avatar {
  background: #238636;
  color: #fff;
}

.message-text {
  max-width: 70%;
  padding: 10px 14px;
  background: #1f6feb;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #fff;
}

.message-body {
  max-width: 80%;
}

.text-message {
  padding: 10px 14px;
  background: #21262d;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
}

.message-time {
  font-size: 11px;
  color: #8b949e;
  margin-top: 4px;
  text-align: right;
}

.user-message .message-time {
  text-align: left;
}

.assistant-message .message-time {
  text-align: right;
}

/* 日志消息 */
.log-message {
  background: #1e1e1e;
  color: #e6edf3;
  padding: 12px;
  border-radius: 6px;
  font-family: 'SFMono-Regular', 'Consolas', monospace;
  font-size: 12px;
  border: 1px solid #30363d;
}

.log-header {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 11px;
}

.log-step {
  color: #58a6ff;
  font-weight: 500;
}

.log-status {
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
}

.log-status.completed {
  background: #238636;
  color: #fff;
}

.log-status.processing {
  background: #d29922;
  color: #000;
}

.log-status.failed {
  background: #f85149;
  color: #fff;
}

.log-body {
  white-space: pre-wrap;
  word-break: break-all;
  color: #c9d1d9;
}

/* 输入区域 */
.input-section {
  background: #161b22;
  border-top: 1px solid #30363d;
  padding: 16px;
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  display: flex;
  gap: 12px;
}

.message-input {
  flex: 1;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 12px 14px;
  color: #e6edf3;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #58a6ff;
}

.message-input:disabled {
  background: #0d1117;
  cursor: not-allowed;
  opacity: 0.5;
}

.message-input::placeholder {
  color: #8b949e;
}

.send-btn {
  width: 44px;
  height: 44px;
  background: #1f6feb;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #1f88ff;
}

.send-btn:disabled {
  background: #30363d;
  cursor: not-allowed;
  opacity: 0.5;
}

/* 右侧代码面板 */
.code-panel {
  position: relative;
  background: #161b22;
  border-left: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  min-width: 300px;
  max-width: 800px;
}

/* 拖拽条样式 */
.resize-handle {
  position: absolute;
  left: -4px;
  top: 0;
  bottom: 0;
  width: 8px;
  cursor: ew-resize;
  z-index: 10;
  transition: background-color 0.2s;
}

.resize-handle:hover,
.resize-handle.resizing {
  background: rgba(88, 166, 255, 0.3);
}

.resize-handle::before {
  content: '';
  position: absolute;
  left: 3px;
  top: 50%;
  transform: translateY(-50%);
  width: 2px;
  height: 20px;
  background: #8b949e;
  border-radius: 1px;
  transition: background-color 0.2s;
}

.resize-handle:hover::before,
.resize-handle.resizing::before {
  background: #58a6ff;
}

.code-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #161b22;
  border-bottom: 1px solid #30363d;
}

.code-panel-tabs {
  display: flex;
  gap: 4px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: #8b949e;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #21262d;
  color: #e6edf3;
}

.tab-btn.active {
  background: #1f6feb;
  color: #fff;
}

.code-panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #e6edf3;
}

.code-panel-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-search {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 6px 10px;
  color: #e6edf3;
  font-size: 12px;
  outline: none;
  width: 140px;
  transition: all 0.2s;
}

.file-search:focus {
  border-color: #58a6ff;
  width: 180px;
}

.file-search::placeholder {
  color: #8b949e;
}

.code-panel-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 文件树 */
.file-tree {
  border-bottom: 1px solid #30363d;
  max-height: 200px;
  overflow-y: auto;
}

.file-tree-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 13px;
  color: #e6edf3;
  border-bottom: 1px solid #21262d;
}

.file-tree-item:hover {
  background: #21262d;
}

.file-tree-item.active {
  background: #1f6feb;
  color: #fff;
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 代码预览 */
.code-preview-container {
  flex: 1;
  overflow: hidden;
}

.empty-code-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #8b949e;
}

.empty-code-preview p {
  margin: 12px 0 0 0;
  font-size: 14px;
}

.code-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.code-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #0d1117;
  border-bottom: 1px solid #30363d;
}

.file-path {
  font-size: 12px;
  color: #8b949e;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.code-preview pre {
  flex: 1;
  margin: 0;
  padding: 16px;
  overflow: auto;
  font-size: 13px;
  line-height: 1.6;
  background: #0d1117;
}

.code-preview code {
  font-family: 'SFMono-Regular', 'Consolas', monospace;
  color: #e6edf3;
}

/* 游戏预览容器 */
.preview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #0d1117;
}

.preview-iframe-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #fff;
  border-radius: 4px;
}

.preview-iframe-container.fullscreen {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 9998;
  border-radius: 0;
  transition: left 0.3s ease;
}

/* 根据左侧边栏状态调整全屏预览位置 */
.sidebar:not(.collapsed) + .chat-container + .code-panel + .preview-iframe-container.fullscreen {
  left: 260px;
}

.sidebar.collapsed + .chat-container + .code-panel + .preview-iframe-container.fullscreen {
  left: 40px;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.preview-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  gap: 12px;
}

/* 后端游戏预览 */
.backend-game-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.backend-game-info {
  max-width: 400px;
}

.backend-game-info svg {
  color: #8b949e;
  margin-bottom: 20px;
}

.backend-game-info h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  color: #e6edf3;
}

.backend-game-info > p {
  margin: 0 0 24px 0;
  font-size: 14px;
  color: #8b949e;
  line-height: 1.6;
}

.preview-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-option-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  color: #e6edf3;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  width: 100%;
}

.preview-option-btn:hover {
  background: #21262d;
  border-color: #58a6ff;
  transform: translateY(-2px);
}

.preview-option-btn svg {
  color: #8b949e;
}

/* 控制台面板 */
.console-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: #0d1117;
  border-top: 1px solid #30363d;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #161b22;
  border-bottom: 1px solid #30363d;
  font-size: 13px;
  font-weight: 500;
  color: #e6edf3;
}

.console-output {
  max-height: 200px;
  padding: 12px 16px;
  overflow-y: auto;
  font-family: 'SFMono-Regular', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #c9d1d9;
  white-space: pre-wrap;
}

.console-input {
  display: flex;
  padding: 10px 16px;
  gap: 10px;
  border-top: 1px solid #30363d;
  background: #0d1117;
}

.console-input input {
  flex: 1;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 4px;
  padding: 8px 12px;
  color: #e6edf3;
  font-size: 12px;
  font-family: 'SFMono-Regular', 'Consolas', monospace;
  outline: none;
}

.console-input input:focus {
  border-color: #58a6ff;
}

.console-input button {
  padding: 8px 16px;
  background: #1f6feb;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.console-input button:hover {
  background: #1f88ff;
}

/* 运行说明弹窗 */
.instructions-modal {
  max-width: 600px;
}

.instructions-content {
  font-size: 14px;
  line-height: 1.8;
  color: #e6edf3;
}

.instructions-content h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #58a6ff;
}

.instructions-content h5 {
  margin: 20px 0 12px 0;
  font-size: 14px;
  color: #e6edf3;
}

.instructions-content p {
  margin: 12px 0;
}

.instructions-content ul,
.instructions-content ol {
  margin: 12px 0;
  padding-left: 24px;
}

.instructions-content li {
  margin: 6px 0;
  color: #c9d1d9;
}

.instructions-content pre {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 12px;
  margin: 12px 0;
  font-family: 'SFMono-Regular', 'Consolas', monospace;
  font-size: 12px;
  overflow-x: auto;
}

.instructions-content strong {
  color: #e6edf3;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #30363d;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #e6edf3;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #e6edf3;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #e6edf3;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  border-color: #58a6ff;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #30363d;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #1f6feb;
  color: #fff;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: #1f88ff;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  color: #e6edf3;
  border: 1px solid #30363d;
}

.btn-secondary:hover {
  background: #21262d;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #0d1117;
}

::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #8b949e;
}

/* 动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
