<template>
  <div class="schedule-panel card">
    <div class="card-content">
      <span class="card-title primary-color-text">Scheduled Executions</span>
      <ScheduleList class="existing-schedules"/>
      <div class="schedule-divider"></div>
      <span class="card-subtitle">Create New Schedule</span>

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
        <DatePicker v-model="startDate" :show-header-in-modal="!mobileView" class="inline" label="Date"/>
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
                      :show-header-in-modal="!mobileView"
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
            <DatePicker v-model="endDate" :show-header-in-modal="!mobileView" class="inline repeat-start-date schedule-repeat_col-2" label="Date" />
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
                             :text="day.day.charAt(0)"
                             :title="day.day"/>
          </div>
          <div v-if="weekdaysError" class="weekdays-error">{{ weekdaysError }}</div>
        </div>
      </div>
    </div>
    <div v-if="errors.length > 0 || apiError" class="schedule-errors">
      <span v-for="(error, index) in errors" :key="'err-'+index" class="error-message">{{ error }}</span>
      <span v-if="apiError" class="error-message">{{ apiError }}</span>
    </div>
    <div class="schedule-panel-buttons card-action">
      <a class="waves-effect btn-flat" @click="close">
        Cancel
      </a>
      <PromisableButton :click="runScheduleAction"
                        :enabled="errors.length === 0"
                        :preloaderStyle="{ width: '20px', height: '20px' }"
                        title="Schedule"/>
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
import ScheduleList from "@/main-app/components/schedule/ScheduleList";
import {mapActions, mapState} from "vuex";
import '@/common/materializecss/imports/toast'
import {clearArray, isEmptyArray, isEmptyString} from "@/common/utils/common";

export default {
  name: 'SchedulePanel',
  components: {PromisableButton, ToggleDayButton, Combobox, Textfield, TimePicker, DatePicker, ScheduleList},
  props: {
    mobileView: {
      type: Boolean,
      default: false
    },
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
      apiError: null
    }
  },
  mounted: function () {
    this.id = this._uid;

    M.updateTextFields();
  },

  methods: {
    ...mapActions('scriptSchedule', ['schedule']),
    ...mapActions('scriptSetup', ['setParameterValue']),

    getParamValue(paramName) {
      return this.parameterValues ? this.parameterValues[paramName] : '';
    },

    setParamValue(paramName, value) {
      this.setParameterValue({ parameterName: paramName, value: value });
    },

    runScheduleAction() {
      this.apiError = null;
      const scheduleSetup = this.buildScheduleSetup();
      return this.schedule({scheduleSetup})
          .then(({data: response}) => {
            M.toast({html: 'Scheduled #' + response['id']});
            this.close();
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
        weekDays: weekDays
      };
    },

    close() {
      this.$emit('close');
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
      parameters: 'parameters'
    }),
    ...mapState('scriptSetup', {
      parameterValues: 'parameterValues'
    }),

    hasParameters() {
      return this.parameters && this.parameters.length > 0;
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

.schedule-panel {
  font-size: 16px;
  max-width: 400px;
  width: 100%;
  max-height: 600px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.existing-schedules {
  margin-bottom: 12px;
}

.schedule-divider {
  border-top: 1px solid var(--outline-color);
  margin: 12px 0;
}

.card-subtitle {
  font-size: 16px;
  font-weight: 500;
  color: var(--font-color-main);
  display: block;
  margin-bottom: 8px;
}

.schedule-panel .card-title {
  font-size: 20px;
}

.schedule-panel .card-content {
  padding-top: 12px;
  padding-bottom: 12px;
}

.schedule-panel .input-field.inline {
  margin-top: 8px;
  margin-bottom: 8px;
  vertical-align: baseline;
}

.schedule-panel .input-field.inline:after {
  top: 3.9em;
  left: 0;
  font-size: 12px;
  white-space: nowrap;
}

.schedule-panel .schedule-type-field {
  display: inline;
  margin-right: 32px;
}

.schedule-panel .schedule-type-field:last-child {
  margin-right: 0;
}

.schedule-panel .with-gap + span {
  font-size: 16px;
}

.schedule-panel .with-gap:checked + span {
  color: var(--font-color-main);
}

.toggle-day-button {
  display: inline-block;
  margin-right: 8px;
}

.toggle-day-button:last-child {
  margin-right: 0;
}

.schedule-panel input[type="radio"]:not(:checked) + span:before {
  border: 2px solid var(--font-color-medium);
}

.schedule-type-panel {
  margin-top: 16px;
  margin-bottom: 0;
  margin-left: -3px;
}

.one-time-schedule-panel {
  margin-top: 24px;
}

.one-time-schedule-panel .date-picker {
  width: 50%
}

.one-time-schedule-panel .time-picker {
  width: calc(45% - 32px)
}

.one-time-schedule-panel .time-picker {
  margin-left: 32px;
}

.repeat-schedule-panel {
  margin-top: 16px;
}

.repeat-schedule-panel span {
  display: inline-block;
}

.repeat-schedule-panel .schedule-repeat_col-12 {
  width: 65%;
  margin: 0 5% 0 0;
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

.schedule-panel-buttons.card-action {
  display: flex;
  justify-content: flex-end;
  padding: 8px;
}

.schedule-panel .schedule-panel-buttons.card-action a.btn-flat {
  margin-right: 8px;
}

.schedule-panel .repeat-weekday-panel {
  margin-bottom: 16px;
  padding-bottom: 8px;
  width: fit-content;
  height: 36px;
  box-sizing: border-box;
}

.schedule-panel .repeat-weekday-panel.error {
  border-bottom: 1px solid #F44336;
}

.repeat-weeks-panel {
  position: relative;
}

.schedule-panel .weekdays-error {
  color: #F44336;
  position: absolute;
  font-size: 12px;
  top: 40px;
  right: 32px;
}

@media (max-width: 320px) {
  .toggle-day-button {
    margin-right: 4px;
  }
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
  padding: 4px 8px;
  border: 1px solid var(--separator-color);
  border-radius: 4px;
  background-color: var(--background-color);
  color: var(--font-color-main);
  font-size: 13px;
  box-sizing: border-box;
}

.schedule-parameters-section .param-input:focus,
.schedule-parameters-section .param-select:focus {
  border-color: var(--primary-color);
  outline: none;
}

.schedule-parameters-section .param-value label {
  display: flex;
  align-items: center;
  height: 24px;
}

.schedule-errors {
  padding: 8px 16px;
  background-color: rgba(244, 67, 54, 0.1);
  border-left: 3px solid #F44336;
  margin: 8px 0;
}

.schedule-errors .error-message {
  display: block;
  color: #F44336;
  font-size: 14px;
}

@media (max-height: calc(600px)) {
  .schedule-panel {
    max-height: 340px;
  }

  .schedule-panel .input-field.inline {
    margin-top: 0;
    margin-bottom: 0;
  }
}
</style>