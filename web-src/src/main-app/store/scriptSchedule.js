import {axiosInstance} from '@/common/utils/axios_utils';
import clone from 'lodash/clone';
import {parametersToFormData} from '@/main-app/store/mainStoreHelper';

export default {
    state: {
        schedules: [],
        loading: false,
        error: null
    },
    namespaced: true,
    mutations: {
        SET_SCHEDULES(state, schedules) {
            state.schedules = schedules;
        },
        SET_LOADING(state, loading) {
            state.loading = loading;
        },
        SET_ERROR(state, error) {
            state.error = error;
        },
        REMOVE_SCHEDULE(state, scheduleId) {
            state.schedules = state.schedules.filter(s => s.id !== scheduleId);
        }
    },
    actions: {
        schedule({state, commit, dispatch, rootState}, {scheduleSetup}) {
            const parameterValues = clone(rootState.scriptSetup.parameterValues);
            const scriptName = rootState.scriptConfig.scriptConfig.name;

            const formData = parametersToFormData(parameterValues);
            formData.append('__script_name', scriptName);
            formData.append('__schedule_config', JSON.stringify(scheduleSetup))

            return axiosInstance.post('schedule', formData)
                .then(response => {
                    // Refresh schedules after creating a new one
                    dispatch('fetchSchedules', {scriptName});
                    // Also refresh allSchedules store for Activity page and other views
                    dispatch('allSchedules/refresh', null, {root: true});
                    return response;
                })
                .catch(e => {
                    if (e.response.status === 422) {
                        e.userMessage = e.response.data;
                    }
                    throw e;
                });
        },

        fetchSchedules({commit, rootState}, {scriptName} = {}) {
            commit('SET_LOADING', true);
            commit('SET_ERROR', null);

            const script = scriptName || (rootState.scriptConfig.scriptConfig && rootState.scriptConfig.scriptConfig.name);
            const url = script ? `schedules?script=${encodeURIComponent(script)}` : 'schedules';

            return axiosInstance.get(url)
                .then(response => {
                    commit('SET_SCHEDULES', response.data.schedules || []);
                    return response.data.schedules;
                })
                .catch(e => {
                    commit('SET_ERROR', e.message || 'Failed to fetch schedules');
                    throw e;
                })
                .finally(() => {
                    commit('SET_LOADING', false);
                });
        },

        deleteSchedule({commit, dispatch}, {scheduleId}) {
            return axiosInstance.delete(`schedules/${scheduleId}`)
                .then(response => {
                    commit('REMOVE_SCHEDULE', scheduleId);
                    // Also refresh allSchedules store for Activity page and other views
                    dispatch('allSchedules/refresh', null, {root: true});
                    return response.data;
                })
                .catch(e => {
                    if (e.response && e.response.status === 404) {
                        e.userMessage = 'Schedule not found';
                    } else if (e.response && e.response.status === 403) {
                        e.userMessage = 'Access denied';
                    }
                    throw e;
                });
        }
    },
    getters: {
        schedulesForScript: (state) => (scriptName) => {
            return state.schedules.filter(s => s.script_name === scriptName);
        }
    }
}
