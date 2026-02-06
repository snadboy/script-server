<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content schedule-modal card">
      <div class="modal-header">
        <span class="modal-title">{{ isEditMode ? 'Edit Schedule' : 'Schedule Execution' }}</span>
        <span class="modal-subtitle">{{ scriptName }}</span>
      </div>

      <div class="modal-body">

        <div class="schedule-description-field input-field">
          <input type="text" v-model="description" id="schedule-description"
                 placeholder="Optional description for this schedule">
          <label for="schedule-description">Description</label>
        </div>

        <!-- Verb Selector -->
        <div v-if="hasVerbs" class="schedule-verb-section">
          <label class="section-label">Command</label>
          <select v-model="selectedVerb" class="verb-select">
            <option v-for="verb in verbOptions" :key="verb.name" :value="verb.name">
              {{ verb.label || verb.name }}
            </option>
          </select>
        </div>

        <!-- Connection Selection -->
        <div v-if="filteredConnections.length > 0" class="schedule-connections-section">
          <label class="section-label">Connections</label>
          <div class="connections-list">
            <label v-for="conn in filteredConnections" :key="conn.id" class="connection-checkbox">
              <input
                type="checkbox"
                :value="conn.id"
                v-model="selectedConnections"
                class="filled-in"
              />
              <span class="checkbox-custom"></span>
              <span>
                <i class="material-icons">{{ getConnectionIcon(conn.type) }}</i>
                {{ conn.name }}
                <span class="connection-type">({{ getConnectionTypeName(conn.type) }})</span>
              </span>
            </label>
          </div>
        </div>

        <div v-if="hasParameters" class="schedule-parameters-section">
          <span class="parameters-label">Parameters</span>
          <div class="params-table-wrapper">
            <table class="params-table">
              <thead>
                <tr>
                  <th>Parameter</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="param in parameters" :key="param.name">
                  <td class="param-name">{{ param.name }}</td>
                  <td class="param-value">
                    <input v-if="!param.withoutValue && param.type !== 'list' && param.type !== 'multiselect'"
                           type="text"
                           :value="getParamValue(param.name)"
                           @input="setParamValue(param.name, $event.target.value)"
                           class="param-input"/>
                    <label v-else-if="param.withoutValue">
                      <input type="checkbox"
                             :checked="getParamValue(param.name)"
                             @change="setParamValue(param.name, $event.target.checked)"
                             class="filled-in"/>
                      <span></span>
                    </label>
                    <select v-else-if="param.type === 'list'"
                            :value="getParamValue(param.name)"
                            @change="setParamValue(param.name, $event.target.value)"
                            class="param-select">
                      <option v-for="opt in param.values" :key="opt" :value="opt">{{ opt }}</option>
                    </select>
                    <span v-else class="param-display">{{ getParamValue(param.name) }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="schedule-type-panel">
          <p class="schedule-type-field">
            <label>
              <input :checked="oneTimeSchedule" class="with-gap" name="schedule-type"
                     type="radio"
                     @click="oneTimeSchedule = true"/>
              <span>One time</span>
            </label>
          </p>
          <p class="schedule-type-field">
            <label>
              <input :checked="!oneTimeSchedule" class="with-gap" name="schedule-type"
                     type="radio"
                     @click="oneTimeSchedule = false"/>
              <span>Repeat</span>
            </label>
          </p>
        </div>

        <div v-if="oneTimeSchedule" class="one-time-schedule-panel">
          <DatePicker v-model="startDate" :show-header-in-modal="true" class="inline" label="Date"/>
          <TimePicker v-model="startTime" class="inline" label="Time" @error="checkErrors"/>
        </div>

        <div v-else class="repeat-schedule-panel">
          <div>
            <span class="schedule-repeat_col-1">Every</span>
            <Textfield v-model="repeatPeriod" :config="repeatPeriodField"
                       class="inline repeat-period-field schedule-repeat_col-2" @error="checkErrors"/>
            <Combobox v-model="repeatTimeUnit" :config="repeatTimeUnitField"
                      :show-header="false" class="inline repeat-time-unit-field schedule-repeat_col-3"/>
          </div>
          <div>
            <span class="schedule-repeat_col-1">Starting</span>
            <DatePicker v-model="startDate"
                        :show-header-in-modal="true"
                        class="inline repeat-start-date schedule-repeat_col-2" label="Date"/>
            <TimePicker v-model="startTime" class="inline repeat-start-time schedule-repeat_col-3"
                        label="Time" @error="checkErrors"/>
          </div>

          <div>
            <span class="schedule-repeat_col-1">End:</span>
            <div class="schedule-type-panel">
              <p class="schedule-type-field">
                <label>
                  <input :checked="endOption === 'never'" class="with-gap" name="end-type" type="radio" @click="endOption = 'never'" />
                  <span>Never</span>
                </label>
              </p>
              <p class="schedule-type-field">
                <label>
                  <input :checked="endOption === 'maxExecuteCount'" class="with-gap" name="end-type" type="radio" @click="endOption = 'maxExecuteCount'" />
                  <span>Count</span>
                </label>
              </p>
              <p class="schedule-type-field">
                <label>
                  <input :checked="endOption === 'endDatetime'" class="with-gap" name="end-type" type="radio" @click="endOption = 'endDatetime'" />
                  <span>Date</span>
                </label>
              </p>
            </div>
            <br>
            <div v-if="endOption === 'endDatetime'">
              <span class="schedule-repeat_col-1">Ending</span>
              <DatePicker v-model="endDate" :show-header-in-modal="true" class="inline repeat-start-date schedule-repeat_col-2" label="Date" />
              <TimePicker v-model="endTime" class="inline repeat-start-time schedule-repeat_col-3" label="Time" @error="checkErrors" />
            </div>
            <div v-if="endOption === 'maxExecuteCount'">
              <span class="schedule-repeat_col-1">Count</span>
              <Textfield v-model="maxExecuteCount" :config="repeatPeriodField" class="inline repeat-period-field schedule-repeat_col-2" @error="checkErrors" />
            </div>

            <div v-if="repeatTimeUnit === 'weeks'" class="repeat-weeks-panel">
              <div :class="{ error: weekdaysError }" class="repeat-weekday-panel">
                <ToggleDayButton v-for="day in weekDays"
                                 :key="day.day"
                                 v-model="day.active"
                                 :full-name="day.day"/>
              </div>
              <div v-if="weekdaysError" class="weekdays-error">{{ weekdaysError }}</div>
            </div>
          </div>

        </div>

        <div class="enabled-toggle-row" :class="{ 'toggle-disabled': oneTimeSchedule }">
          <label class="enabled-toggle-label">
            <input type="checkbox" v-model="scheduleEnabled" class="filled-in" :disabled="oneTimeSchedule" />
            <span class="checkbox-custom"></span>
            <span>Enabled</span>
          </label>
          <span class="enabled-hint">{{ oneTimeSchedule ? 'Only applies to recurring schedules' : 'Disabled schedules won\'t run until enabled' }}</span>
        </div>

        <div v-if="errors.length > 0 || apiError" class="schedule-errors">
          <span v-for="(error, index) in errors" :key="'err-'+index" class="error-message">{{ error }}</span>
          <span v-if="apiError" class="error-message">{{ apiError }}</span>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-flat waves-effect" @click="close">Cancel</button>
        <PromisableButton :click="runScheduleAction"
                          :enabled="errors.length === 0"
                          :preloaderStyle="{ width: '20px', height: '20px' }"
                          :title="isEditMode ? 'Save' : 'Schedule'"/>
      </div>
    </div>
  </div>
</template>

<script>
import '@/common/materializecss/imports/datepicker'
import DatePicker from "@/common/components/inputs/DatePicker";
import TimePicker from "@/common/components/inputs/TimePicker";
import Textfield from "@/common/components/textfield";
import Combobox from "@/common/components/combobox";
import '@/common/materializecss/imports/cards';
import {repeatPeriodField, repeatTimeUnitField} from "@/main-app/components/schedule/schedulePanelFields";
import ToggleDayButton from "@/main-app/components/schedule/ToggleDayButton";
import PromisableButton from "@/common/components/PromisableButton";
import {mapActions, mapState} from "vuex";
import '@/common/materializecss/imports/toast'
import {clearArray, isEmptyArray, isEmptyString} from "@/common/utils/common";

export default {
  name: 'ScheduleModal',
  components: {PromisableButton, ToggleDayButton, Combobox, Textfield, TimePicker, DatePicker},

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    scriptName: {
      type: String,
      default: ''
    },
    editSchedule: {
      type: Object,
      default: null
    }
  },

  data() {
    const now = new Date();
    const currentDay = now.getDay();

    const endDay = new Date(now);
    endDay.setDate(now.getDate() + 1);

    return {
      oneTimeSchedule: true,
      startDate: now,
      startTime: now.toTimeString().substr(0, 5),
      endOption: 'never',
      endDate: endDay,
      endTime: endDay.toTimeString().substr(0, 5),
      id: null,
      repeatPeriod: 1,
      maxExecuteCount: 1,
      repeatTimeUnit: 'days',
      weekDays: [
        {'day': 'Monday', active: currentDay === 1},
        {'day': 'Tuesday', active: currentDay === 2},
        {'day': 'Wednesday', active: currentDay === 3},
        {'day': 'Thursday', active: currentDay === 4},
        {'day': 'Friday', active: currentDay === 5},
        {'day': 'Saturday', active: currentDay === 6},
        {'day': 'Sunday', active: currentDay === 0}
      ],

      repeatPeriodField,
      repeatTimeUnitField,
      errors: [],
      apiError: null,
      boundFixOverlayDimensions: null,
      originalParent: null,
      description: '',
      scheduleEnabled: true,
      // Execution configuration
      selectedVerb: null,
      selectedConnections: [],
      availableConnections: [],
      connectionTypes: []
    }
  },

  mounted: function () {
    this.id = this._uid;
  },

  methods: {
    ...mapActions('scriptSchedule', ['schedule']),
    ...mapActions('scriptSetup', ['setParameterValue']),
    ...mapActions('allSchedules', ['updateSchedule']),

    fixOverlayDimensions() {
      // Fix for display scaling causing 100vh to be larger than viewport
      const overlay = this.$el;
      if (overlay && overlay.classList.contains('modal-overlay')) {
        overlay.style.height = window.innerHeight + 'px';
        overlay.style.width = window.innerWidth + 'px';
      }
    },

    getParamValue(paramName) {
      return this.parameterValues ? this.parameterValues[paramName] : '';
    },

    setParamValue(paramName, value) {
      this.setParameterValue({ parameterName: paramName, value: value });
    },

    async loadConnections() {
      try {
        const axiosInstance = (await import('@/common/utils/axios_utils')).axiosInstance;

        // Load connection types
        const typesResp = await axiosInstance.get('/admin/connections/types');
        this.connectionTypes = typesResp.data.types || [];

        // Load available connections
        const connsResp = await axiosInstance.get('/admin/connections');
        this.availableConnections = connsResp.data.connections || [];
      } catch (error) {
        console.error('Failed to load connections:', error);
        this.availableConnections = [];
        this.connectionTypes = [];
      }
    },

    getConnectionIcon(typeId) {
      const type = this.connectionTypes.find(t => t.type_id === typeId);
      return type ? type.icon : 'vpn_key';
    },

    getConnectionTypeName(typeId) {
      const type = this.connectionTypes.find(t => t.type_id === typeId);
      return type ? type.display_name : typeId;
    },

    runScheduleAction() {
      this.apiError = null;
      const scheduleSetup = this.buildScheduleSetup();

      if (this.isEditMode) {
        // Update existing schedule
        return this.updateSchedule({
          scheduleId: this.editSchedule.id,
          scheduleConfig: scheduleSetup
        })
            .then((response) => {
              M.toast({html: 'Schedule updated'});
              this.close();
            })
            .catch((e) => {
              if (e.response && e.response.data) {
                this.apiError = e.response.data;
              } else if (e.userMessage) {
                this.apiError = e.userMessage;
              } else {
                this.apiError = 'Failed to update schedule';
              }
              throw e;
            });
      } else {
        // Create new schedule
        return this.schedule({scheduleSetup})
            .then(({data: response}) => {
              M.toast({html: 'Scheduled #' + response['id']});
              // Reset form to allow creating another schedule
              this.resetScheduleFields();
            })
            .catch((e) => {
              if (e.response && e.response.data) {
                this.apiError = e.response.data;
              } else if (e.userMessage) {
                this.apiError = e.userMessage;
              } else {
                this.apiError = 'Failed to schedule';
              }
              throw e;
            });
      }
    },

    resetScheduleFields() {
      // Reset only schedule-specific fields, keeping the modal open
      const now = new Date();
      const currentDay = now.getDay();
      const endDay = new Date(now);
      endDay.setDate(now.getDate() + 1);

      this.oneTimeSchedule = true;
      this.startDate = now;
      this.startTime = now.toTimeString().substr(0, 5);
      this.endOption = 'never';
      this.endDate = endDay;
      this.endTime = endDay.toTimeString().substr(0, 5);
      this.repeatPeriod = 1;
      this.maxExecuteCount = 1;
      this.repeatTimeUnit = 'days';
      this.weekDays = [
        {'day': 'Monday', active: currentDay === 1},
        {'day': 'Tuesday', active: currentDay === 2},
        {'day': 'Wednesday', active: currentDay === 3},
        {'day': 'Thursday', active: currentDay === 4},
        {'day': 'Friday', active: currentDay === 5},
        {'day': 'Saturday', active: currentDay === 6},
        {'day': 'Sunday', active: currentDay === 0}
      ];
      this.description = '';
      this.scheduleEnabled = true;
      this.errors = [];
      this.apiError = null;
      this.$nextTick(() => M.updateTextFields());
    },

    buildScheduleSetup() {
      const startDatetime = new Date(this.startDate);
      const [hours, minutes] = this.startTime.split(':');
      startDatetime.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      let endOption = this.endOption;
      let endArg = null;

      if (this.endOption === 'maxExecuteCount') {
        endArg = this.maxExecuteCount;
        endOption = 'max_executions';
      } else if (this.endOption === 'endDatetime') {
        const endDatetime = new Date(this.endDate);
        const [hoursEnd, minutesEnd] = this.endTime.split(':');
        endDatetime.setHours(parseInt(hoursEnd), parseInt(minutesEnd), 0, 0);
        endArg = endDatetime;
        endOption = 'end_datetime';
      }

      const weekDays = this.weekDays.filter(day => day.active).map(day => day.day);

      return {
        repeatable: !this.oneTimeSchedule,
        startDatetime: startDatetime,
        endOption: endOption,
        endArg: endArg,
        repeatUnit: this.repeatTimeUnit,
        repeatPeriod: this.repeatPeriod,
        weekDays: weekDays,
        description: this.description,
        enabled: this.oneTimeSchedule ? true : this.scheduleEnabled,
        // Execution configuration
        verb: this.selectedVerb || null,
        connectionIds: this.selectedConnections || []
      };
    },

    close() {
      this.$emit('close');
    },

    async resetForm() {
      // Load connections first
      await this.loadConnections();

      if (this.editSchedule) {
        // Edit mode - populate form with existing schedule data
        this.populateFromSchedule(this.editSchedule);
      } else {
        // Create mode - reset to defaults
        const now = new Date();
        const currentDay = now.getDay();
        const endDay = new Date(now);
        endDay.setDate(now.getDate() + 1);

        this.oneTimeSchedule = true;
        this.startDate = now;
        this.startTime = now.toTimeString().substr(0, 5);
        this.endOption = 'never';
        this.endDate = endDay;
        this.endTime = endDay.toTimeString().substr(0, 5);
        this.repeatPeriod = 1;
        this.maxExecuteCount = 1;
        this.repeatTimeUnit = 'days';
        this.weekDays = [
          {'day': 'Monday', active: currentDay === 1},
          {'day': 'Tuesday', active: currentDay === 2},
          {'day': 'Wednesday', active: currentDay === 3},
          {'day': 'Thursday', active: currentDay === 4},
          {'day': 'Friday', active: currentDay === 5},
          {'day': 'Saturday', active: currentDay === 6},
          {'day': 'Sunday', active: currentDay === 0}
        ];
        this.description = '';
        this.scheduleEnabled = true;

        // Initialize verb from instance defaults
        if (this.hasVerbs) {
          this.selectedVerb = this.scriptConfig?.defaultVerb || this.verbsConfig?.default || this.verbOptions[0]?.name;
        }

        // Initialize connections from instance defaults
        this.selectedConnections = this.scriptConfig?.defaultConnections || [];
      }
      this.errors = [];
      this.apiError = null;
    },

    populateFromSchedule(schedule) {
      const sched = schedule.schedule;

      this.oneTimeSchedule = !sched.repeatable;
      this.description = schedule.description || '';
      this.scheduleEnabled = schedule.enabled !== false;

      // Parse start datetime
      const startDatetime = new Date(sched.start_datetime);
      this.startDate = startDatetime;
      this.startTime = startDatetime.toTimeString().substr(0, 5);

      // Repeat settings
      if (sched.repeatable) {
        this.repeatPeriod = sched.repeat_period || 1;
        this.repeatTimeUnit = sched.repeat_unit || 'days';

        // End option
        if (sched.end_option === 'max_executions') {
          this.endOption = 'maxExecuteCount';
          this.maxExecuteCount = sched.end_arg || 1;
        } else if (sched.end_option === 'end_datetime') {
          this.endOption = 'endDatetime';
          const endDatetime = new Date(sched.end_arg);
          this.endDate = endDatetime;
          this.endTime = endDatetime.toTimeString().substr(0, 5);
        } else {
          this.endOption = 'never';
        }

        // Weekdays (for weekly schedules)
        if (sched.weekdays && sched.weekdays.length > 0) {
          this.weekDays = [
            {'day': 'Monday', active: sched.weekdays.includes('Monday')},
            {'day': 'Tuesday', active: sched.weekdays.includes('Tuesday')},
            {'day': 'Wednesday', active: sched.weekdays.includes('Wednesday')},
            {'day': 'Thursday', active: sched.weekdays.includes('Thursday')},
            {'day': 'Friday', active: sched.weekdays.includes('Friday')},
            {'day': 'Saturday', active: sched.weekdays.includes('Saturday')},
            {'day': 'Sunday', active: sched.weekdays.includes('Sunday')}
          ];
        } else {
          const currentDay = new Date().getDay();
          this.weekDays = [
            {'day': 'Monday', active: currentDay === 1},
            {'day': 'Tuesday', active: currentDay === 2},
            {'day': 'Wednesday', active: currentDay === 3},
            {'day': 'Thursday', active: currentDay === 4},
            {'day': 'Friday', active: currentDay === 5},
            {'day': 'Saturday', active: currentDay === 6},
            {'day': 'Sunday', active: currentDay === 0}
          ];
        }
      }

      // Load execution configuration (verb and connections)
      this.selectedVerb = sched.verb || this.scriptConfig?.defaultVerb || null;
      this.selectedConnections = sched.connectionIds || this.scriptConfig?.defaultConnections || [];
    },

    checkErrors() {
      clearArray(this.errors);

      for (const child of this.$children) {
        if ((child.$options._componentTag === TimePicker.name)
            || (child.$options._componentTag === Textfield.name)) {
          if (!isEmptyString(child.error)) {
            this.errors.push(child.error);
          }
        }
      }

      if (!isEmptyString(this.weekdaysError)) {
        this.errors.push(this.weekdaysError);
      }
    }
  },

  computed: {
    ...mapState('scriptConfig', {
      parameters: 'parameters',
      scriptConfig: 'scriptConfig'
    }),
    ...mapState('scriptSetup', {
      parameterValues: 'parameterValues'
    }),

    hasParameters() {
      return this.parameters && this.parameters.length > 0;
    },

    verbsConfig() {
      return this.scriptConfig?.verbs || null;
    },

    hasVerbs() {
      return this.verbsConfig && this.verbsConfig.options && this.verbsConfig.options.length > 0;
    },

    verbOptions() {
      if (!this.verbsConfig) return [];
      return this.verbsConfig.options || [];
    },

    supportedConnectionTypes() {
      return this.scriptConfig?.supportedConnections || [];
    },

    filteredConnections() {
      if (this.supportedConnectionTypes.length > 0) {
        return this.availableConnections.filter(conn =>
          this.supportedConnectionTypes.includes(conn.type)
        );
      }
      return this.availableConnections;
    },

    isEditMode() {
      return this.editSchedule !== null;
    },

    weekdaysError() {
      if (this.oneTimeSchedule || this.repeatTimeUnit !== 'weeks') {
        return null;
      }

      const activeWeekDays = this.weekDays.filter(day => day.active);
      if (isEmptyArray(activeWeekDays)) {
        return 'required';
      }

      return null;
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden';
        this.resetForm();
        // Move modal to body to avoid transform containment issues from parent elements
        this.$nextTick(() => {
          this.originalParent = this.$el.parentElement;
          document.body.appendChild(this.$el);
          this.boundFixOverlayDimensions = this.fixOverlayDimensions.bind(this);
          this.boundFixOverlayDimensions();
          window.addEventListener('resize', this.boundFixOverlayDimensions);
          M.updateTextFields();
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
    },

    weekdaysError() {
      this.$nextTick(this.checkErrors);
    },

    oneTimeSchedule() {
      this.$nextTick(this.checkErrors);
    }
  }
}
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
  z-index: 1000;
}

.schedule-modal {
  width: 85%;
  max-width: 500px;
  height: auto;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-md);
  margin: 0 !important;
  position: relative;
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

.modal-subtitle {
  font-size: 0.9em;
  color: var(--font-color-medium);
  margin-top: 4px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
}

.schedule-description-field {
  margin-top: 12px;
  margin-bottom: 16px;
}

.schedule-description-field input {
  border-bottom: 1px solid var(--separator-color) !important;
}

.schedule-description-field input:focus {
  border-bottom: 1px solid var(--primary-color) !important;
  box-shadow: 0 1px 0 0 var(--primary-color) !important;
}

.modal-body .input-field.inline {
  margin-top: 8px;
  margin-bottom: 8px;
  vertical-align: baseline;
}

.modal-body .input-field.inline:after {
  top: 3.9em;
  left: 0;
  font-size: 12px;
  white-space: nowrap;
}

.schedule-type-panel {
  margin-top: 16px;
  margin-bottom: 0;
  margin-left: -3px;
}

.schedule-type-field {
  display: inline;
  margin-right: 32px;
}

.schedule-type-field:last-child {
  margin-right: 0;
}

.with-gap + span {
  font-size: 16px;
}

.with-gap:checked + span {
  color: var(--font-color-main);
}

input[type="radio"]:not(:checked) + span:before {
  border: 2px solid var(--font-color-medium);
}

.one-time-schedule-panel {
  margin-top: 24px;
}

.one-time-schedule-panel .date-picker {
  width: 50%
}

.one-time-schedule-panel .time-picker {
  width: calc(45% - 32px);
  margin-left: 32px;
}

.repeat-schedule-panel {
  margin-top: 16px;
}

.repeat-schedule-panel span {
  display: inline-block;
}

.repeat-schedule-panel .schedule-repeat_col-1 {
  width: 20%;
  margin: 0;
}

.repeat-schedule-panel .schedule-repeat_col-2 {
  width: 35%;
  margin-left: 10%;
  margin-right: 5%;
}

.repeat-schedule-panel .schedule-repeat_col-3 {
  width: 30%;
  margin: 0;
}

.repeat-weekday-panel {
  margin-bottom: 16px;
  padding: 8px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  box-sizing: border-box;
}

.repeat-weekday-panel.error {
  border-bottom: 2px solid #F44336;
  padding-bottom: 6px;
}

.repeat-weekday-panel >>> .toggle-day-button {
  margin-right: 4px;
  margin-bottom: 4px;
}

.repeat-weekday-panel >>> .toggle-day-button:last-child {
  margin-right: 0;
}

.repeat-weeks-panel {
  position: relative;
}

.weekdays-error {
  color: #F44336;
  position: absolute;
  font-size: 12px;
  top: 40px;
  right: 32px;
}

.schedule-parameters-section {
  margin: 16px 0;
  padding: 12px;
  background-color: var(--background-color-high-emphasis);
  border-radius: 4px;
}

.schedule-parameters-section .parameters-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--font-color-medium);
  display: block;
  margin-bottom: 8px;
}

.schedule-parameters-section .params-table-wrapper {
  max-height: 200px;
  overflow-y: auto;
}

.schedule-parameters-section .params-table {
  width: 100%;
  font-size: 13px;
  border-collapse: collapse;
}

.schedule-parameters-section .params-table th,
.schedule-parameters-section .params-table td {
  text-align: left;
  padding: 6px 8px;
  vertical-align: middle;
}

.schedule-parameters-section .params-table th {
  color: var(--font-color-medium);
  font-weight: 500;
  border-bottom: 1px solid var(--separator-color);
  position: sticky;
  top: 0;
  background-color: var(--background-color-high-emphasis);
}

.schedule-parameters-section .params-table .param-name {
  font-weight: 500;
  color: var(--font-color-main);
  white-space: nowrap;
  width: 40%;
}

.schedule-parameters-section .params-table .param-value {
  width: 60%;
}

.schedule-parameters-section .param-input,
.schedule-parameters-section .param-select {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  background-color: var(--background-color-level-4dp);
  color: var(--font-color-main);
  font-size: 13px;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.schedule-parameters-section .param-input:focus,
.schedule-parameters-section .param-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(38, 166, 154, 0.2);
  outline: none;
}

.schedule-parameters-section .param-value label {
  display: flex;
  align-items: center;
  height: 24px;
}

.schedule-errors {
  padding: 8px 16px;
  background-color: var(--status-error-bg);
  border-left: 3px solid var(--status-error-color);
  margin: 8px 0;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.schedule-errors .error-message {
  display: block;
  color: var(--status-error-color);
  font-size: 14px;
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

@media screen and (max-width: 768px) {
  .schedule-modal {
    width: 95%;
    max-height: 95vh;
  }

  .modal-body {
    padding: 16px;
  }
}

@media (max-width: 320px) {
  .repeat-weekday-panel {
    gap: 2px;
  }
}

.enabled-toggle-row {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--separator-color);
}

.enabled-toggle-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.enabled-toggle-label span {
  font-size: 14px;
  color: var(--font-color-main);
}

.enabled-hint {
  display: block;
  font-size: 12px;
  color: var(--font-color-medium);
  margin-top: 4px;
  margin-left: 30px;
}

.toggle-disabled {
  opacity: 0.5;
}

.toggle-disabled .enabled-toggle-label {
  cursor: not-allowed;
}

.toggle-disabled input[type="checkbox"]:disabled + span {
  color: var(--font-color-medium);
}

/* Verb and Connection Sections */
.schedule-verb-section,
.schedule-connections-section {
  margin-bottom: 20px;
}

.section-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--font-color-main);
  margin-bottom: 8px;
}

.verb-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--background-color);
  color: var(--font-color-main);
  font-size: 14px;
}

.connections-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.connection-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.connection-checkbox:hover {
  background-color: var(--background-color-medium-emphasis);
}

.connection-checkbox .material-icons {
  font-size: 18px;
  color: var(--primary-color);
}

.connection-type {
  color: var(--font-color-medium);
  font-size: 12px;
  margin-left: 4px;
}
</style>
