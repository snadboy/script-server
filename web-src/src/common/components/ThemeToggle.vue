<template>
  <div class="theme-toggle">
    <button
        class="btn-icon-flat waves-effect waves-circle theme-button"
        :title="'Theme: ' + themeLabel + ' (click to change)'"
        @click="cycle">
      <i class="material-icons">{{ icon }}</i>
    </button>
  </div>
</template>

<script>
import {
  getThemePreference,
  cycleTheme,
  getThemeIcon,
  getThemeLabel,
  initTheme
} from '@/common/utils/theme';

export default {
  name: 'ThemeToggle',

  data() {
    return {
      currentTheme: getThemePreference()
    };
  },

  computed: {
    icon() {
      return getThemeIcon(this.currentTheme);
    },
    themeLabel() {
      return getThemeLabel(this.currentTheme);
    }
  },

  mounted() {
    initTheme();
  },

  methods: {
    cycle() {
      this.currentTheme = cycleTheme();
    }
  }
};
</script>

<style>
.theme-toggle {
  display: inline-flex;
  align-items: center;
}

.theme-toggle .theme-button {
  width: 36px;
  height: 36px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: transparent;
  border: none;
  cursor: pointer;
}

.theme-toggle .theme-button i {
  font-size: 22px;
  color: var(--font-color-main);
}

/* On dark backgrounds (admin header, primary-color areas) */
.primary-color-dark .theme-toggle .theme-button i,
.primary-color .theme-toggle .theme-button i,
.page-title .theme-toggle .theme-button i {
  color: rgba(255, 255, 255, 0.87);
}
</style>
