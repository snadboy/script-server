import {axiosInstance} from '@/common/utils/axios_utils';

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
        fetchAllSchedules({commit}) {
            commit('SET_LOADING', true);
            commit('SET_ERROR', null);

            // Fetch all schedules (no script filter)
            return axiosInstance.get('schedules')
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
            return axiosInstance.get('schedules')
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
            return axiosInstance.delete(`schedules/${scheduleId}`)
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
        }
    }
}
