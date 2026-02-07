import {axiosInstance} from '@/common/utils/axios_utils';
import {API} from '@/common/api-constants';

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
        },
        UPDATE_SCHEDULE_ENABLED(state, {scheduleId, enabled, nextExecution}) {
            const schedule = state.schedules.find(s => String(s.id) === String(scheduleId));
            if (schedule) {
                schedule.enabled = enabled;
                if (nextExecution) {
                    schedule.next_execution = nextExecution;
                }
            }
        }
    },
    actions: {
        fetchAllSchedules({commit}) {
            commit('SET_LOADING', true);
            commit('SET_ERROR', null);

            // Fetch all schedules (no script filter)
            return axiosInstance.get(API.SCHEDULES)
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

        refresh({commit}) {
            // Silently refresh schedules list without loading indicator
            // to avoid disrupting the UI (e.g., closing modals)
            return axiosInstance.get(API.SCHEDULES)
                .then(response => {
                    commit('SET_SCHEDULES', response.data.schedules || []);
                    return response.data.schedules;
                })
                .catch(e => {
                    // Silent refresh - don't update error state
                    console.error('Failed to refresh schedules:', e);
                });
        },

        deleteSchedule({commit, dispatch, rootState}, {scheduleId}) {
            return axiosInstance.delete(`${API.SCHEDULES}/${scheduleId}`)
                .then(response => {
                    commit('REMOVE_SCHEDULE', scheduleId);
                    // Also refresh scriptSchedule store for the current script view
                    const scriptName = rootState.scriptConfig.scriptConfig && rootState.scriptConfig.scriptConfig.name;
                    if (scriptName) {
                        dispatch('scriptSchedule/fetchSchedules', {scriptName}, {root: true});
                    }
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
        },

        toggleScheduleEnabled({commit}, {scheduleId, enabled}) {
            return axiosInstance.post(`${API.SCHEDULES}/${scheduleId}/enabled`, {enabled})
                .then(response => {
                    commit('UPDATE_SCHEDULE_ENABLED', {
                        scheduleId,
                        enabled: response.data.enabled,
                        nextExecution: response.data.next_execution
                    });
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
        },

        updateSchedule({dispatch}, {scheduleId, scheduleConfig}) {
            return axiosInstance.put(`${API.SCHEDULES}/${scheduleId}`, {schedule_config: scheduleConfig})
                .then(response => {
                    // Refresh the full schedules list to get updated data
                    dispatch('refresh');
                    return response.data;
                })
                .catch(e => {
                    if (e.response && e.response.status === 404) {
                        e.userMessage = 'Schedule not found';
                    } else if (e.response && e.response.status === 422) {
                        e.userMessage = e.response.data || 'Invalid schedule configuration';
                    } else if (e.response && e.response.status === 403) {
                        e.userMessage = 'Access denied';
                    }
                    throw e;
                });
        }
    }
}
