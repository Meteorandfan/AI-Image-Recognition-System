<template>
  <div class="page">
    <el-card class="header-card" shadow="never">
      <h1>AI 智能图像识别与管理系统</h1>
      <p class="subtitle">上传图片后进行模拟识别，并查看历史记录。</p>
    </el-card>

    <el-row :gutter="20" class="main-row">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="panel" shadow="hover">
          <template #header>
            <div class="panel-title">图片上传</div>
          </template>

          <el-upload
            class="upload-area"
            drag
            :show-file-list="false"
            :http-request="handleUpload"
            :before-upload="beforeUpload"
            :disabled="loading"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">点击或拖拽图片到此处上传</div>
            <div class="upload-tip">仅支持常见图片格式（jpg/png/webp等）</div>
          </el-upload>

          <div v-loading="loading" class="result-box">
            <div v-if="result">
              <el-tag type="success">识别结果</el-tag>
              <p class="result-line">物体名称：{{ result.label }}</p>
              <p class="result-line">置信度：{{ (result.confidence * 100).toFixed(2) }}%</p>
              <p class="result-line">图片名：{{ result.filename }}</p>
              <p class="result-line">时间：{{ formatTime(result.created_at) }}</p>
            </div>
            <div v-else class="result-empty">暂无识别结果</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="panel" shadow="hover">
          <template #header>
            <div class="panel-title">历史记录</div>
          </template>

          <el-table :data="history" stripe style="width: 100%">
            <template #empty>
              <el-empty description="暂无历史记录" />
            </template>
            <el-table-column prop="filename" label="图片名" min-width="120" />
            <el-table-column prop="label" label="结果" width="120" />
            <el-table-column prop="confidence" label="置信度" width="120">
              <template #default="scope">
                {{ (scope.row.confidence * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" min-width="160">
              <template #default="scope">
                {{ formatTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button size="small" type="danger" @click="deleteItem(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

// 基础配置：通过 /api 走 Vite 代理
const api = axios.create({
  baseURL: '/api'
})

// 页面状态
const loading = ref(false)
const result = ref(null)
const history = ref([])

// 上传限制
const MAX_SIZE_MB = 2
const ALLOWED_EXT = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']

// 上传前校验
const beforeUpload = (file) => {
  const ext = file.name ? file.name.toLowerCase().slice(file.name.lastIndexOf('.')) : ''
  if (!ALLOWED_EXT.includes(ext)) {
    ElMessage.error('文件格式错误，仅支持 jpg/png/webp/bmp')
    return false
  }
  if (!file.type.startsWith('image/')) {
    ElMessage.error('文件格式错误，请上传图片')
    return false
  }
  const sizeMb = file.size / 1024 / 1024
  if (sizeMb > MAX_SIZE_MB) {
    ElMessage.error(`图片过大，最大支持 ${MAX_SIZE_MB}MB`)
    return false
  }
  return true
}

// 自定义上传逻辑
const handleUpload = async (options) => {
  const { file } = options
  const formData = new FormData()
  formData.append('file', file)

  loading.value = true
  try {
    const res = await api.post('/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = res.data
    ElMessage.success('识别完成')
    await fetchHistory()
  } catch (error) {
    ElMessage.error(error?.response?.data?.message || error?.response?.data?.detail || '识别失败')
  } finally {
    loading.value = false
  }
}

// 获取历史记录
const fetchHistory = async () => {
  try {
    const res = await api.get('/history')
    history.value = res.data
  } catch (error) {
    ElMessage.error(error?.response?.data?.message || '获取历史记录失败')
  }
}

// 删除记录
const deleteItem = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除这条记录吗？', '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/history/${id}`)
    ElMessage.success('删除成功')
    await fetchHistory()
  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      return
    }
    ElMessage.error(error?.response?.data?.message || '删除失败')
  }
}

// 时间格式化（按用户本地时区展示）
const formatTime = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (num) => String(num).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: #f5f7fb;
  min-height: 100vh;
}

.header-card {
  margin-bottom: 20px;
}

.subtitle {
  color: #6b7280;
  margin-top: 6px;
}

.main-row {
  margin-top: 10px;
}

.panel-title {
  font-weight: 600;
}

.upload-area {
  width: 100%;
  margin-bottom: 16px;
}

.upload-icon {
  font-size: 36px;
  color: #409eff;
}

.upload-text {
  font-size: 14px;
  margin-top: 6px;
}

.upload-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.result-box {
  min-height: 140px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.result-line {
  margin: 6px 0;
}

.result-empty {
  color: #9ca3af;
}

@media (max-width: 768px) {
  .page {
    padding: 12px;
  }
}
</style>
