import {isEmptyString, isNull, logError} from '@/common/utils/common';
import {axiosInstance} from '@/common/utils/axios_utils';

const store = () => ({
    state: {
        executions: [],
        selectedExecution: null,
        selectedExecutionId: null,
        loading: false,
        detailsLoading: false
    },
    namespaced: true,
    actions: {
        init({commit}) {
            commit('SET_LOADING', true);
            commit('SET_EXECUTION_DETAILS', {execution: null, id: null});

            axiosInstance.get('history/execution_log/short').then(({data}) => {
                sortExecutionLogs(data);

                let executions = data.map(log => translateExecutionLog(log));
                commit('SET_EXECUTIONS', executions);
                commit('SET_LOADING', false);
            });
        },

        refresh({commit, state}) {
            // Silently refresh executions list without loading indicator
            // to avoid disrupting the UI (e.g., closing modals)
            axiosInstance.get('history/execution_log/short').then(({data}) => {
                sortExecutionLogs(data);

                let executions = data.map(log => translateExecutionLog(log));
                commit('SET_EXECUTIONS', executions);
            });
        },

        selectExecution({commit, state}, executionId) {
            if (isEmptyString(executionId)) {
                commit('SET_EXECUTION_DETAILS', {id: executionId, execution: null});
                commit('SET_DETAILS_LOADING', false);
                return;
            }

            let execution = findById(state.executions, executionId);
            if (isNull(execution)) {
                execution = {
                    id: executionId,
                    user: 'Unknown',
                    script: 'Unknown'
                };
            }
            commit('SET_EXECUTION_DETAILS', {id: executionId, execution});
            commit('SET_DETAILS_LOADING', true);

            axiosInstance.get('history/execution_log/long/' + executionId).then(({data: incomingLog}) => {
                if (executionId !== state.selectedExecutionId) {
                    return;
                }

                const executionLog = translateExecutionLog(incomingLog);

                commit('SET_EXECUTION_DETAILS', {id: executionId, execution: executionLog});
                commit('SET_DETAILS_LOADING', false);
            }).catch((error) => {
                logError(error);
            });
        }
    },
    mutations: {
        SET_LOADING(state, loading) {
            state.loading = loading;
        },

        SET_EXECUTIONS(state, executions) {
            state.executions = executions;
        },

        SET_EXECUTION_DETAILS(state, {execution, id}) {
            state.selectedExecution = execution;
            state.selectedExecutionId = id;
        },

        SET_DETAILS_LOADING(state, loading) {
            state.detailsLoading = loading;
        }
    }
});

export default store

function sortExecutionLogs(logs) {
    logs.sort(function (v1, v2) {
        if (isNull(v1.startTime)) {
            if (isNull(v2.startTime)) {
                return v1.user.localeCompare(v2.user);
            }
            return 1;
        } else if (isNull(v2.startTime)) {
            return -1;
        }

        let dateCompare = Date.parse(v2.startTime) - Date.parse(v1.startTime);
        if (dateCompare !== 0) {
            return dateCompare;
        }

        return v1.user.localeCompare(v2.user);
    });
}

export function translateExecutionLog(log) {
    log.startTimeString = formatDateCompact(log.startTime);
    log.finishTimeString = formatDateCompact(log.finishTime);
    log.durationString = formatDuration(log.startTime, log.finishTime);
    log.fullStatus = getFullStatus(log);

    return log;
}

function formatDateCompact(timeValue) {
    if (isNull(timeValue)) {
        return '';
    }
    const date = new Date(timeValue);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${month}/${day}/${year} @ ${hours}:${minutes}`;
}

function formatDuration(startTime, finishTime) {
    if (isNull(startTime) || isNull(finishTime)) {
        return '';
    }
    const start = new Date(startTime);
    const finish = new Date(finishTime);
    const durationMs = finish - start;

    if (durationMs < 0) return '';

    const totalSeconds = Math.floor(durationMs / 1000);
    const hours = Math.floor(totalSeconds / 3600).toString().padStart(2, '0');
    const minutes = Math.floor((totalSeconds % 3600) / 60).toString().padStart(2, '0');
    const seconds = (totalSeconds % 60).toString().padStart(2, '0');
    return `(${hours}:${minutes}:${seconds})`;
}

function getFullStatus(log) {
    if (!isNull(log.exitCode) && !isNull(log.status)) {
        return log.status + ' (' + log.exitCode + ')'
    } else if (!isNull(log.status)) {
        return log.status;
    }
}

function findById(executions, id) {
    return executions.find(execution => execution.id === id)
}
