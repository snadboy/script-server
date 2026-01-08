<template>
  <button v-trim-text
       :class="{active: value}"
       class="toggle-day-button"
       type="button"
       :title="fullName"
       @click="$emit('input', !value)">
    <span class="day-abbr">{{ abbreviation }}</span>
    <span class="day-letter">{{ letter }}</span>
  </button>
</template>

<script>
export default {
  name: 'ToggleDayButton',
  props: {
    fullName: {
      type: String,
      required: true
    },
    value: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    abbreviation() {
      // Return first 3 letters (Mon, Tue, Wed, etc.)
      return this.fullName.substring(0, 3);
    },
    letter() {
      // Use unique letters for each day to avoid T/T and S/S confusion
      const dayLetters = {
        'Monday': 'M',
        'Tuesday': 'Tu',
        'Wednesday': 'W',
        'Thursday': 'Th',
        'Friday': 'F',
        'Saturday': 'Sa',
        'Sunday': 'Su'
      };
      return dayLetters[this.fullName] || this.fullName.charAt(0);
    }
  }
}
</script>

<style scoped>
.toggle-day-button {
  min-height: 44px;
  min-width: 44px;
  padding: 8px 12px;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  border: none;
  border-radius: 8px;
  background-color: var(--background-color-high-emphasis);

  cursor: pointer;
  text-transform: uppercase;

  font-size: 13px;
  font-weight: 500;
  color: var(--font-color-disabled);

  transition: background-color 0.2s ease, color 0.2s ease, transform 0.1s ease;
}

.toggle-day-button:hover {
  background-color: var(--hover-color);
  color: var(--font-color-medium);
}

.toggle-day-button:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.toggle-day-button:active {
  transform: scale(0.95);
}

.toggle-day-button.active {
  color: var(--font-on-primary-color-main);
  background-color: var(--primary-color);
}

.toggle-day-button.active:hover {
  background-color: var(--primary-color-dark);
}

/* Show abbreviation by default, hide letter */
.day-abbr {
  display: inline;
}

.day-letter {
  display: none;
}

/* On small screens, show 2-letter code instead */
@media (max-width: 400px) {
  .toggle-day-button {
    min-width: 36px;
    padding: 8px 6px;
  }

  .day-abbr {
    display: none;
  }

  .day-letter {
    display: inline;
  }
}
</style>