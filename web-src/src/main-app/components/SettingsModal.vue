<template>
  <div v-if="visible" class="settings-modal-overlay" @click.self="close">
    <div class="settings-modal">
      <div class="modal-header">
        <span class="modal-title">Settings</span>
      </div>

      <div class="modal-body">
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
      </div>

      <div class="modal-footer">
        <button class="btn waves-effect" @click="close">Cancel</button>
        <button class="btn waves-effect btn-primary" @click="save">Save</button>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex';

export default {
  name: 'SettingsModal',

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
      saving: false
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
        // Still close on error - client settings were saved
        this.close();
      } finally {
        this.saving = false;
      }
    }
  }
};
</script>

<style scoped>
.settings-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.settings-modal {
  background: var(--background-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  width: 85%;
  max-width: 400px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  flex-direction: column;
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
  padding: 16px 24px;
  overflow-y: auto;
  flex: 1;
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
.setting-input:invalid,
.setting-input.invalid,
.setting-input:focus:invalid {
  border-color: var(--separator-color);
  box-shadow: none;
  border-bottom: 1px solid var(--separator-color);
}

.setting-input:focus:invalid {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(38, 166, 154, 0.2);
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
