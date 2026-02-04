<template>
  <div v-if="visible" class="dialog-overlay">
    <div class="dialog-preview">
      <!-- Header -->
      <div class="dialog-header">
        <h2 class="dialog-title">Configure Project: {{ project?.name }}</h2>
        <button class="dialog-close" @click="close">×</button>
      </div>

      <!-- Tabs -->
      <div class="dialog-tabs">
        <div
          :class="['dialog-tab', { active: activeTab === 'parameters' }]"
          @click="activeTab = 'parameters'"
        >
          Parameters
        </div>
        <div
          :class="['dialog-tab', { active: activeTab === 'verbs' }]"
          @click="activeTab = 'verbs'"
        >
          Verbs
        </div>
      </div>

      <!-- Content -->
      <div class="dialog-content">
        <!-- Error/Success Messages -->
        <div v-if="error" class="error-banner">
          <i class="material-icons">error</i>
          {{ error }}
        </div>
        <div v-if="success" class="success-banner">
          <i class="material-icons">check_circle</i>
          {{ success }}
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <i class="material-icons spinning">hourglass_empty</i>
          Loading configuration...
        </div>

        <!-- Parameters Tab -->
        <div v-else-if="activeTab === 'parameters'" class="tab-content active">
          <div v-if="parameters.length === 0" class="empty-state">
            <i class="material-icons">list_alt</i>
            <p>No parameters defined yet</p>
            <button class="btn-add" @click="addParameter">
              <i class="material-icons">add</i>
              Add Parameter
            </button>
          </div>

          <div v-else class="master-detail">
            <!-- Add Parameter Button (before table) -->
            <button class="btn-add-top" @click="addParameter">
              <i class="material-icons">add</i>
              Add Parameter
            </button>

            <!-- Parameters Table -->
            <div class="master-table-container">
              <table class="master-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Required</th>
                    <th>Default</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(param, index) in parameters"
                    :key="index"
                    :class="{ selected: selectedParamIndex === index }"
                    @click="selectParameter(index)"
                  >
                    <td><code>{{ param.name || '(unnamed)' }}</code></td>
                    <td>{{ param.type }}</td>
                    <td>
                      <span :class="['badge', param.required ? 'badge-required' : 'badge-optional']">
                        {{ param.required ? 'Required' : 'Optional' }}
                      </span>
                    </td>
                    <td>{{ formatDefault(param) }}</td>
                    <td class="actions-cell">
                      <button
                        v-if="index > 0"
                        class="btn-icon-small"
                        title="Move Up"
                        @click.stop="moveParameter(index, -1)"
                      >
                        <i class="material-icons">arrow_upward</i>
                      </button>
                      <button
                        v-if="index < parameters.length - 1"
                        class="btn-icon-small"
                        title="Move Down"
                        @click.stop="moveParameter(index, 1)"
                      >
                        <i class="material-icons">arrow_downward</i>
                      </button>
                      <button
                        class="btn-icon-small btn-delete"
                        title="Delete"
                        @click.stop="deleteParameter(index)"
                      >
                        <i class="material-icons">delete</i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Parameter Detail Panel -->
            <div v-if="selectedParamIndex !== null" class="detail-panel">
              <div class="section-header">Basic Information</div>

              <div class="form-group">
                <label class="form-label">Parameter Name</label>
                <input
                  v-model="selectedParameter.name"
                  type="text"
                  class="form-input"
                  placeholder="parameter_name"
                  @input="markUnsaved"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Type</label>
                <select v-model="selectedParameter.type" class="form-input" @change="onTypeChange">
                  <option value="text">Text</option>
                  <option value="int">Integer</option>
                  <option value="bool">Boolean</option>
                  <option value="list">List</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Description</label>
                <input
                  v-model="selectedParameter.description"
                  type="text"
                  class="form-input"
                  placeholder="Parameter description"
                  @input="markUnsaved"
                />
              </div>

              <div class="form-group">
                <label class="checkbox-label">
                  <input v-model="selectedParameter.required" type="checkbox" @change="markUnsaved" />
                  Required
                </label>
              </div>

              <div class="section-header">Parameter Behavior</div>

              <div class="form-group">
                <label class="form-label">CLI Flag (param)</label>
                <input
                  v-model="selectedParameter.param"
                  type="text"
                  class="form-input"
                  placeholder="--flag-name"
                  @input="markUnsaved"
                />
              </div>

              <!-- Type-specific fields -->
              <template v-if="selectedParameter.type === 'int'">
                <div class="section-header">Constraints</div>
                <div class="form-group">
                  <label class="form-label">Minimum Value</label>
                  <input
                    v-model.number="selectedParameter.min"
                    type="number"
                    class="form-input"
                    @input="markUnsaved"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Maximum Value</label>
                  <input
                    v-model.number="selectedParameter.max"
                    type="number"
                    class="form-input"
                    @input="markUnsaved"
                  />
                </div>
              </template>

              <template v-if="selectedParameter.type === 'text'">
                <div class="section-header">Constraints</div>
                <div class="form-group">
                  <label class="form-label">Min Length</label>
                  <input
                    v-model.number="selectedParameter.min_length"
                    type="number"
                    class="form-input"
                    @input="markUnsaved"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Max Length</label>
                  <input
                    v-model.number="selectedParameter.max_length"
                    type="number"
                    class="form-input"
                    @input="markUnsaved"
                  />
                </div>
              </template>

              <template v-if="selectedParameter.type === 'list'">
                <div class="section-header">List Options</div>
                <div
                  v-for="(option, optIndex) in getListValues()"
                  :key="optIndex"
                  class="list-option-row"
                >
                  <input
                    v-model="option.value"
                    class="form-input"
                    placeholder="value"
                    @input="markUnsaved"
                  />
                  <input
                    v-model="option.label"
                    class="form-input"
                    placeholder="label"
                    @input="markUnsaved"
                  />
                  <button class="btn-icon-small btn-delete" @click="removeListValue(optIndex)">
                    <i class="material-icons">close</i>
                  </button>
                </div>
                <button class="btn-secondary" @click="addListValue">
                  <i class="material-icons">add</i>
                  Add Option
                </button>
              </template>

              <!-- Default Value -->
              <div v-if="selectedParameter.type !== 'list'" class="form-group">
                <label class="form-label">Default Value</label>
                <input
                  v-if="selectedParameter.type === 'bool'"
                  v-model="selectedParameter.default"
                  type="checkbox"
                  @change="markUnsaved"
                />
                <input
                  v-else-if="selectedParameter.type === 'int'"
                  v-model.number="selectedParameter.default"
                  type="number"
                  class="form-input"
                  @input="markUnsaved"
                />
                <input
                  v-else
                  v-model="selectedParameter.default"
                  type="text"
                  class="form-input"
                  @input="markUnsaved"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Verbs Tab -->
        <div v-else-if="activeTab === 'verbs'" class="tab-content active">
          <!-- Enable Checkbox -->
          <div class="enable-section">
            <label class="enable-label">
              <input v-model="verbsEnabled" type="checkbox" @change="markUnsaved" />
              <span>Enable Verb/Subcommand Support</span>
            </label>
            <p class="enable-help">Allow this script to have multiple subcommands like git or docker</p>
          </div>

          <template v-if="verbsEnabled">
            <!-- Empty State -->
            <div v-if="verbOptions.length === 0" class="empty-state">
              <i class="material-icons">category</i>
              <p>No verbs defined yet</p>
              <button class="btn-add" @click="addVerb">
                <i class="material-icons">add</i>
                Add Verb
              </button>
            </div>

            <!-- Verbs List with Configuration -->
            <div v-else class="master-detail">
              <!-- Add Verb Button (before table) -->
              <button class="btn-add-top" @click="addVerb">
                <i class="material-icons">add</i>
                Add Verb
              </button>

              <!-- Verbs Table -->
              <div class="master-table-container">
                <table class="master-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Label</th>
                      <th>Description</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(verb, index) in verbOptions"
                      :key="index"
                      :class="{ selected: selectedVerbIndex === index }"
                      @click="selectVerb(index)"
                    >
                      <td><code>{{ verb.name || '(unnamed)' }}</code></td>
                      <td>{{ verb.label || '-' }}</td>
                      <td>{{ truncate(verb.description, 40) }}</td>
                      <td class="actions-cell">
                        <button
                          v-if="index > 0"
                          class="btn-icon-small"
                          title="Move Up"
                          @click.stop="moveVerb(index, -1)"
                        >
                          <i class="material-icons">arrow_upward</i>
                        </button>
                        <button
                          v-if="index < verbOptions.length - 1"
                          class="btn-icon-small"
                          title="Move Down"
                          @click.stop="moveVerb(index, 1)"
                        >
                          <i class="material-icons">arrow_downward</i>
                        </button>
                        <button
                          class="btn-icon-small btn-delete"
                          title="Delete"
                          @click.stop="deleteVerb(index)"
                        >
                          <i class="material-icons">delete</i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Verb Configuration (immediately after table) -->
              <div v-if="selectedVerbIndex !== null" class="detail-panel">
                <div class="section-header">Verb Configuration</div>

                <div class="form-group">
                  <label class="form-label">Verb Name</label>
                  <input
                    v-model="selectedVerb.name"
                    class="form-input"
                    placeholder="run, create, delete..."
                    @input="markUnsaved"
                  />
                </div>

                <div class="form-group">
                  <label class="form-label">Display Label</label>
                  <input
                    v-model="selectedVerb.label"
                    class="form-input"
                    placeholder="Run Cleanup"
                    @input="markUnsaved"
                  />
                </div>

                <div class="form-group">
                  <label class="form-label">Description</label>
                  <textarea
                    v-model="selectedVerb.description"
                    class="form-input"
                    rows="2"
                    placeholder="Execute the cleanup process"
                    @input="markUnsaved"
                  ></textarea>
                </div>

                <div v-if="parameters.length > 0" class="section-header">Parameter Selection</div>
                <div v-if="parameters.length > 0" class="parameter-selection-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Parameter</th>
                        <th>Type</th>
                        <th>Use in Verb</th>
                        <th>Required</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="param in parameters" :key="param.name">
                        <td class="param-name">{{ param.name }}</td>
                        <td class="param-type">{{ param.type }}</td>
                        <td class="param-checkbox">
                          <label class="checkbox-label-inline">
                            <input
                              type="checkbox"
                              :checked="isParameterSelected(param.name)"
                              @change="toggleParameter(param.name, $event)"
                            />
                          </label>
                        </td>
                        <td class="param-checkbox">
                          <label class="checkbox-label-inline">
                            <input
                              type="checkbox"
                              :checked="isParameterRequired(param.name)"
                              :disabled="!isParameterSelected(param.name)"
                              @change="toggleRequired(param.name, $event)"
                            />
                          </label>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div v-if="parameters.length === 0" class="empty-message">
                    No parameters defined. Add parameters in the Parameters tab first.
                  </div>
                </div>
              </div>

              <!-- Global Settings (Collapsible) - after Verb Configuration -->
              <div class="global-settings">
                <div class="global-header" @click="globalExpanded = !globalExpanded">
                  <span>Global Verb Settings</span>
                  <i class="material-icons">{{ globalExpanded ? 'expand_less' : 'expand_more' }}</i>
                </div>
                <div v-show="globalExpanded" class="global-content">
                  <div class="form-group">
                    <label class="form-label">Parameter Name</label>
                    <input
                      v-model="verbsConfig.parameter_name"
                      class="form-input"
                      placeholder="verb"
                      @input="markUnsaved"
                    />
                  </div>
                  <div class="form-group">
                    <label class="checkbox-label">
                      <input v-model="verbsConfig.required" type="checkbox" @change="markUnsaved" />
                      Verb selection required (user must choose a verb to execute)
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Footer -->
      <div class="dialog-footer">
        <button class="btn-secondary" @click="close">Cancel</button>
        <button class="btn-primary" :disabled="saving || !hasUnsavedChanges" @click="save">
          <i v-if="saving" class="material-icons spinning">hourglass_empty</i>
          <i v-else class="material-icons">save</i>
          {{ saving ? 'Saving...' : 'Save Configuration' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { axiosInstance } from '@/common/utils/axios_utils';

export default {
  name: 'ProjectConfigPlaygroundModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    project: {
      type: Object,
      default: null
    }
  },

  emits: ['close', 'saved'],

  data() {
    return {
      activeTab: 'parameters',
      loading: false,
      saving: false,
      error: null,
      success: null,
      hasUnsavedChanges: false,

      // Parameters
      parameters: [],
      selectedParamIndex: null,

      // Verbs
      verbsEnabled: false,
      verbsConfig: {
        parameter_name: 'verb',
        required: false,
        default: null,
        options: []
      },
      selectedVerbIndex: null,
      globalExpanded: false
    };
  },

  computed: {
    selectedParameter() {
      return this.selectedParamIndex !== null ? this.parameters[this.selectedParamIndex] : null;
    },

    verbOptions() {
      return this.verbsConfig.options || [];
    },

    selectedVerb() {
      return this.selectedVerbIndex !== null ? this.verbOptions[this.selectedVerbIndex] : null;
    }
  },

  watch: {
    visible(newVal) {
      if (newVal && this.project) {
        this.loadConfiguration();
      } else {
        this.reset();
      }
    }
  },

  mounted() {
    // Add Esc key listener
    this.handleEscape = (event) => {
      if (event.key === 'Escape' && this.visible) {
        this.close();
      }
    };
    document.addEventListener('keydown', this.handleEscape);
  },

  beforeUnmount() {
    // Remove Esc key listener
    document.removeEventListener('keydown', this.handleEscape);
  },

  methods: {
    async loadConfiguration() {
      if (!this.project) return;

      this.loading = true;
      this.error = null;

      try {
        const response = await axiosInstance.get(`/admin/projects/${this.project.id}/config`);
        const config = response.data;

        this.parameters = config.parameters || [];
        this.verbsConfig = config.verbs || {
          parameter_name: 'verb',
          required: false,
          default: null,
          options: []
        };
        this.verbsEnabled = !!config.verbs;
        this.hasUnsavedChanges = false;
      } catch (err) {
        console.error('Failed to load project configuration:', err);
        this.error = err.response?.data?.message || 'Failed to load configuration';
      } finally {
        this.loading = false;
      }
    },

    async save() {
      this.saving = true;
      this.error = null;
      this.success = null;

      try {
        // Save parameters
        await axiosInstance.put(`/admin/projects/${this.project.id}/parameters`, {
          parameters: this.parameters
        });

        // Save verbs
        await axiosInstance.put(`/admin/projects/${this.project.id}/verbs`, {
          verbs: this.verbsEnabled ? this.verbsConfig : null,
          sharedParameters: []
        });

        this.success = 'Configuration saved successfully!';
        this.hasUnsavedChanges = false;

        setTimeout(() => {
          this.$emit('saved', this.project);
          this.close();
        }, 1500);
      } catch (err) {
        console.error('Failed to save configuration:', err);
        this.error = err.response?.data?.message || 'Failed to save configuration';
      } finally {
        this.saving = false;
      }
    },

    close() {
      if (this.hasUnsavedChanges) {
        if (!confirm('You have unsaved changes. Are you sure you want to close?')) {
          return;
        }
      }
      this.$emit('close');
    },

    reset() {
      this.activeTab = 'parameters';
      this.parameters = [];
      this.verbsConfig = {
        parameter_name: 'verb',
        required: false,
        default: null,
        options: []
      };
      this.verbsEnabled = false;
      this.selectedParamIndex = null;
      this.selectedVerbIndex = null;
      this.hasUnsavedChanges = false;
      this.error = null;
      this.success = null;
    },

    markUnsaved() {
      this.hasUnsavedChanges = true;
    },

    // Parameter methods
    selectParameter(index) {
      this.selectedParamIndex = index;
    },

    addParameter() {
      this.parameters.push({
        name: '',
        type: 'text',
        description: '',
        required: false,
        param: '',
        default: null
      });
      this.selectedParamIndex = this.parameters.length - 1;
      this.markUnsaved();
    },

    deleteParameter(index) {
      if (confirm('Delete this parameter?')) {
        this.parameters.splice(index, 1);
        if (this.selectedParamIndex === index) {
          this.selectedParamIndex = null;
        } else if (this.selectedParamIndex > index) {
          this.selectedParamIndex--;
        }
        this.markUnsaved();
      }
    },

    moveParameter(index, direction) {
      const newIndex = index + direction;
      if (newIndex >= 0 && newIndex < this.parameters.length) {
        [this.parameters[index], this.parameters[newIndex]] = [
          this.parameters[newIndex],
          this.parameters[index]
        ];
        if (this.selectedParamIndex === index) {
          this.selectedParamIndex = newIndex;
        }
        this.markUnsaved();
      }
    },

    formatDefault(param) {
      if (param.default === null || param.default === undefined) return '-';
      if (param.type === 'bool') return param.default ? 'true' : 'false';
      return String(param.default);
    },

    onTypeChange() {
      if (this.selectedParameter.type === 'list' && !this.selectedParameter.values) {
        this.selectedParameter.values = [];
      }
      this.markUnsaved();
    },

    getListValues() {
      if (!this.selectedParameter.values) {
        this.selectedParameter.values = [];
      }
      return this.selectedParameter.values;
    },

    addListValue() {
      if (!this.selectedParameter.values) {
        this.selectedParameter.values = [];
      }
      this.selectedParameter.values.push({ value: '', label: '' });
      this.markUnsaved();
    },

    removeListValue(optionIndex) {
      this.selectedParameter.values.splice(optionIndex, 1);
      this.markUnsaved();
    },

    // Verb methods
    selectVerb(index) {
      this.selectedVerbIndex = index;
    },

    addVerb() {
      if (!this.verbsConfig.options) {
        this.verbsConfig.options = [];
      }
      this.verbsConfig.options.push({
        name: '',
        label: '',
        description: '',
        parameters: [],
        required_parameters: []
      });
      this.selectedVerbIndex = this.verbsConfig.options.length - 1;
      this.markUnsaved();
    },

    deleteVerb(index) {
      if (confirm('Delete this verb?')) {
        this.verbsConfig.options.splice(index, 1);
        if (this.selectedVerbIndex === index) {
          this.selectedVerbIndex = null;
        } else if (this.selectedVerbIndex > index) {
          this.selectedVerbIndex--;
        }
        this.markUnsaved();
      }
    },

    moveVerb(index, direction) {
      const newIndex = index + direction;
      if (newIndex >= 0 && newIndex < this.verbOptions.length) {
        [this.verbOptions[index], this.verbOptions[newIndex]] = [
          this.verbOptions[newIndex],
          this.verbOptions[index]
        ];
        if (this.selectedVerbIndex === index) {
          this.selectedVerbIndex = newIndex;
        }
        this.markUnsaved();
      }
    },

    isParameterSelected(paramName) {
      return this.selectedVerb?.parameters?.includes(paramName) || false;
    },

    toggleParameter(paramName, event) {
      if (!this.selectedVerb.parameters) {
        this.selectedVerb.parameters = [];
      }
      if (event.target.checked) {
        if (!this.selectedVerb.parameters.includes(paramName)) {
          this.selectedVerb.parameters.push(paramName);
        }
      } else {
        this.selectedVerb.parameters = this.selectedVerb.parameters.filter(p => p !== paramName);
        // Also remove from required if unchecked
        if (this.selectedVerb.required_parameters) {
          this.selectedVerb.required_parameters = this.selectedVerb.required_parameters.filter(
            p => p !== paramName
          );
        }
      }
      this.markUnsaved();
    },

    isParameterRequired(paramName) {
      return this.selectedVerb?.required_parameters?.includes(paramName) || false;
    },

    toggleRequired(paramName, event) {
      if (!this.selectedVerb.required_parameters) {
        this.selectedVerb.required_parameters = [];
      }
      if (event.target.checked) {
        if (!this.selectedVerb.required_parameters.includes(paramName)) {
          this.selectedVerb.required_parameters.push(paramName);
        }
      } else {
        this.selectedVerb.required_parameters = this.selectedVerb.required_parameters.filter(
          p => p !== paramName
        );
      }
      this.markUnsaved();
    },

    truncate(text, maxLength) {
      if (!text) return '-';
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
  }
};
</script>

<style scoped>
/* Match playground dark theme exactly */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.dialog-preview {
  width: 900px;
  max-width: 95%;
  max-height: 90vh;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  color: #e0e0e0;
}

/* Header */
.dialog-header {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #333;
  flex-shrink: 0;
}

.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: #e0e0e0;
  margin: 0;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 32px;
  color: #999;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.dialog-close:hover {
  background: #252525;
  color: #e0e0e0;
}

/* Tabs */
.dialog-tabs {
  display: flex;
  background: #252525;
  border-bottom: 1px solid #333;
  flex-shrink: 0;
}

.dialog-tab {
  padding: 12px 24px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  font-size: 14px;
  font-weight: 500;
  color: #999;
  transition: all 0.2s;
}

.dialog-tab:hover {
  background: #2a2a2a;
  color: #ccc;
}

.dialog-tab.active {
  color: #4a90e2;
  border-bottom-color: #4a90e2;
  background: #1e1e1e;
}

/* Content */
.dialog-content {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.tab-content {
  display: none;
}

.tab-content.active {
  display: block;
}

/* Messages */
.error-banner,
.success-banner {
  padding: 12px 16px;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.error-banner {
  background: #4a2626;
  color: #ff8a80;
  border-left: 3px solid #ff8a80;
}

.success-banner {
  background: #264a26;
  color: #80ff80;
  border-left: 3px solid #80ff80;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.loading-state .material-icons {
  font-size: 48px;
  margin-bottom: 16px;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-state .material-icons {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 8px 0 16px 0;
  font-size: 16px;
}

/* Master-Detail */
.master-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.master-table-container {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #333;
  border-radius: 4px;
  background: #2a2a2a;
}

.master-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.master-table thead {
  position: sticky;
  top: 0;
  background: #252525;
  z-index: 1;
}

.master-table th {
  text-align: left;
  padding: 12px;
  font-weight: 600;
  color: #ccc;
  border-bottom: 2px solid #333;
}

.master-table tbody tr {
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #2a2a2a;
}

.master-table tbody tr:hover {
  background: #252525;
}

.master-table tbody tr.selected {
  background: #1a3a52;
}

.master-table td {
  padding: 6px 12px;
  color: #ccc;
}

.master-table code {
  font-family: 'Courier New', monospace;
  background: #252525;
  padding: 2px 6px;
  border-radius: 3px;
  color: #4a90e2;
}

.actions-cell {
  text-align: right;
  white-space: nowrap;
}

.btn-icon-small {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
  color: #999;
  display: inline-flex;
  align-items: center;
}

.btn-icon-small:hover {
  background: #333;
  color: #e0e0e0;
}

.btn-icon-small.btn-delete:hover {
  background: #4a2626;
  color: #ff8a80;
}

.btn-icon-small .material-icons {
  font-size: 18px;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.badge-required {
  background: #4a2626;
  color: #ff8a80;
}

.badge-optional {
  background: #264a26;
  color: #80ff80;
}

/* Detail Panel */
.detail-panel {
  border: 1px solid #333;
  border-radius: 4px;
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
  background: #2a2a2a;
}

.section-header {
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 8px;
  color: #e0e0e0;
  border-bottom: 2px solid #333;
  font-size: 14px;
}

/* Forms */
.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #ccc;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
  background: #2a2a2a;
  border: 1px solid #3a3a3a;
  color: #e0e0e0;
  font-family: inherit;
}

.form-input:focus {
  outline: none;
  border-color: #4a90e2;
}

textarea.form-input {
  resize: vertical;
  font-family: inherit;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #ccc;
  cursor: pointer;
}

input[type='checkbox'] {
  /* Force native checkbox appearance - override Materialize */
  width: 16px;
  height: 16px;
  margin: 0;
  cursor: pointer;
  /* Show native checkbox (not Materialize's custom one) */
  opacity: 1 !important;
  position: relative !important;
  pointer-events: auto !important;
  -webkit-appearance: checkbox;
  -moz-appearance: checkbox;
  appearance: checkbox;
}

/* Override Materialize's checkbox pseudo-elements */
input[type='checkbox'] + span:before,
input[type='checkbox'] + span:after {
  display: none !important;
}

/* Parameter Selection Table */
.parameter-selection-table {
  margin-top: 8px;
}

.parameter-selection-table table {
  width: 100%;
  border-collapse: collapse;
  background: #252525;
  border: 1px solid #3a3a3a;
  border-radius: 4px;
}

.parameter-selection-table thead {
  background: #2a2a2a;
}

.parameter-selection-table th {
  padding: 8px 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #888;
  border-bottom: 1px solid #3a3a3a;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.parameter-selection-table td {
  padding: 6px 12px;
  font-size: 13px;
  color: #ccc;
  border-bottom: 1px solid #2a2a2a;
}

.parameter-selection-table tbody tr:last-child td {
  border-bottom: none;
}

.parameter-selection-table tbody tr:hover {
  background: #2a2a2a;
}

.parameter-selection-table .param-name {
  font-weight: 500;
  color: #e0e0e0;
}

.parameter-selection-table .param-type {
  color: #888;
  font-size: 12px;
}

.parameter-selection-table .param-checkbox {
  text-align: center;
  width: 80px;
}

.checkbox-label-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.parameter-selection-table input[type='checkbox']:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.parameter-selection-table .empty-message {
  padding: 24px;
  text-align: center;
  color: #888;
  font-size: 13px;
}

/* List Options */
.list-option-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

/* Enable Section */
.enable-section {
  padding: 16px;
  background: #252525;
  border-radius: 4px;
  border: 1px solid #333;
  margin-bottom: 16px;
}

.enable-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.enable-label input {
  width: 18px;
  height: 18px;
}

.enable-help {
  margin: 8px 0 0 26px;
  font-size: 13px;
  color: #999;
}

/* Global Settings */
.global-settings {
  border: 1px solid #333;
  border-radius: 4px;
  background: #252525;
  margin-bottom: 16px;
}

.global-header {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-weight: 500;
  color: #e0e0e0;
}

.global-header:hover {
  background: #2a2a2a;
}

.global-header .material-icons {
  color: #999;
}

.global-content {
  padding: 16px;
  border-top: 1px solid #333;
}

/* Checkbox Grid */
.checkbox-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 8px;
}

/* Buttons */
.btn-add,
.btn-add-top,
.btn-add-bottom {
  background: #4a90e2;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}

.btn-add:hover,
.btn-add-top:hover,
.btn-add-bottom:hover {
  background: #357abd;
}

.btn-add-top {
  margin-bottom: 16px;
}

.btn-add-bottom {
  margin-top: 16px;
}

.btn-secondary {
  background: #2a2a2a;
  color: #e0e0e0;
  border: 1px solid #3a3a3a;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #333;
}

.btn-primary {
  background: #4a90e2;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #357abd;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary .material-icons,
.btn-secondary .material-icons,
.btn-add .material-icons,
.btn-add-bottom .material-icons {
  font-size: 18px;
}

/* Footer */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #333;
  background: #1e1e1e;
  flex-shrink: 0;
}

/* Animation */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.spinning {
  animation: spin 1s linear infinite;
}
</style>
