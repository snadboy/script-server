<template>
  <div v-if="visible" :class="overlayClass">
    <div :class="dialogClass">
      <div :class="headerClass">
        <h5 v-if="!isPlayground" class="modal-title">
          <i class="material-icons">tune</i>
          Configure Project: {{ project?.name }}
        </h5>
        <h2 v-else class="dialog-title">Configure Project: {{ project?.name }}</h2>
        <button :class="closeButtonClass" @click="close">
          <i v-if="!isPlayground" class="material-icons">close</i>
          <template v-else>×</template>
        </button>
      </div>

      <!-- Tabs -->
      <div :class="tabsClass">
        <button
          v-if="!isPlayground"
          :class="['tab-btn', { active: activeTab === 'parameters' }]"
          @click="activeTab = 'parameters'"
        >
          <i class="material-icons">list</i>
          Parameters
        </button>
        <div
          v-else
          :class="['dialog-tab', { active: activeTab === 'parameters' }]"
          @click="activeTab = 'parameters'"
        >
          Parameters
        </div>

        <button
          v-if="!isPlayground"
          :class="['tab-btn', { active: activeTab === 'verbs' }]"
          @click="activeTab = 'verbs'"
        >
          <i class="material-icons">code</i>
          Verbs
        </button>
        <div
          v-else
          :class="['dialog-tab', { active: activeTab === 'verbs' }]"
          @click="activeTab = 'verbs'"
        >
          Verbs
        </div>

        <button
          v-if="!isPlayground"
          :class="['tab-btn', { active: activeTab === 'connections' }]"
          @click="activeTab = 'connections'"
        >
          <i class="material-icons">vpn_key</i>
          Connections
        </button>
        <div
          v-else
          :class="['dialog-tab', { active: activeTab === 'connections' }]"
          @click="activeTab = 'connections'"
        >
          Connections
        </div>
      </div>

      <div :class="contentClass">
        <!-- Error/Success Messages -->
        <div v-if="error" :class="errorClass">
          <i class="material-icons">error</i>
          {{ error }}
        </div>
        <div v-if="success" :class="successClass">
          <i class="material-icons">check_circle</i>
          {{ success }}
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <i class="material-icons spinning">hourglass_empty</i>
          Loading configuration...
        </div>

        <!-- Parameters Tab -->
        <div v-else-if="activeTab === 'parameters'" :class="tabContentClass">
          <!-- Standard mode: use child component -->
          <ProjectParametersEditor
            v-if="!isPlayground"
            v-model="parameters"
            :verbs="verbsConfig"
            :shared-parameters="sharedParameters"
            @update:modelValue="markUnsaved"
            @update:verbs="updateVerbs"
            @update:sharedParameters="updateSharedParameters"
          />

          <!-- Playground mode: inline editor -->
          <template v-else>
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
          </template>
        </div>

        <!-- Verbs Tab -->
        <div v-else-if="activeTab === 'verbs'" :class="tabContentClass">
          <!-- Standard mode: use child component -->
          <VerbConfigEditor
            v-if="!isPlayground"
            v-model:verbs-config="verbsConfig"
            :available-parameters="parameterNames"
            @update:verbsConfig="markUnsaved"
          />

          <!-- Playground mode: inline editor -->
          <template v-else>
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
          </template>
        </div>

        <!-- Connections Tab -->
        <div v-else-if="activeTab === 'connections'" :class="tabContentClass">
          <!-- Standard mode -->
          <div v-if="!isPlayground" class="connections-config">
            <div class="config-section">
              <h3>Supported Connection Types</h3>
              <p class="help-text">
                Select which connection types this script can use. If none selected, all connections will be available.
              </p>
              <div class="connection-types-list">
                <label v-for="connType in availableConnectionTypes" :key="connType.value" class="connection-type-option">
                  <input
                    type="checkbox"
                    :value="connType.value"
                    v-model="supportedConnections"
                    @change="markUnsaved"
                  />
                  <span>
                    <i class="material-icons">{{ connType.icon }}</i>
                    {{ connType.label }}
                  </span>
                </label>
              </div>
            </div>
          </div>

          <!-- Playground mode -->
          <div v-else class="connections-section">
            <p class="section-description">
              Select which connection types this script can use. If none selected, all connections will be available.
            </p>

            <div class="connections-table-container">
              <table class="connections-table">
                <thead>
                  <tr>
                    <th class="col-checkbox">Select</th>
                    <th class="col-name">Connection Type</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="connType in availableConnectionTypes" :key="connType.value">
                    <td class="col-checkbox">
                      <input
                        type="checkbox"
                        :value="connType.value"
                        v-model="supportedConnections"
                        @change="markUnsaved"
                      />
                    </td>
                    <td class="col-name">
                      <i class="material-icons">{{ connType.icon }}</i>
                      <span>{{ connType.label }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div :class="footerClass">
        <button :class="cancelButtonClass" @click="close">Cancel</button>
        <button
          :class="saveButtonClass"
          :disabled="saving || (isStandardMode && !canSave)"
          @click="save"
        >
          <i v-if="saving" class="material-icons spinning">hourglass_empty</i>
          <i v-else class="material-icons">save</i>
          {{ saving ? 'Saving...' : 'Save Configuration' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';
import ProjectParametersEditor from './ProjectParametersEditor.vue';
import VerbConfigEditor from '@/admin/components/scripts-config/VerbConfigEditor.vue';

export default {
  name: 'ProjectConfigModal',

  components: {
    ProjectParametersEditor,
    VerbConfigEditor
  },

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    project: {
      type: Object,
      default: null
    },
    mode: {
      type: String,
      default: 'standard',
      validator: v => ['standard', 'playground'].includes(v)
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

      // Configuration data
      parameters: [],
      verbsConfig: null,
      sharedParameters: [],
      supportedConnections: [],

      // Playground-specific data
      selectedParamIndex: null,
      verbsEnabled: false,
      selectedVerbIndex: null,
      globalExpanded: false,

      // Available connection types (loaded from backend)
      availableConnectionTypes: []
    };
  },

  computed: {
    isPlayground() {
      return this.mode === 'playground';
    },

    isStandardMode() {
      return this.mode === 'standard';
    },

    parameterNames() {
      return this.parameters.map(p => p.name);
    },

    canSave() {
      // On Parameters tab, always allow saving
      if (this.activeTab === 'parameters') {
        return this.hasUnsavedChanges;
      }

      // On Verbs tab, require at least one verb option if verbs are enabled
      if (this.activeTab === 'verbs') {
        if (this.verbsConfig && (!this.verbsConfig.options || this.verbsConfig.options.length === 0)) {
          return false;
        }
        return this.hasUnsavedChanges;
      }

      return this.hasUnsavedChanges;
    },

    // Playground-specific computed properties
    selectedParameter() {
      return this.selectedParamIndex !== null ? this.parameters[this.selectedParamIndex] : null;
    },

    verbOptions() {
      return this.verbsConfig?.options || [];
    },

    selectedVerb() {
      return this.selectedVerbIndex !== null ? this.verbOptions[this.selectedVerbIndex] : null;
    },

    // Dynamic CSS classes based on mode
    overlayClass() {
      return this.isPlayground ? 'dialog-overlay' : 'modal-overlay';
    },

    dialogClass() {
      return this.isPlayground ? 'dialog-preview' : 'modal-dialog project-config-modal';
    },

    headerClass() {
      return this.isPlayground ? 'dialog-header' : 'modal-header';
    },

    closeButtonClass() {
      return this.isPlayground ? 'dialog-close' : 'modal-close';
    },

    tabsClass() {
      return this.isPlayground ? 'dialog-tabs' : 'modal-tabs';
    },

    contentClass() {
      return this.isPlayground ? 'dialog-content' : 'modal-body';
    },

    tabContentClass() {
      return this.isPlayground ? 'tab-content active' : 'tab-content';
    },

    errorClass() {
      return this.isPlayground ? 'error-banner' : 'error-message';
    },

    successClass() {
      return this.isPlayground ? 'success-banner' : 'success-message';
    },

    footerClass() {
      return this.isPlayground ? 'dialog-footer' : 'modal-footer';
    },

    cancelButtonClass() {
      return this.isPlayground ? 'btn-secondary' : 'btn btn-secondary';
    },

    saveButtonClass() {
      return this.isPlayground ? 'btn-primary' : 'btn btn-primary';
    }
  },

  watch: {
    visible(newVal) {
      if (newVal && this.project) {
        this.loadConfiguration();
        this.loadConnectionTypes();
      } else {
        this.reset();
      }
    },

    supportedConnections() {
      this.markUnsaved();
    }
  },

  mounted() {
    if (this.isPlayground) {
      // Add Esc key listener for playground mode
      this.handleEscape = (event) => {
        if (event.key === 'Escape' && this.visible) {
          this.close();
        }
      };
      document.addEventListener('keydown', this.handleEscape);
    }
  },

  beforeUnmount() {
    if (this.isPlayground && this.handleEscape) {
      // Remove Esc key listener
      document.removeEventListener('keydown', this.handleEscape);
    }
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
        this.verbsConfig = config.verbs || (this.isPlayground ? {
          parameter_name: 'verb',
          required: false,
          default: null,
          options: []
        } : null);
        this.verbsEnabled = !!config.verbs;
        this.sharedParameters = config.sharedParameters || [];
        this.supportedConnections = config.supported_connections || [];
        this.hasUnsavedChanges = false;
      } catch (err) {
        console.error('Failed to load project configuration:', err);
        this.error = err.response?.data?.message || 'Failed to load configuration';
      } finally {
        this.loading = false;
      }
    },

    async loadConnectionTypes() {
      // Skip if already loaded
      if (this.availableConnectionTypes.length > 0) return;

      try {
        const response = await axiosInstance.get('/admin/connections/types');
        const types = response.data.types || [];

        // Transform backend format to UI format
        this.availableConnectionTypes = types.map(type => ({
          value: type.type_id,
          label: type.display_name,
          icon: type.icon
        }));
      } catch (err) {
        console.error('Failed to load connection types:', err);
        // Fallback to empty array - UI will still work, just no connection options
      }
    },

    async save() {
      this.saving = true;
      this.error = null;
      this.success = null;

      try {
        // Save parameters
        await axiosInstance.put(
          `/admin/projects/${this.project.id}/parameters`,
          {parameters: this.parameters}
        );

        // Save verbs
        await axiosInstance.put(
          `/admin/projects/${this.project.id}/verbs`,
          {
            verbs: this.isPlayground ? (this.verbsEnabled ? this.verbsConfig : null) : this.verbsConfig,
            sharedParameters: []
          }
        );

        // Save supported connections
        await axiosInstance.put(
          `/admin/projects/${this.project.id}/supported_connections`,
          {supported_connections: this.supportedConnections}
        );

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

    markUnsaved() {
      this.hasUnsavedChanges = true;
    },

    updateVerbs(updatedVerbs) {
      this.verbs = updatedVerbs;
      this.markUnsaved();
    },

    updateSharedParameters(updatedShared) {
      this.sharedParameters = updatedShared;
      this.markUnsaved();
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
      this.verbsConfig = this.isPlayground ? {
        parameter_name: 'verb',
        required: false,
        default: null,
        options: []
      } : null;
      this.verbsEnabled = false;
      this.sharedParameters = [];
      this.supportedConnections = [];
      this.selectedParamIndex = null;
      this.selectedVerbIndex = null;
      this.hasUnsavedChanges = false;
      this.error = null;
      this.success = null;
    },

    // Playground-specific methods for parameter editing
    selectParameter(index) {
      if (this.isPlayground) {
        this.selectedParamIndex = index;
      }
    },

    addParameter() {
      if (this.isPlayground) {
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
      }
    },

    deleteParameter(index) {
      if (this.isPlayground && confirm('Delete this parameter?')) {
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
      if (this.isPlayground) {
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
      }
    },

    formatDefault(param) {
      if (param.default === null || param.default === undefined) return '-';
      if (param.type === 'bool') return param.default ? 'true' : 'false';
      return String(param.default);
    },

    onTypeChange() {
      if (this.isPlayground && this.selectedParameter.type === 'list' && !this.selectedParameter.values) {
        this.selectedParameter.values = [];
      }
      this.markUnsaved();
    },

    getListValues() {
      if (this.isPlayground) {
        if (!this.selectedParameter.values) {
          this.selectedParameter.values = [];
        }
        return this.selectedParameter.values;
      }
      return [];
    },

    addListValue() {
      if (this.isPlayground) {
        if (!this.selectedParameter.values) {
          this.selectedParameter.values = [];
        }
        this.selectedParameter.values.push({ value: '', label: '' });
        this.markUnsaved();
      }
    },

    removeListValue(optionIndex) {
      if (this.isPlayground) {
        this.selectedParameter.values.splice(optionIndex, 1);
        this.markUnsaved();
      }
    },

    // Playground-specific methods for verb editing
    selectVerb(index) {
      if (this.isPlayground) {
        this.selectedVerbIndex = index;
      }
    },

    addVerb() {
      if (this.isPlayground) {
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
      }
    },

    deleteVerb(index) {
      if (this.isPlayground && confirm('Delete this verb?')) {
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
      if (this.isPlayground) {
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
      }
    },

    isParameterSelected(paramName) {
      return this.isPlayground && (this.selectedVerb?.parameters?.includes(paramName) || false);
    },

    toggleParameter(paramName, event) {
      if (this.isPlayground) {
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
      }
    },

    isParameterRequired(paramName) {
      return this.isPlayground && (this.selectedVerb?.required_parameters?.includes(paramName) || false);
    },

    toggleRequired(paramName, event) {
      if (this.isPlayground) {
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
      }
    },

    truncate(text, maxLength) {
      if (!text) return '-';
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
  }
};
</script>

<style scoped>
/* Standard mode styles (light theme) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-index-modal-overlay);
}

.modal-dialog {
  background: var(--background-color, #fff);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  /* Master-detail layout variables */
  --params-table-height: 200px;
  --verbs-table-height: 200px;
  --detail-panel-height: 448px;
  --master-detail-gap: 10px;

  /* Color variables for light theme (default) */
  --table-header-bg: #f5f5f5;
  --detail-panel-bg: #fafafa;
  --selected-row-bg: #e3f2fd;
  --hover-color: #fafafa;
  --border-color: #e0e0e0;
  --border-color-light: #f0f0f0;
  --text-primary: #424242;
  --text-secondary: #666;
  --input-bg: #ffffff;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-title .material-icons {
  font-size: 24px;
  color: var(--primary-color, #2196F3);
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background-color: var(--hover-color, #f5f5f5);
}

.modal-close .material-icons {
  font-size: 24px;
  color: var(--text-secondary, #666);
}

.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  background: var(--tabs-background, #f9f9f9);
  flex-shrink: 0;
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary, #666);
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  background-color: var(--hover-color, #f0f0f0);
  color: var(--text-primary, #333);
}

.tab-btn.active {
  color: var(--primary-color, #2196F3);
  border-bottom-color: var(--primary-color, #2196F3);
  background-color: var(--background-color, #fff);
}

.tab-btn .material-icons {
  font-size: 20px;
}

.modal-body {
  flex: 1 1 auto;
  overflow-y: auto !important;
  overflow-x: hidden;
  padding: 24px;
  min-height: 0;
  max-height: calc(90vh - 220px);
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
}

.tab-content {
  max-width: 100%;
  overflow: visible;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary, #666);
}

.loading-state .material-icons {
  font-size: 48px;
  margin-bottom: 16px;
  color: var(--primary-color, #2196F3);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-message {
  padding: 12px 16px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-message::before {
  content: 'error';
  font-family: 'Material Icons';
  font-size: 20px;
}

.success-message {
  padding: 12px 16px;
  background-color: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.success-message::before {
  content: 'check_circle';
  font-family: 'Material Icons';
  font-size: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color, #e0e0e0);
  background: var(--background-color, #fff);
  flex-shrink: 0;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--background-color, #fff);
  color: var(--text-primary, #333);
  border: 1px solid var(--border-color, #ddd);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--hover-color, #f5f5f5);
}

.btn-primary {
  background: var(--primary-color, #2196F3);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-dark, #1976D2);
}

.btn .material-icons {
  font-size: 18px;
}

/* Playground mode styles (dark theme) */
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

/* Master-Detail (Playground only) */
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

/* Detail Panel (Playground only) */
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

/* Forms (Playground) */
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
  width: 16px;
  height: 16px;
  margin: 0;
  cursor: pointer;
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

/* Parameter Selection Table (Playground) */
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

/* List Options (Playground) */
.list-option-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

/* Enable Section (Playground) */
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

/* Global Settings (Playground) */
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

/* Buttons (Playground) */
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

/* Connections Tab (Playground) */
.connections-section {
  padding: 24px;
}

.section-description {
  margin: 0 0 20px 0;
  color: #b0b0b0;
  font-size: 14px;
  line-height: 1.5;
}

.connections-table-container {
  max-height: 240px;
  overflow-y: auto;
  border: 1px solid #333;
  border-radius: 4px;
}

.connections-table {
  width: 100%;
  border-collapse: collapse;
  background: #252525;
}

.connections-table thead {
  position: sticky;
  top: 0;
  background: #1e1e1e;
  z-index: 1;
}

.connections-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #333;
}

.connections-table tbody tr {
  border-bottom: 1px solid #2a2a2a;
  transition: background-color 0.2s;
}

.connections-table tbody tr:hover {
  background: #2a2a2a;
}

.connections-table td {
  padding: 16px;
  font-size: 14px;
  color: #cccccc;
}

.connections-table .col-checkbox {
  width: 100px;
  text-align: center;
}

.connections-table .col-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.connections-table .col-name {
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 12px;
}

.connections-table .col-name .material-icons {
  font-size: 22px;
  color: #4a90e2;
  flex-shrink: 0;
}

.connections-table .col-name span {
  flex: 1;
}
</style>
