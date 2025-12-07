<template>
  <div class="chat-container">
    <!-- 头部导航 -->
    <el-header class="chat-header">
      <div class="header-left">
        <h2>电力交易智能问答</h2>
      </div>
      <div class="header-right">
        <span class="user-info">欢迎，{{ user.username }} ({{ user.role === 'admin' ? '管理员' : '用户' }})</span>
        <el-button v-if="user.role === 'admin'" type="primary" @click="goToUserManagement">
          用户管理
        </el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </el-header>

    <!-- 问答区域 -->
    <div class="chat-content">
      <div class="chat-messages" ref="messagesContainer">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.type]"
        >
          <div class="message-avatar">
            <el-avatar :icon="message.type === 'user' ? 'User' : 'ChatDotRound'" />
          </div>
          <div class="message-content">
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="message assistant loading">
          <div class="message-avatar">
            <el-avatar icon="ChatDotRound" />
          </div>
          <div class="message-content">
            <div class="message-text">
              <span class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <el-input
          v-model="inputQuestion"
          type="textarea"
          :rows="3"
          placeholder="请输入关于电力交易的问题..."
          :disabled="loading"
          @keydown.enter.exact.prevent="handleSend"
        />
        <div class="input-actions">
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="handleSend"
            :disabled="!inputQuestion.trim()"
          >
            发送
          </el-button>
          <el-button @click="clearChat" :disabled="loading">清空对话</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { chatAPI } from '../services/api'

export default {
  name: 'Chat',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const messagesContainer = ref(null)
    
    const user = computed(() => authStore.user)
    const inputQuestion = ref('')
    const loading = ref(false)
    const messages = ref([])

    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }

    // 格式化时间
    const formatTime = () => {
      return new Date().toLocaleTimeString('zh-CN', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 发送消息
    const handleSend = async () => {
      if (!inputQuestion.value.trim() || loading.value) return
      
      const question = inputQuestion.value.trim()
      inputQuestion.value = ''
      
      // 添加用户消息
      messages.value.push({
        type: 'user',
        content: question,
        time: formatTime()
      })
      
      scrollToBottom()
      loading.value = true
      
      try {
        // 处理流式响应
        const response = await chatAPI.chatStream(question)
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        
        let buffer = ''
        let finalResult = ''
        
        // 添加AI消息占位
        messages.value.push({
          type: 'assistant',
          content: '',
          time: formatTime()
        })
        
        while (true) {
          const { done, value } = await reader.read()
          
          if (done) break
          
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                if (data.type === 'content') {
                  // 直接处理内容作为最终结果
                  finalResult += data.content
                  const beautifiedResult = finalResult
                    .replace(/###/g, '\n\n ')  // 美化###分隔符
                    .replace(/关键点/g, '\n\n**关键点**')
                  messages.value[messages.value.length - 1].content = beautifiedResult
                  scrollToBottom()
                } else if (data.type === 'end') {
                  // 处理结束事件，使用完整响应更新结果
                  const beautifiedResult = data.complete_response
                    .replace(/###/g, '\n\n### ')  // 美化###分隔符
                    .replace(/总结/g, '\n\n**总结**')
                    .replace(/关键点/g, '\n\n**关键点**')
                  messages.value[messages.value.length - 1].content = beautifiedResult
                  scrollToBottom()
                }
              } catch (e) {
                // 忽略解析错误
              }
            }
          }
        }
        
      } catch (error) {
        ElMessage.error('发送失败：' + error.message)
        // 移除AI消息占位
        messages.value.pop()
      } finally {
        loading.value = false
      }
    }

    // 清空对话
    const clearChat = () => {
      messages.value = []
    }

    // 跳转到用户管理
    const goToUserManagement = () => {
      router.push('/users')
    }

    // 退出登录
    const handleLogout = () => {
      authStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    }

    onMounted(() => {
      // 初始化欢迎消息
      messages.value.push({
        type: 'assistant',
        content: '您好！我是电力交易智能问答助手，请问有什么可以帮助您的？',
        time: formatTime()
      })
    })

    return {
      user,
      inputQuestion,
      loading,
      messages,
      messagesContainer,
      handleSend,
      clearChat,
      goToUserManagement,
      handleLogout
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left h2 {
  color: #303133;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  color: #606266;
  font-size: 14px;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  max-height: calc(100vh - 200px);
}

.message {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message.user .message-text {
  background: #409eff;
  color: white;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.message.user .message-time {
  text-align: right;
}

.typing-dots {
  display: inline-flex;
  gap: 3px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #909399;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input-area {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.input-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  justify-content: flex-end;
}

/* 确保普通消息的换行符正确显示 */
.message-text {
  white-space: pre-wrap;
  line-height: 1.6;
}
</style>