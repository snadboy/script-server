<template>
  <div v-if="visible" class="settings-modal-overlay" @click.self="close">
    <div class="settings-modal">
      <div class="modal-header">
        <h5>Settings</h5>
        <button class="close-btn" @click="close">
          <i class="material-icons">close</i>
        </button>
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
        completedExecutionsLimit: 50
      }
    };
  },

  computed: {
    ...mapState('settings', ['completedExecutionsLimit'])
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        // Load current settings when modal opens
        this.localSettings.completedExecutionsLimit = this.completedExecutionsLimit;
      }
    }
  },

  methods: {
    ...mapActions('settings', ['updateSettings']),

    close() {
      this.$emit('close');
    },

    save() {
      this.updateSettings({
        completedExecutionsLimit: this.localSettings.completedExecutionsLimit
      });
      this.close();
    }
  }
};
</script>

<style scoped>
.settings-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.settings-modal {
  background: var(--background-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  width: 400px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--separator-color);
}

.modal-header h5 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: var(--background-color-high-emphasis);
}

.close-btn i {
  font-size: 24px;
  color: var(--font-color-medium);
}

.modal-body {
  padding: 20px;
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

.setting-input {
  width: 80px;
  padding: 8px 12px;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  background: var(--background-color-slight-emphasis);
  color: var(--font-color-main);
  font-size: 14px;
  text-align: center;
}

.setting-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 20px;
  border-top: 1px solid var(--separator-color);
}

.btn {
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
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
  background: var(--primary-color-dark);
}
</style>
