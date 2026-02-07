<template>
  <BaseModal
    :visible="visible"
    title="Settings"
    modal-class="settings-modal"
    overlay-class="settings-modal-overlay"
    :show-close-button="false"
    @close="close"
  >
    <template #default>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div class="settings-section">
          <h6>Display</h6>

          <div class="setting-row">
            <label for="completedLimit">Completed executions to show</label>
            <input
              id="completedLimit"
              v-model.number="localSettings.completedExecutionsLimit"
              type="number"
              min="10"
              max="500"
              step="10"
              class="setting-input"
            />
          </div>

          <div class="setting-row">
            <label for="logSizeLimit">Log entries to keep (max 250)</label>
            <input
              id="logSizeLimit"
              v-model.number="localSettings.logSizeLimit"
              type="number"
              min="50"
              max="250"
              step="10"
              class="setting-input"
            />
          </div>
        </div>

        <div v-if="isAdmin" class="settings-section">
          <h6>Scheduling</h6>

          <div class="setting-row">
            <div class="setting-label-group">
              <label for="retentionMinutes">One-time schedule retention</label>
              <span class="setting-hint">Minutes to keep completed schedules (-1 = forever)</span>
            </div>
            <input
              id="retentionMinutes"
              v-model.number="localSettings.onetimeRetentionMinutes"
              type="number"
              min="-1"
              max="10080"
              step="5"
              class="setting-input"
            />
          </div>
        </div>
    </template>

    <template #footer>
      <button class="btn waves-effect" @click="close">Cancel</button>
      <button class="btn waves-effect btn-primary" @click="save">Save</button>
    </template>
  </BaseModal>
</template>

<script>
import {mapState, mapActions} from 'vuex';
import BaseModal from '@/common/components/BaseModal.vue';

export default {
  name: 'SettingsModal',

  components: {
    BaseModal
  },

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      localSettings: {
        completedExecutionsLimit: 50,
        logSizeLimit: 250,
        onetimeRetentionMinutes: 60
      },
      saving: false,
      error: null
    };
  },

  computed: {
    ...mapState('settings', ['completedExecutionsLimit', 'logSizeLimit', 'onetimeRetentionMinutes']),
    ...mapState('auth', {
      isAdmin: 'admin'
    })
  },

  watch: {
    async visible(newVal) {
      if (newVal) {
        // Load current settings when modal opens
        this.localSettings.completedExecutionsLimit = this.completedExecutionsLimit;
        this.localSettings.logSizeLimit = this.logSizeLimit;

        // Fetch server-side settings if admin
        if (this.isAdmin) {
          await this.fetchScheduleSettings();
          this.localSettings.onetimeRetentionMinutes = this.onetimeRetentionMinutes;
        }
      }
    }
  },

  methods: {
    ...mapActions('settings', ['updateSettings', 'fetchScheduleSettings', 'updateRetention']),

    close() {
      this.$emit('close');
    },

    async save() {
      this.saving = true;
      try {
        // Save client-side settings
        this.updateSettings({
          completedExecutionsLimit: this.localSettings.completedExecutionsLimit,
          logSizeLimit: this.localSettings.logSizeLimit
        });

        // Save server-side settings if admin
        if (this.isAdmin) {
          await this.updateRetention(this.localSettings.onetimeRetentionMinutes);
        }

        this.close();
      } catch (e) {
        console.error('Failed to save settings:', e);
        this.error = 'Failed to save server settings. Client settings were saved.';
      } finally {
        this.saving = false;
      }
    }
  }
};
</script>

<style scoped>
/* Custom modal sizing */
.settings-modal {
  width: 85%;
  max-width: 400px;
  max-height: 85vh;
}

.settings-section h6 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.setting-row label {
  font-size: 14px;
  color: var(--font-color-main);
}

.setting-label-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.setting-hint {
  font-size: 11px;
  color: var(--font-color-medium);
}

.setting-input {
  width: 80px;
  padding: 8px 10px;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  background: var(--background-color-level-4dp);
  color: var(--font-color-main);
  font-size: 14px;
  text-align: center;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.setting-input:hover {
  border-color: rgba(255, 255, 255, 0.5);
}

.setting-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(38, 166, 154, 0.2);
}

/* Override Materialize validation styling */
.setting-input,
.setting-input:invalid,
.setting-input.invalid,
.setting-input:focus:invalid,
.setting-input[type="number"] {
  border-bottom: 1px solid var(--separator-color) !important;
  box-shadow: none !important;
}

.setting-input:focus,
.setting-input:focus:invalid,
.setting-input[type="number"]:focus {
  border-color: var(--primary-color) !important;
  border-bottom-color: var(--primary-color) !important;
  box-shadow: 0 0 0 2px rgba(38, 166, 154, 0.2) !important;
}

/* Footer styling */
.btn {
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  line-height: 1.2;
  cursor: pointer;
  border: none;
  background: var(--background-color-high-emphasis);
  color: var(--font-color-main);
}

.btn:hover {
  background: var(--background-color-slight-emphasis);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-color-dark-color);
}

@media screen and (max-width: 768px) {
  .settings-modal {
    width: 95%;
    max-height: 95vh;
  }

  .modal-body {
    padding: 16px;
  }
}
</style>
