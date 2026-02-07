import historyModule from '@/common/store/executions-module';
import {isNull, logError} from '@/common/utils/common';
import get from 'lodash/get';
import Vue from 'vue'
import Vuex from 'vuex'
import authModule from '@/common/store/auth';
import scheduleModule from './scriptSchedule';
import allSchedulesModule from './allSchedules';
import pageModule from './page';
import settingsModule from './settings';
import {POLL_INTERVAL_MS} from '@/common/ui-constants';

import scriptConfigModule from './scriptConfig';
import scriptExecutionManagerModule from './scriptExecutionManager';
import scriptsModule from './scripts';
import scriptSetupModule from './scriptSetup';
import serverConfigModule from './serverConfig';
import {axiosInstance} from '@/common/utils/axios_utils';

// Admin store modules
import adminScriptsModule from '@/admin/store/scripts-module';
import adminScriptConfigModule from '@/admin/store/script-config-module';


Vue.use(Vuex);

const store = new Vuex.Store({
    modules: {
        scripts: scriptsModule,
        serverConfig: serverConfigModule,
        scriptConfig: scriptConfigModule(),
        scriptSetup: scriptSetupModule,
        executions: scriptExecutionManagerModule,
        auth: authModule,
        history: historyModule(),
        page: pageModule,
        scriptSchedule: scheduleModule,
        allSchedules: allSchedulesModule,
        settings: settingsModule,
        // Admin modules (namespaced for admin pages)
        adminScripts: adminScriptsModule,
        adminScriptConfig: adminScriptConfigModule
    },
    actions: {
        init({dispatch}) {
            dispatch('auth/init');
            dispatch('serverConfig/init');
            dispatch('scripts/init');
            dispatch('executions/init');
            dispatch('history/init');
            dispatch('allSchedules/fetchAllSchedules');

            // Start periodic polling for scheduled task updates
            // This catches executions started by the backend scheduler
            dispatch('startScheduledTaskPolling');
        },

        startScheduledTaskPolling({dispatch}) {
            // Poll every 5 seconds for updates from scheduled tasks
            // This catches executions started by the backend scheduler and keeps
            // schedule countdowns, last run times, and execution counts up to date
            setInterval(() => {
                // Always refresh both history and schedules
                // - History: catches new running tasks and completed tasks
                // - Schedules: updates next run countdown, last run time, execution count
                dispatch('history/refresh');
                dispatch('allSchedules/refresh');
            }, POLL_INTERVAL_MS);
        },

        resetScript({dispatch, state}) {
            const selectedScript = state.scripts.selectedScript

            dispatch('scriptSetup/reset');
            dispatch('scriptConfig/reloadScript', {selectedScript});
        },

        logout({dispatch}) {
            dispatch('executions/stopAll')
                .then(() => dispatch('auth/logout'))
                .then(() => location.reload())
                .catch(e => e && logError(e));
        }
    },
    mutations: {},

    strict: process.env.NODE_ENV !== 'production'
});

store.watch((state) => state.scripts.selectedScript, (selectedScript) => {
    store.dispatch('resetScript');
    store.dispatch('executions/selectScript', {selectedScript});
});

store.watch((state) => state.scripts.predefinedParameters, (predefinedParameters) => {
    if (!isNull(predefinedParameters)) {
        store.dispatch('scriptSetup/reloadModel', {
            values: predefinedParameters,
            forceAllowedValues: false,
            scriptName: store.state.scripts.selectedScript
        });
    }
});

store.watch((state) => state.scriptConfig.parameters, (parameters) => {
    const scriptConfig = store.state.scriptConfig.scriptConfig
    const scriptName = scriptConfig ? scriptConfig.name : null;
    store.dispatch('scriptSetup/initFromParameters', {scriptName, parameters, scriptConfig});
});

// Watch for executor changes (count and status) to refresh history and schedules lists
store.watch(
    (state) => {
        const executors = state.executions.executors;
        const ids = Object.keys(executors);
        const statuses = {};
        for (const id of ids) {
            if (executors[id] && executors[id].state) {
                statuses[id] = executors[id].state.status;
            }
        }
        // Include count to detect when executors are added
        return JSON.stringify({ count: ids.length, statuses });
    },
    () => {
        // Debounce the refresh to avoid multiple calls
        if (store._historyRefreshTimeout) {
            clearTimeout(store._historyRefreshTimeout);
        }
        store._historyRefreshTimeout = setTimeout(() => {
            store.dispatch('history/refresh');
            // Also refresh schedules - one-time schedules are removed after execution
            store.dispatch('allSchedules/refresh');
        }, 500);
    }
);

axiosInstance.interceptors.response.use((response) => response, (error) => {
    if (get(error, 'response.status') === 401) {
        store.dispatch('auth/setAuthenticated', false);
    }
    throw error;
});

window.addEventListener('beforeunload', function (e) {
    if (store.getters['executions/hasActiveExecutors']) {
        e = e || window.event;

        // in modern browsers the message will be replaced with default one (security reasons)
        var message = 'Closing the page will stop all running scripts. Are you sure?';
        e.returnValue = message;

        return message;
    }
});

export default store;