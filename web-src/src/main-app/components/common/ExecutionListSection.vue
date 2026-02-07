<template>
  <CollapsibleSection
    :title="title"
    :count="items.length"
    :isEmpty="!loading && items.length === 0"
    :emptyMessage="emptyMessage"
    :collapsed="collapsed"
    @toggle="$emit('toggle')"
    :class="sectionClass">
    <!-- Optional actions slot (e.g., delete all button) -->
    <template v-if="$slots.actions" #actions>
      <slot name="actions"></slot>
    </template>

    <!-- Loading state -->
    <template v-if="loading">
      <div class="loading-state">
        <div class="spinner"></div>
      </div>
    </template>

    <!-- Items list -->
    <template v-else>
      <slot name="item" v-for="item in items" :item="item" :key="getItemKey(item)"></slot>
    </template>
  </CollapsibleSection>
</template>

<script>
import CollapsibleSection from './CollapsibleSection';

export default {
  name: 'ExecutionListSection',

  components: {
    CollapsibleSection
  },

  props: {
    // Section configuration
    title: {
      type: String,
      required: true
    },
    items: {
      type: Array,
      required: true,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    collapsed: {
      type: Boolean,
      default: false
    },
    emptyMessage: {
      type: String,
      default: 'No items'
    },
    sectionClass: {
      type: [String, Object, Array],
      default: ''
    },
    // Key generation
    keyPrefix: {
      type: String,
      default: 'item'
    },
    keyField: {
      type: String,
      default: 'id'
    }
  },

  methods: {
    getItemKey(item) {
      return `${this.keyPrefix}-${item[this.keyField]}`;
    }
  }
};
</script>

<style scoped src="@/main-app/styles/executionSection.css"></style>

<style scoped>
.loading-state {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--separator-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
