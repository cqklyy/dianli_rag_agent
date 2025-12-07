<template>
  <div class="user-management">
    <!-- 头部导航 -->
    <el-header class="management-header">
      <div class="header-left">
        <h2>用户管理</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="goToChat">返回问答</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </el-header>

    <!-- 内容区域 -->
    <div class="management-content">
      <!-- 操作栏 -->
      <div class="action-bar">
        <el-button type="primary" @click="showAddDialog = true" icon="Plus">
          添加用户
        </el-button>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名"
          style="width: 300px; margin-left: 20px;"
          prefix-icon="Search"
          clearable
        />
      </div>

      <!-- 用户表格 -->
      <el-table :data="filteredUsers" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'success'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button 
              size="small" 
              @click="handleEdit(row)"
              :disabled="row.id === currentUser.id"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="handleDelete(row)"
              :disabled="row.id === currentUser.id"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog 
      :title="editMode === 'add' ? '添加用户' : '编辑用户'"
      v-model="showAddDialog"
      width="500px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="editMode === 'add'">
          <el-input 
            v-model="userForm.password" 
            type="password" 
            placeholder="请输入密码" 
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { userAPI } from '../services/api'

export default {
  name: 'UserManagement',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const userFormRef = ref(null)
    
    const currentUser = computed(() => authStore.user)
    const users = ref([])
    const loading = ref(false)
    const showAddDialog = ref(false)
    const editMode = ref('add') // 'add' 或 'edit'
    const submitting = ref(false)
    const searchKeyword = ref('')
    
    const userForm = ref({
      id: null,
      username: '',
      password: '',
      role: 'user'
    })
    
    const userRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
      ],
      role: [
        { required: true, message: '请选择角色', trigger: 'change' }
      ]
    }

    // 过滤用户列表
    const filteredUsers = computed(() => {
      if (!searchKeyword.value) return users.value
      return users.value.filter(user => 
        user.username.toLowerCase().includes(searchKeyword.value.toLowerCase())
      )
    })

    // 加载用户列表
    const loadUsers = async () => {
      loading.value = true
      try {
        const data = await userAPI.getUsers()
        users.value = data
      } catch (error) {
        ElMessage.error('加载用户列表失败：' + error.message)
      } finally {
        loading.value = false
      }
    }

    // 重置表单
    const resetForm = () => {
      userForm.value = {
        id: null,
        username: '',
        password: '',
        role: 'user'
      }
    }

    // 添加用户
    const handleAdd = () => {
      editMode.value = 'add'
      resetForm()
      showAddDialog.value = true
    }

    // 编辑用户
    const handleEdit = (user) => {
      editMode.value = 'edit'
      userForm.value = { ...user }
      showAddDialog.value = true
    }

    // 删除用户
    const handleDelete = async (user) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await userAPI.deleteUser(user.id)
        ElMessage.success('删除成功')
        loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败：' + error.message)
        }
      }
    }

    // 提交表单
    const handleSubmit = async () => {
      if (!userFormRef.value) return
      
      try {
        const valid = await userFormRef.value.validate()
        if (!valid) return
        
        submitting.value = true
        
        if (editMode.value === 'add') {
          await userAPI.addUser(userForm.value)
          ElMessage.success('添加成功')
        } else {
          await userAPI.updateUser(userForm.value.id, userForm.value)
          ElMessage.success('更新成功')
        }
        
        showAddDialog.value = false
        loadUsers()
      } catch (error) {
        ElMessage.error('操作失败：' + error.message)
      } finally {
        submitting.value = false
      }
    }

    // 跳转到问答界面
    const goToChat = () => {
      router.push('/chat')
    }

    // 退出登录
    const handleLogout = () => {
      authStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    }

    onMounted(() => {
      loadUsers()
    })

    return {
      currentUser,
      users,
      loading,
      showAddDialog,
      editMode,
      submitting,
      searchKeyword,
      userForm,
      userFormRef,
      userRules,
      filteredUsers,
      handleAdd,
      handleEdit,
      handleDelete,
      handleSubmit,
      goToChat,
      handleLogout
    }
  }
}
</script>

<style scoped>
.user-management {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.management-header {
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

.management-content {
  flex: 1;
  padding: 20px;
  background: #f5f7fa;
}

.action-bar {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.el-table {
  background: #fff;
  border-radius: 4px;
}
</style>