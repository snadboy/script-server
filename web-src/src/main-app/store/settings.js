import axios from 'axios';
import {API} from '@/common/api-constants';

const STORAGE_KEY = 'scriptServer.settings';

const DEFAULT_SETTINGS = {
  completedExecutionsLimit: 50,
  logSizeLimit: 250
};

// Server-side settings (not stored in localStorage)
const DEFAULT_SERVER_SETTINGS = {
  onetimeRetentionMinutes: 60
};

function loadSettings() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return {...DEFAULT_SETTINGS, ...DEFAULT_SERVER_SETTINGS, ...JSON.parse(stored)};
    }
  } catch (e) {
    // Ignore localStorage errors
  }
  return {...DEFAULT_SETTINGS, ...DEFAULT_SERVER_SETTINGS};
}

function saveSettings(settings) {
  try {
    // Only save client-side settings to localStorage
    const clientSettings = {
      completedExecutionsLimit: settings.completedExecutionsLimit,
      logSizeLimit: settings.logSizeLimit
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(clientSettings));
  } catch (e) {
    // Ignore localStorage errors
  }
}

export default {
  namespaced: true,

  state: loadSettings(),

  mutations: {
    SET_SETTINGS(state, settings) {
      Object.assign(state, settings);
    },
    SET_RETENTION(state, minutes) {
      state.onetimeRetentionMinutes = minutes;
    }
  },

  actions: {
    updateSettings({commit, state}, settings) {
      commit('SET_SETTINGS', settings);
      saveSettings(state);
    },

    async fetchScheduleSettings({commit}) {
      try {
        const response = await axios.get(API.SCHEDULE_SETTINGS);
        commit('SET_RETENTION', response.data.onetime_retention_minutes);
      } catch (e) {
        // Silent failure - settings modal will use defaults if fetch fails
        console.error('Failed to fetch schedule settings:', e);
      }
    },

    async updateRetention({commit}, minutes) {
      try {
        const response = await axios.put(API.SCHEDULE_SETTINGS, {
          onetime_retention_minutes: minutes
        });
        commit('SET_RETENTION', response.data.onetime_retention_minutes);
        return true;
      } catch (e) {
        console.error('Failed to update retention setting:', e);
        throw e;
      }
    }
  }
};
