import {UPLOAD_MODE} from '@/admin/components/scripts-config/script-edit/ScriptEditDialog'
import {axiosInstance} from '@/common/utils/axios_utils';
import {contains, forEachKeyValue, isEmptyArray, isEmptyValue} from '@/common/utils/common';
import clone from 'lodash/clone';

const allowedEmptyValuesInParam = ['name'];

function removeEmptyValues(config) {
    if (isEmptyArray(config.parameters)) {
        return;
    }

    for (const parameter of config.parameters) {
        let emptyValueKeys = [];
        forEachKeyValue(parameter, (key, value) => {
            if (contains(allowedEmptyValuesInParam, key)) {
                return;
            }

            if (isEmptyValue(value)) {
                emptyValueKeys.push(key);
            }
        });

        emptyValueKeys.forEach(key => delete parameter[key]);
    }
}

export const NEW_SCRIPT = '_new';

export default {
    state: {
        scriptName: null,
        scriptConfig: null,
        scriptFilename: null,
        error: null,
        new: false,
        originalConfigJson: null,
        isDirty: false
    },
    namespaced: true,
    actions: {
        init({commit, state}, scriptName) {
            if (scriptName === NEW_SCRIPT) {
                commit('INIT_NEW_SCRIPT');
                return;
            }

            commit('RESET', scriptName);

            axiosInstance.get('admin/scripts/' + encodeURIComponent(scriptName))
                .then(({data}) => {
                    commit('SET_SCRIPT_CONFIG', {config: data.config, filename: data.filename});
                })
                .catch((error) => {
                    commit('SET_LOAD_ERROR', 'Failed to load script config')
                });
        },

        save({dispatch, commit, state}) {
            const oldName = state.scriptName;
            const newName = state.scriptConfig.name;

            const formData = prepareConfigForSave(state.scriptConfig, state.scriptFilename)

            const axiosAction = state.new ? axiosInstance.post : axiosInstance.put;

            return axiosAction('admin/scripts', formData)
                .then(() => {
                    commit('MARK_CLEAN');
                    if (oldName === newName) {
                        dispatch('init', newName);
                        return {navigate: false};
                    } else {
                        // Return navigation info for component to handle
                        return {navigate: true, path: `/admin/scripts/${encodeURIComponent(newName)}`};
                    }
                })
                .catch(e => {
                    if ((e.response.status === 422) || (e.response.status === 403)) {
                        e.userMessage = e.response.data;
                    }
                    throw e;
                });
        },

        deleteScript({state}) {
            const oldName = state.scriptName;

            return axiosInstance.delete(`admin/scripts/${encodeURIComponent(oldName)}`)
                .then(() => {
                    // Return navigation info for component to handle
                    return {navigate: true, path: '/admin/scripts'};
                })
                .catch(e => {
                    if (e.response.status === 422) {
                        e.userMessage = e.response.data;
                    }
                    throw e;
              });
          },
    },
    mutations: {
        RESET(state, scriptName) {
            state.scriptName = scriptName;
            state.scriptConfig = null;
            state.scriptFilename = null;
            state.error = null;
            state.new = false;
        },

        SET_SCRIPT_CONFIG(state, {config, filename}) {
            state.error = null;
            state.scriptConfig = config;
            state.scriptFilename = filename;
            state.new = false;
            state.originalConfigJson = null;  // Will be captured after form initializes
            state.isDirty = false;
        },

        SET_LOAD_ERROR(state, error) {
            state.error = error;
            state.scriptConfig = null;
            state.scriptFilename = null;
        },

        INIT_NEW_SCRIPT(state) {
            state.scriptName = null;
            state.scriptConfig = {parameters: []};
            state.new = true;
            state.scriptFilename = null;
            state.error = null;
            state.originalConfigJson = null;  // Will be captured after form initializes
            state.isDirty = false;
        },

        CAPTURE_ORIGINAL(state) {
            state.originalConfigJson = JSON.stringify(state.scriptConfig);
            state.isDirty = false;
        },

        SET_DIRTY(state, isDirty) {
            state.isDirty = isDirty;
        },

        MARK_CLEAN(state) {
            state.originalConfigJson = JSON.stringify(state.scriptConfig);
            state.isDirty = false;
        }
    }
}

function prepareConfigForSave(scriptConfig, scriptFilename) {
    const config = clone(scriptConfig);

    removeEmptyValues(config);

    const formData = new FormData()
    if (config['script']['mode'] === UPLOAD_MODE) {
        const uploadFile = config['script']['uploadFile']
        formData.append('uploadedScript', uploadFile)
        delete config['script']['uploadFile']
    }

    formData.append('config', JSON.stringify(config))
    formData.append('filename', scriptFilename)

    return formData
}
