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

// 知识库管理相关API
export const knowledgeBaseAPI = {
  // 获取知识库数据
  getData: (page = 1, pageSize = 10) => {
    return new Promise((resolve, reject) => {
      fetch(`/api/data/get?page=${page}&pageSize=${pageSize}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('获取数据失败')
        }
        return response.json()
      })
      .then(data => {
        resolve(data)
      })
      .catch(error => {
        reject(error)
      })
    })
  },

  // 添加数据
  addData: (data) => {
    return new Promise((resolve, reject) => {
      fetch('/api/data/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('添加数据失败')
        }
        return response.json()
      })
      .then(result => {
        resolve(result)
      })
      .catch(error => {
        reject(error)
      })
    })
  },

  // 删除数据
  deleteData: (id) => {
    return new Promise((resolve, reject) => {
      fetch(`/api/data/delete/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('删除数据失败')
        }
        return response.json()
      })
      .then(result => {
        resolve(result)
      })
      .catch(error => {
        reject(error)
      })
    })
  },

  // 更新数据
  updateData: (id, data) => {
    return new Promise((resolve, reject) => {
      fetch(`/api/data/update/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('更新数据失败')
        }
        return response.json()
      })
      .then(result => {
        resolve(result)
      })
      .catch(error => {
        reject(error)
      })
    })
  },

  // 自动数据采集
  collectData: (response) => {
    return new Promise((resolve, reject) => {
      fetch('/api/data/collect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ response })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('数据采集失败')
        }
        return response.json()
      })
      .then(data => {
        resolve(data)
      })
      .catch(error => {
        reject(error)
      })
    })
  }
}

export default api