<template>
  <div class="theme-toggle">
    <button
        class="btn-icon-flat waves-effect waves-circle theme-button"
        :title="'Theme: ' + themeLabel + ' (click to change)'"
        @click="cycle">
      <i class="material-icons primary-color-text">{{ icon }}</i>
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

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
}

.theme-button {
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

.theme-button i {
  font-size: 22px;
}
</style>
