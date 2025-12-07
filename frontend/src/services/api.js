import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 用户相关API
export const userAPI = {
  // 登录验证（这里需要您在后端实现对应的登录接口）
  login: (username, password) => {
    // 模拟登录验证，实际应该调用后端API
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // 模拟用户数据
        const users = [
          { id: 1, username: 'cqk', password: '123456', role: 'admin' },
          { id: 2, username: 'lyy', password: '123456', role: 'user' }
        ]
        
        const user = users.find(u => u.username === username && u.password === password)
        if (user) {
          resolve({ success: true, user: { id: user.id, username: user.username, role: user.role } })
        } else {
          reject(new Error('用户名或密码错误'))
        }
      }, 500)
    })
  },

  // 获取用户列表（管理员功能）
  getUsers: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { id: 1, username: 'cqk', role: 'admin', created_time: '2025-11-30 10:15:40' },
          { id: 2, username: 'lyy', role: 'user', created_time: '2025-11-30 10:16:04' }
        ])
      }, 500)
    })
  },

  // 添加用户
  addUser: (userData) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true, user: { ...userData, id: Date.now() } })
      }, 500)
    })
  },

  // 删除用户
  deleteUser: (userId) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true })
      }, 500)
    })
  },

  // 更新用户
  updateUser: (userId, userData) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true, user: { ...userData, id: userId } })
      }, 500)
    })
  }
}

// 问答相关API
export const chatAPI = {
  // 流式问答
  chatStream: (question) => {
    return fetch('/api/chat/sse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question })
    })
  }
}

export default api