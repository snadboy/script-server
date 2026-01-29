<template>
  <section class="collapsible-section" :class="{ collapsed: isCollapsed }">
    <h6 class="section-title">
      <div class="title-left" @click="toggle">
        <i class="material-icons expand-icon" :class="{ collapsed: isCollapsed }">expand_more</i>
        <slot name="title">{{ title }}</slot>
        <span v-if="count !== null && count !== undefined" class="badge">{{ count }}</span>
      </div>
      <div class="title-actions" @click.stop>
        <slot name="actions"></slot>
      </div>
    </h6>
    <div v-if="!isCollapsed" class="section-content">
      <div v-if="isEmpty" class="empty-state">
        <p>{{ emptyMessage }}</p>
      </div>
      <div v-else class="item-list">
        <slot></slot>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'CollapsibleSection',

  props: {
    title: {
      type: String,
      default: ''
    },
    count: {
      type: Number,
      default: null
    },
    collapsed: {
      type: Boolean,
      default: false
    },
    emptyMessage: {
      type: String,
      default: 'No items'
    },
    isEmpty: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      isCollapsed: this.collapsed
    };
  },

  watch: {
    collapsed(newVal) {
      this.isCollapsed = newVal;
    }
  },

  methods: {
    toggle() {
      this.isCollapsed = !this.isCollapsed;
      this.$emit('toggle', this.isCollapsed);
    }
  }
};
</script>

<style scoped>
.collapsible-section {
  display: flex;
  flex-direction: column;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 0 12px 0;
  padding: 0 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--font-color-main);
}

.title-left {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.title-left:hover {
  color: var(--primary-color);
}

.title-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title .expand-icon {
  font-size: 20px;
  color: var(--primary-color);
  transition: transform 0.2s ease;
}

.section-title .expand-icon.collapsed {
  transform: rotate(-90deg);
}

.section-title .badge {
  background: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.section-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.empty-state {
  padding: 16px;
  margin: 0 16px;
  text-align: center;
  color: var(--font-color-medium);
  background: var(--background-color-slight-emphasis);
  border-radius: var(--radius-md);
}

.empty-state p {
  margin: 0;
  font-size: 13px;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 16px;
}
</style>
