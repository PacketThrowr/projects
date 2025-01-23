<template>
  <div class="page-content">
    <div class="user-management">
      <div class="header">
        <h2>User Management</h2>
        <button @click="showCreateModal = true" class="add-button">Add User</button>
      </div>

      <!-- Users Table -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.is_superuser ? 'Admin' : 'User' }}</td>
            <td>
                <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
            </td>
            <td>
                <button @click="editUser(user)" class="action-button edit">Edit</button>
                <button @click="confirmDelete(user)" class="action-button delete">Delete</button>
            </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Create/Edit Modal -->
      <div v-if="showCreateModal || showEditModal" class="modal">
        <div class="modal-content">
          <h2>{{ showEditModal ? 'Edit User' : 'Create User' }}</h2>
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label for="username">Username</label>
              <input 
                type="text" 
                id="username" 
                v-model="formData.username" 
                required
              >
            </div>
            <div class="form-group">
              <label for="email">Email</label>
              <input 
                type="email" 
                id="email" 
                v-model="formData.email" 
                required
              >
            </div>
            <div class="form-group">
              <label for="password">
                Password {{ showEditModal ? '(Leave blank to keep current)' : '' }}
              </label>
              <input 
                type="password" 
                id="password" 
                v-model="formData.password"
                :required="!showEditModal"
              >
            </div>
            <div class="form-group checkbox">
              <label>
                <input 
                  type="checkbox" 
                  v-model="formData.is_superuser"
                >
                Admin User
              </label>
            </div>
            <div class="form-group checkbox">
              <label>
                <input 
                  type="checkbox" 
                  v-model="formData.is_active"
                >
                Active
              </label>
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeModal" class="cancel-button">Cancel</button>
              <button type="submit" class="submit-button">
                {{ showEditModal ? 'Save Changes' : 'Create User' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="modal">
        <div class="modal-content">
          <h2>Confirm Delete</h2>
          <p>Are you sure you want to delete user "{{ userToDelete?.username }}"?</p>
          <div class="modal-actions">
            <button @click="showDeleteModal = false" class="cancel-button">Cancel</button>
            <button @click="deleteUser" class="delete-button">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { API_BASE_URL } from '../config';

export default {
  name: 'UserManagement',
  setup() {
    const users = ref([]);
    const showCreateModal = ref(false);
    const showEditModal = ref(false);
    const showDeleteModal = ref(false);
    const userToDelete = ref(null);
    const formData = ref({
      username: '',
      email: '',
      password: '',
      is_superuser: false,
      is_active: true
    });

    const fetchUsers = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/api/users`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (!response.ok) throw new Error('Failed to fetch users');
        users.value = await response.json();
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };

    const handleSubmit = async () => {
      try {
        const token = localStorage.getItem('token');
        
        if (showEditModal.value) {
          // Editing existing user - include all required fields
          const dataToSend = {
            username: formData.value.username,
            email: formData.value.email,
            is_active: formData.value.is_active,
            is_superuser: formData.value.is_superuser,
            is_verified: formData.value.is_verified || false  // Include the is_verified field
          };
          
          // Only include password if it's been entered
          if (formData.value.password) {
            dataToSend.password = formData.value.password;
          }
          console.log('PUT Request Data:', dataToSend);
          console.log('Form Data Password:', formData.value.password);
          console.log('ID:', formData.value.id);
          const response = await fetch(`${API_BASE_URL}/api/users/${formData.value.id}/`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSend)
          });

          if (!response.ok) throw new Error('Failed to update user');
        } else {
          // Creating new user - send all fields
          const response = await fetch(`${API_BASE_URL}/api/users`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData.value)
          });

          if (!response.ok) throw new Error('Failed to create user');
        }
        
        await fetchUsers();
        closeModal();
      } catch (error) {
        console.error('Error saving user:', error);
      }
    };

    const editUser = (user) => {
      formData.value = { ...user };
      formData.value.password = ''; // Clear password field for editing
      showEditModal.value = true;
    };

    const confirmDelete = (user) => {
      userToDelete.value = user;
      showDeleteModal.value = true;
    };

    const deleteUser = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/api/users/${userToDelete.value.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) throw new Error('Failed to delete user');
        
        await fetchUsers();
        showDeleteModal.value = false;
        userToDelete.value = null;
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    };

    const closeModal = () => {
      showCreateModal.value = false;
      showEditModal.value = false;
      formData.value = {
        username: '',
        email: '',
        password: '',
        is_superuser: false,
        is_active: true
      };
    };

    onMounted(fetchUsers);

    return {
      users,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      userToDelete,
      formData,
      handleSubmit,
      editUser,
      confirmDelete,
      deleteUser,
      closeModal
    };
  }
};
</script>

<style scoped>
.user-management {
  width: 100%;
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.add-button {
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.add-button:hover {
  background-color: #45a049;
}

.table-container {
  background-color: var(--menu-bar-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  color: var(--text-color);
}

.users-table th,
.users-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--background-color);
}

.users-table th {
  background-color: rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.875rem;
}

.status-badge.active {
  background-color: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.status-badge.inactive {
  background-color: rgba(244, 67, 54, 0.2);
  color: #F44336;
}

.action-button {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 0.5rem;
  font-size: 0.875rem;
}

.action-button.edit {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--text-color);
}

.action-button.delete {
  background-color: rgba(244, 67, 54, 0.1);
  color: #F44336;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--menu-bar-color);
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  color: var(--text-color);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"] {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  background-color: var(--background-color);
  color: var(--text-color);
}

.form-group.checkbox {
  display: flex;
  align-items: center;
}

.form-group.checkbox label {
  margin-bottom: 0;
  margin-left: 0.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.cancel-button,
.submit-button,
.delete-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-button {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--text-color);
}

.submit-button {
  background-color: #4CAF50;
  color: white;
}

.delete-button {
  background-color: #F44336;
  color: white;
}
</style>