<template>
  <div class="login-container">
    <div class="login-form">
      <div class="login-header">
        <h1>电力交易智能问答系统</h1>
        <p>欢迎登录</p>
      </div>
      
      <el-form :model="form" :rules="rules" ref="loginForm" class="form-content">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="loading"
          @click="handleLogin"
        >
          登录
        </el-button>
      </el-form>

    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { userAPI } from '../services/api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const loginForm = ref(null)
    const loading = ref(false)
    
    const form = ref({
      username: '',
      password: ''
    })
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
      ]
    }
    
    const handleLogin = async () => {
      if (!loginForm.value) return
      
      try {
        const valid = await loginForm.value.validate()
        if (!valid) return
        
        loading.value = true
        
        const result = await userAPI.login(form.value.username, form.value.password)
        
        if (result.success) {
          authStore.login(result.user)
          ElMessage.success('登录成功')
          router.push('/chat')
        }
      } catch (error) {
        ElMessage.error(error.message || '登录失败')
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      rules,
      loginForm,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 24px;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.form-content {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
}

.demo-accounts {
  border-top: 1px solid #eee;
  padding-top: 20px;
  text-align: center;
}

.demo-accounts h3 {
  color: #666;
  margin-bottom: 10px;
  font-size: 14px;
}

.demo-accounts p {
  color: #999;
  font-size: 12px;
  margin: 5px 0;
}
</style>