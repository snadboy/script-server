<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content user-management-modal card">
      <div class="modal-header">
        <span class="modal-title">User Management</span>
      </div>

      <div class="modal-body">
        <!-- Default Password Warning Banner -->
        <div v-if="usingDefaultPassword" class="default-password-warning">
          <i class="material-icons">warning</i>
          <span>
            <strong>Security Warning:</strong> The default admin password is still in use.
            Please change the password for user "{{ defaultPasswordUser }}" immediately.
          </span>
        </div>

        <div class="section-header">
          <div class="auth-info">
            <h6>Users</h6>
            <span v-if="authStatus" class="user-count">({{ authStatus.user_count }} users)</span>
          </div>
          <button class="btn waves-effect waves-light" @click="showAddUserDialog = true">
            <i class="material-icons left">person_add</i>
            Add User
          </button>
        </div>

        <div v-if="loading" class="loading-spinner">
          <div class="preloader-wrapper active">
            <div class="spinner-layer spinner-primary-only">
              <div class="circle-clipper left"><div class="circle"></div></div>
              <div class="gap-patch"><div class="circle"></div></div>
              <div class="circle-clipper right"><div class="circle"></div></div>
            </div>
          </div>
        </div>

        <div v-else-if="users.length === 0" class="no-users">
          <p>No users configured. Add a user to enable authentication.</p>
        </div>

        <table v-else class="striped highlight">
          <thead>
            <tr>
              <th>Username</th>
              <th>Admin</th>
              <th>Code Editor</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.username">
              <td>{{ user.username }}</td>
              <td>
                <label>
                  <input type="checkbox" class="filled-in"
                         :checked="user.is_admin"
                         @click.prevent="toggleAdmin(user)" />
                  <span></span>
                </label>
              </td>
              <td>
                <label>
                  <input type="checkbox" class="filled-in"
                         :checked="user.is_admin || user.is_code_editor"
                         :disabled="user.is_admin"
                         @click.prevent="toggleCodeEditor(user)" />
                  <span></span>
                </label>
              </td>
              <td class="actions">
                <button class="btn-flat waves-effect" @click="showPasswordDialog(user)"
                        title="Change Password">
                  <i class="material-icons">vpn_key</i>
                </button>
                <button class="btn-flat waves-effect" @click="confirmDeleteUser(user)"
                        title="Delete User">
                  <i class="material-icons red-text">delete</i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Add User Dialog (nested modal) -->
        <div v-if="showAddUserDialog" class="nested-modal-overlay" @click.self="closeAddUserDialog">
          <div class="nested-modal-content card">
            <div class="card-content">
              <span class="card-title">Add New User</span>
              <div class="input-field">
                <input id="new-username" type="text" v-model="newUser.username" />
                <label for="new-username">Username</label>
              </div>
              <div class="input-field password-field">
                <input id="new-password" :type="showNewPassword ? 'text' : 'password'" v-model="newUser.password" />
                <label for="new-password">Password</label>
                <button type="button" class="btn-flat password-toggle" @click="showNewPassword = !showNewPassword">
                  <i class="material-icons">{{ showNewPassword ? 'visibility_off' : 'visibility' }}</i>
                </button>
              </div>
              <div class="input-field">
                <label>
                  <input type="checkbox" class="filled-in" v-model="newUser.is_admin" />
                  <span>Admin User</span>
                </label>
              </div>
              <div v-if="addUserError" class="error-message">{{ addUserError }}</div>
            </div>
            <div class="card-action">
              <button class="btn-flat waves-effect" @click="closeAddUserDialog">Cancel</button>
              <button class="btn waves-effect waves-light" @click="addUser" :disabled="!canAddUser">
                Add User
              </button>
            </div>
          </div>
        </div>

        <!-- Change Password Dialog (nested modal) -->
        <div v-if="showChangePasswordDialog" class="nested-modal-overlay" @click.self="closeChangePasswordDialog">
          <div class="nested-modal-content card">
            <div class="card-content">
              <span class="card-title">Change Password for {{ selectedUser?.username }}</span>
              <div class="input-field password-field">
                <input id="change-password" :type="showChangePassword ? 'text' : 'password'" v-model="newPassword" />
                <label for="change-password">New Password</label>
                <button type="button" class="btn-flat password-toggle" @click="showChangePassword = !showChangePassword">
                  <i class="material-icons">{{ showChangePassword ? 'visibility_off' : 'visibility' }}</i>
                </button>
              </div>
              <div v-if="changePasswordError" class="error-message">{{ changePasswordError }}</div>
            </div>
            <div class="card-action">
              <button class="btn-flat waves-effect" @click="closeChangePasswordDialog">Cancel</button>
              <button class="btn waves-effect waves-light" @click="changePassword" :disabled="!newPassword">
                Change Password
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-flat waves-effect" @click="handleClose">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';

export default {
  name: 'UserManagementModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      users: [],
      authStatus: null,
      loading: true,
      usingDefaultPassword: false,
      defaultPasswordUser: null,
      showAddUserDialog: false,
      showChangePasswordDialog: false,
      showNewPassword: false,
      showChangePassword: false,
      selectedUser: null,
      newUser: {
        username: '',
        password: '',
        is_admin: false
      },
      newPassword: '',
      addUserError: '',
      changePasswordError: '',
      boundFixOverlayDimensions: null,
      originalParent: null
    };
  },

  computed: {
    canAddUser() {
      return this.newUser.username.trim() && this.newUser.password.trim();
    },
    hasAdminUsers() {
      return this.users.some(u => u.is_admin);
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden';
        this.fetchData();
        // Move modal to body to avoid transform containment issues from parent elements
        this.$nextTick(() => {
          this.originalParent = this.$el.parentElement;
          document.body.appendChild(this.$el);
          this.boundFixOverlayDimensions = this.fixOverlayDimensions.bind(this);
          this.boundFixOverlayDimensions();
          window.addEventListener('resize', this.boundFixOverlayDimensions);
        });
      } else {
        document.body.style.overflow = '';
        if (this.boundFixOverlayDimensions) {
          window.removeEventListener('resize', this.boundFixOverlayDimensions);
        }
        // Move modal back to original parent
        if (this.originalParent && this.$el.parentElement === document.body) {
          this.originalParent.appendChild(this.$el);
        }
      }
    }
  },

  methods: {
    fixOverlayDimensions() {
      const overlay = this.$el;
      if (overlay && overlay.classList.contains('modal-overlay')) {
        overlay.style.height = window.innerHeight + 'px';
        overlay.style.width = window.innerWidth + 'px';
      }
    },

    handleClose() {
      this.$emit('close');
    },

    async fetchData() {
      this.loading = true;
      try {
        const [usersRes, statusRes, defaultPwdRes] = await Promise.all([
          axiosInstance.get('admin/users'),
          axiosInstance.get('admin/auth/status'),
          axiosInstance.get('admin/auth/default-password-status')
        ]);
        this.users = usersRes.data.users || [];
        this.authStatus = statusRes.data;
        this.usingDefaultPassword = defaultPwdRes.data.using_default_password || false;
        this.defaultPasswordUser = defaultPwdRes.data.default_user || null;
      } catch (e) {
        console.error('Failed to fetch user data:', e);
        M.toast({html: 'Failed to load user data'});
      } finally {
        this.loading = false;
      }
    },

    async addUser() {
      this.addUserError = '';
      try {
        await axiosInstance.post('admin/users/add', this.newUser);
        M.toast({html: `User ${this.newUser.username} added`});
        this.closeAddUserDialog();
        await this.fetchData();
      } catch (e) {
        this.addUserError = this.getErrorMessage(e, 'Failed to add user');
      }
    },

    closeAddUserDialog() {
      this.showAddUserDialog = false;
      this.showNewPassword = false;
      this.newUser = { username: '', password: '', is_admin: !this.hasAdminUsers };
      this.addUserError = '';
    },

    closeChangePasswordDialog() {
      this.showChangePasswordDialog = false;
      this.showChangePassword = false;
      this.newPassword = '';
      this.changePasswordError = '';
    },

    async confirmDeleteUser(user) {
      if (confirm(`Delete user "${user.username}"? This cannot be undone.`)) {
        try {
          await axiosInstance.delete(`admin/users/${encodeURIComponent(user.username)}`);
          M.toast({html: `User ${user.username} deleted`});
          await this.fetchData();
        } catch (e) {
          const message = this.getErrorMessage(e, 'Failed to delete user');
          M.toast({html: message, classes: 'red'});
        }
      }
    },

    showPasswordDialog(user) {
      this.selectedUser = user;
      this.newPassword = '';
      this.changePasswordError = '';
      this.showChangePasswordDialog = true;
    },

    async changePassword() {
      this.changePasswordError = '';
      try {
        await axiosInstance.post(
          `admin/users/${encodeURIComponent(this.selectedUser.username)}/password`,
          { password: this.newPassword }
        );
        M.toast({html: 'Password changed'});
        this.closeChangePasswordDialog();
      } catch (e) {
        this.changePasswordError = this.getErrorMessage(e, 'Failed to change password');
      }
    },

    getErrorMessage(e, fallback) {
      const data = e.response?.data;
      if (typeof data === 'string') {
        return data || fallback;
      }
      return data?.reason || fallback;
    },

    async toggleAdmin(user) {
      try {
        await axiosInstance.post(
          `admin/users/${encodeURIComponent(user.username)}/roles`,
          { is_admin: !user.is_admin, is_code_editor: user.is_code_editor }
        );
        await this.fetchData();
      } catch (e) {
        const message = this.getErrorMessage(e, 'Failed to update user roles');
        M.toast({html: message, classes: 'red'});
        await this.fetchData();
      }
    },

    async toggleCodeEditor(user) {
      try {
        await axiosInstance.post(
          `admin/users/${encodeURIComponent(user.username)}/roles`,
          { is_admin: user.is_admin, is_code_editor: !user.is_code_editor }
        );
        await this.fetchData();
      } catch (e) {
        const message = this.getErrorMessage(e, 'Failed to update user roles');
        M.toast({html: message, classes: 'red'});
        await this.fetchData();
      }
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--z-index-modal-overlay);
}

.user-management-modal {
  width: 85%;
  max-width: 800px;
  height: 85vh;
  max-height: 600px;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-md);
  margin: 0 !important;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--separator-color);
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.4em;
  font-weight: 500;
  color: var(--font-color-main);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--separator-color);
  flex-shrink: 0;
  background: var(--background-color-level-16dp);
}

.default-password-warning {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #ffebee;
  border: 1px solid #f44336;
  border-radius: 4px;
  margin-bottom: 20px;
  color: #c62828;
}

.default-password-warning i {
  font-size: 24px;
  color: #f44336;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.auth-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.auth-info h6 {
  margin: 0;
  font-weight: 500;
}

.user-count {
  color: var(--font-color-medium);
  font-size: 0.9em;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.no-users {
  text-align: center;
  padding: 40px;
  color: var(--font-color-medium);
}

table {
  width: 100%;
}

table th, table td {
  padding: 12px 15px;
}

.actions {
  white-space: nowrap;
}

.actions button {
  margin: 0 2px;
  padding: 0 8px;
}

/* Nested modal for Add User / Change Password */
.nested-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--z-index-toast);
}

.nested-modal-content {
  width: 90%;
  max-width: 400px;
}

.password-field {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  padding: 0 8px;
  min-width: auto;
  height: auto;
  line-height: 1;
}

.password-toggle i {
  font-size: 20px;
  color: var(--font-color-medium);
}

.nested-modal-content .card-content {
  padding-bottom: 0;
}

.nested-modal-content .card-action {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.error-message {
  color: #f44336;
  font-size: 0.9em;
  margin-top: 10px;
}

[type="checkbox"].filled-in:checked + span:not(.lever):after {
  border-color: var(--primary-color);
  background-color: var(--primary-color);
}

[type="checkbox"].filled-in:disabled:checked + span:not(.lever):after {
  border-color: #9e9e9e;
  background-color: #9e9e9e;
}

@media screen and (max-width: 768px) {
  .user-management-modal {
    width: 95%;
    height: 95vh;
    max-height: none;
  }

  .modal-body {
    padding: 16px;
  }
}
</style>
