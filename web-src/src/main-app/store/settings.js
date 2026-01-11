const STORAGE_KEY = 'scriptServer.settings';

const DEFAULT_SETTINGS = {
  completedExecutionsLimit: 50
};

function loadSettings() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return {...DEFAULT_SETTINGS, ...JSON.parse(stored)};
    }
  } catch (e) {
    // Ignore localStorage errors
  }
  return {...DEFAULT_SETTINGS};
}

function saveSettings(settings) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
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
    }
  },

  actions: {
    updateSettings({commit, state}, settings) {
      commit('SET_SETTINGS', settings);
      saveSettings(state);
    }
  }
};
