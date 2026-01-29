<template>
  <div class="game-generator-container">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-content">
        <h1 class="title">
          <span class="icon">🎮</span>
          DreamCoder - AI游戏生成器
        </h1>
        <button class="btn-profile" @click="$router.push('/profile')">
          <img :src="authStore.user?.avatar || '/static/avatars/default-avatar.jpg'" alt="Avatar" class="avatar-small">
          {{ authStore.user?.username }}
        </button>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：输入配置区 -->
      <div class="input-section">
        <div class="card">
          <h2 class="card-title">描述你的游戏</h2>
          <textarea
            v-model="userInput"
            class="game-input"
            placeholder="例如：我想要一个贪吃蛇游戏，可以用方向键控制蛇吃食物，要有计分系统和游戏结束提示..."
            rows="6"
          ></textarea>

          <!-- 快速提示 -->
          <div class="quick-prompts">
            <span class="label">快速开始：</span>
            <button
              v-for="prompt in quickPrompts"
              :key="prompt"
              class="prompt-btn"
              @click="userInput = prompt"
            >
              {{ prompt }}
            </button>
          </div>

          <!-- 模板选择 -->
          <div class="template-section">
            <span class="label">选择模板：</span>
            <button
              v-for="template in templates"
              :key="template.id"
              class="template-btn"
              :class="{ active: selectedTemplate?.id === template.id }"
              @click="selectTemplate(template)"
            >
              {{ template.name }}
            </button>
          </div>

          <!-- 生成按钮 -->
          <button
            class="btn-generate"
            :disabled="!userInput.trim() || isGenerating"
            @click="generateGame"
          >
            <span v-if="!isGenerating">🚀 开始生成</span>
            <span v-else>⏳ 生成中...</span>
          </button>
        </div>

        <!-- 生成日志 -->
        <div class="card logs-card">
          <h2 class="card-title">生成日志</h2>
          <div class="logs-container">
            <div
              v-for="log in logs"
              :key="log.timestamp"
              class="log-item"
              :class="log.status"
            >
              <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              <span class="log-step">{{ log.step }}</span>
              <span class="log-message">{{ log.message }}</span>
              <span v-if="log.status" class="log-status">
                {{ log.status === 'completed' ? '✓' : '✗' }}
              </span>
            </div>
            <div v-if="logs.length === 0" class="log-empty">等待生成...</div>
          </div>
        </div>
      </div>

      <!-- 右侧：预览和代码区 -->
      <div class="preview-section">
        <!-- Tab切换 -->
        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 预览Tab -->
        <div v-if="activeTab === 'preview'" class="tab-content">
          <div v-if="deploymentUrl" class="preview-container">
            <iframe :src="deploymentUrl" class="game-iframe" frameborder="0"></iframe>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">🎯</div>
            <p>游戏生成后可在此处预览</p>
          </div>
        </div>

        <!-- 代码Tab -->
        <div v-if="activeTab === 'code'" class="tab-content">
          <div v-if="generatedFiles && Object.keys(generatedFiles).length > 0" class="code-container">
            <div class="file-tree">
              <div
                v-for="(content, filename) in generatedFiles"
                :key="filename"
                class="file-item"
                :class="{ active: selectedFile === filename }"
                @click="selectedFile = filename"
              >
                📄 {{ filename }}
              </div>
            </div>
            <div class="code-editor">
              <pre><code>{{ generatedFiles[selectedFile] }}</code></pre>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">💻</div>
            <p>游戏生成后可查看代码</p>
          </div>
        </div>

        <!-- 结构Tab -->
        <div v-if="activeTab === 'structure'" class="tab-content">
          <div v-if="projectInfo" class="info-container">
            <div class="info-item">
              <span class="info-label">游戏类型：</span>
              <span class="info-value">{{ projectInfo.game_type || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">技术栈：</span>
              <span class="info-value">{{ projectInfo.tech_stack || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">质量评分：</span>
              <span class="info-value" :class="getQualityClass(projectInfo.quality_score)">
                {{ projectInfo.quality_score?.toFixed(0) || 0 }}/100
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">生成时间：</span>
              <span class="info-value">{{ projectInfo.generation_time?.toFixed(1) || 0 }}秒</span>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">📊</div>
            <p>游戏生成后可查看项目结构</p>
          </div>
        </div>

        <!-- 历史Tab -->
        <div v-if="activeTab === 'history'" class="tab-content">
          <div class="projects-list">
            <div
              v-for="project in projects"
              :key="project.id"
              class="project-item"
              :class="{ active: currentProjectId === project.id }"
              @click="loadProject(project)"
            >
              <div class="project-header">
                <span class="project-title">{{ project.title }}</span>
                <span class="project-status" :class="project.status">
                  {{ getStatusText(project.status) }}
                </span>
              </div>
              <div class="project-desc">{{ project.description }}</div>
              <div class="project-meta">
                {{ formatDate(project.created_at) }}
              </div>
            </div>
            <div v-if="projects.length === 0" class="empty-state">
              <div class="empty-icon">📂</div>
              <p>暂无历史项目</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import apiClient from '@/utils/axios'

const authStore = useAuthStore()

// 状态
const userInput = ref('')
const selectedTemplate = ref(null)
const isGenerating = ref(false)
const logs = ref([])
const deploymentUrl = ref(null)
const generatedFiles = ref(null)
const selectedFile = ref('index.html')
const projectInfo = ref(null)
const currentProjectId = ref(null)
const projects = ref([])
const activeTab = ref('preview')

// 快速提示
const quickPrompts = [
  '贪吃蛇游戏，可以用方向键控制',
  '打砖块游戏，需要挡板接球',
  '打地鼠游戏，点击随机出现的地鼠',
  '猜数字游戏，猜测1-100之间的数字',
  '躲避球游戏，躲避不断出现的障碍物'
]

// 模板数据
const templates = ref([])

// Tab定义
const tabs = [
  { id: 'preview', label: '🎮 游戏预览' },
  { id: 'code', label: '💻 源代码' },
  { id: 'structure', label: '📊 项目信息' },
  { id: 'history', label: '📂 历史项目' }
]

// 加载模板
const loadTemplates = async () => {
  try {
    const response = await apiClient.get('/game/templates')
    templates.value = response.data.templates || []
  } catch (error) {
    console.error('加载模板失败:', error)
  }
}

// 选择模板
const selectTemplate = (template) => {
  selectedTemplate.value = template
  userInput.value = `生成一个${template.name}游戏。${template.description}`
}

// 生成游戏
const generateGame = async () => {
  if (!userInput.value.trim()) return

  isGenerating.value = true
  logs.value = []
  deploymentUrl.value = null
  generatedFiles.value = null
  projectInfo.value = null

  try {
    const response = await apiClient.post('/game/generate', {
      description: userInput.value,
      title: `游戏-${new Date().toLocaleString()}`
    })

    // 轮询获取状态
    const projectId = response.data.project_id
    await pollProjectStatus(projectId)

    // 刷新项目列表
    await loadProjects()

  } catch (error) {
    console.error('生成失败:', error)
    logs.value.push({
      timestamp: new Date().toISOString(),
      step: 'error',
      status: 'failed',
      message: '生成失败: ' + (error.response?.data?.detail || error.message)
    })
  } finally {
    isGenerating.value = false
  }
}

// 轮询项目状态
const pollProjectStatus = async (projectId) => {
  const maxAttempts = 60
  let attempts = 0

  const poll = async () => {
    try {
      const response = await apiClient.get(`/game/projects/${projectId}`)
      const project = response.data

      // 获取日志
      const logsResponse = await apiClient.get(`/game/projects/${projectId}/logs`)
      logs.value = logsResponse.data.logs || []

      if (project.status === 'completed') {
        deploymentUrl.value = project.deployment_url
        projectInfo.value = project
        currentProjectId.value = projectId

        // 获取文件
        const filesResponse = await apiClient.get(`/game/projects/${projectId}/files`)
        generatedFiles.value = filesResponse.data.files
        return
      }

      if (project.status === 'failed') {
        throw new Error('项目生成失败')
      }

      if (attempts < maxAttempts) {
        attempts++
        setTimeout(poll, 1000)
      } else {
        throw new Error('生成超时')
      }
    } catch (error) {
      console.error('轮询失败:', error)
      logs.value.push({
        timestamp: new Date().toISOString(),
        step: 'error',
        status: 'failed',
        message: error.message
      })
    }
  }

  await poll()
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await apiClient.get('/game/projects')
    projects.value = response.data || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 加载项目详情
const loadProject = async (project) => {
  currentProjectId.value = project.id

  try {
    // 获取文件
    const filesResponse = await apiClient.get(`/game/projects/${project.id}/files`)
    generatedFiles.value = filesResponse.data.files
    deploymentUrl.value = filesResponse.data.deployment_url

    // 获取日志
    const logsResponse = await apiClient.get(`/game/projects/${project.id}/logs`)
    logs.value = logsResponse.data.logs || []

    projectInfo.value = project

    // 切换到预览
    activeTab.value = 'preview'
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    generating: '生成中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status] || status
}

// 获取质量等级样式
const getQualityClass = (score) => {
  if (score >= 80) return 'quality-excellent'
  if (score >= 60) return 'quality-good'
  return 'quality-poor'
}

onMounted(() => {
  loadTemplates()
  loadProjects()
})
</script>

<style scoped>
.game-generator-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 1.5rem;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon {
  font-size: 2rem;
}

.btn-profile {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
}

.avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 1.5rem;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
}

.game-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  margin-bottom: 1rem;
  font-family: inherit;
}

.game-input:focus {
  outline: none;
  border-color: #667eea;
}

.quick-prompts, .template-section {
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.label {
  font-weight: 500;
  color: #666;
  font-size: 0.9rem;
}

.prompt-btn, .template-btn {
  padding: 0.4rem 0.8rem;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.prompt-btn:hover, .template-btn:hover {
  background: #e0e0e0;
}

.template-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.btn-generate {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-generate:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.logs-card {
  margin-top: 1.5rem;
  max-height: 300px;
}

.logs-container {
  max-height: 200px;
  overflow-y: auto;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 0.5rem;
}

.log-item {
  display: flex;
  gap: 0.5rem;
  padding: 0.4rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #eee;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #999;
  font-size: 0.75rem;
  min-width: 60px;
}

.log-step {
  font-weight: 500;
  color: #667eea;
  min-width: 100px;
}

.log-message {
  flex: 1;
  color: #333;
}

.log-status {
  color: #51cf66;
}

.log-item.failed .log-status {
  color: #ff6b6b;
}

.log-empty {
  text-align: center;
  color: #999;
  padding: 1rem;
}

.preview-section {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tabs {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
}

.tab-btn {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #f8f9fa;
}

.tab-btn.active {
  border-bottom-color: #667eea;
  color: #667eea;
  font-weight: 600;
}

.tab-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.preview-container {
  flex: 1;
  background: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

.game-iframe {
  width: 100%;
  height: 100%;
  min-height: 500px;
  border-radius: 8px;
  background: white;
}

.code-container {
  display: grid;
  grid-template-columns: 200px 1fr;
  height: 100%;
}

.file-tree {
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
}

.file-item {
  padding: 0.6rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  border-bottom: 1px solid #eee;
}

.file-item:hover {
  background: #e9ecef;
}

.file-item.active {
  background: #667eea;
  color: white;
}

.code-editor {
  padding: 1rem;
  overflow: auto;
  background: #282c34;
}

.code-editor pre {
  margin: 0;
  color: #abb2bf;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.info-container {
  padding: 2rem;
}

.info-item {
  display: flex;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.info-label {
  width: 120px;
  color: #666;
  font-weight: 500;
}

.info-value {
  color: #333;
}

.quality-excellent {
  color: #51cf66;
  font-weight: 600;
}

.quality-good {
  color: #fcc419;
  font-weight: 600;
}

.quality-poor {
  color: #ff6b6b;
  font-weight: 600;
}

.projects-list {
  overflow-y: auto;
  max-height: 100%;
}

.project-item {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  cursor: pointer;
  transition: background 0.2s;
}

.project-item:hover {
  background: #f8f9fa;
}

.project-item.active {
  background: #e7f3ff;
  border-left: 3px solid #667eea;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.project-title {
  font-weight: 600;
  color: #333;
}

.project-status {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.project-status.completed {
  background: #d4edda;
  color: #155724;
}

.project-status.generating {
  background: #fff3cd;
  color: #856404;
}

.project-status.failed {
  background: #f8d7da;
  color: #721c24;
}

.project-desc {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
}

.project-meta {
  color: #999;
  font-size: 0.8rem;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state p {
  font-size: 1.1rem;
}
</style>
