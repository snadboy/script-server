<template>
  <div class="source-selector">
    <div class="source-card" @click="$emit('select', 'import')" :class="{ selected: selected === 'import' }">
      <i class="material-icons">cloud_download</i>
      <h3>Import Python Project</h3>
      <p>Clone from Git, upload ZIP, or copy local project</p>
      <ul class="features">
        <li>Auto-detect dependencies</li>
        <li>Auto-detect entry points</li>
        <li>Generate wrapper script</li>
      </ul>
    </div>

    <div class="source-card" @click="$emit('select', 'manual')" :class="{ selected: selected === 'manual' }">
      <i class="material-icons">code</i>
      <h3>Manual Script</h3>
      <p>Configure any executable or shell script</p>
      <ul class="features">
        <li>Direct script path</li>
        <li>Custom parameters</li>
        <li>Full control</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SourceSelector',

  props: {
    selected: {
      type: String,
      default: null
    }
  },

  emits: ['select']
}
</script>

<style scoped>
.source-selector {
  display: flex;
  gap: 2rem;
  padding: 2rem;
  justify-content: center;
  align-items: stretch;
}

.source-card {
  flex: 1;
  max-width: 400px;
  padding: 2rem;
  border: 2px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 8px);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  background: var(--background-color, white);
}

.source-card:hover {
  border-color: var(--primary-color, #1976d2);
  box-shadow: var(--shadow, 0 4px 12px rgba(0, 0, 0, 0.1));
  transform: translateY(-2px);
}

.source-card.selected {
  border-color: var(--primary-color, #1976d2);
  background: var(--primary-color-light, rgba(25, 118, 210, 0.05));
}

.source-card i.material-icons {
  font-size: 64px;
  color: var(--primary-color, #1976d2);
  margin-bottom: 1rem;
}

.source-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 500;
}

.source-card p {
  margin: 0 0 1rem 0;
  color: var(--text-color-secondary, #666);
  font-size: 0.95rem;
}

.source-card .features {
  list-style: none;
  padding: 0;
  margin: 1rem 0 0 0;
  text-align: left;
}

.source-card .features li {
  padding: 0.25rem 0;
  color: var(--text-color-secondary, #666);
  font-size: 0.9rem;
}

.source-card .features li::before {
  content: '✓';
  color: var(--success-color, #4caf50);
  font-weight: bold;
  margin-right: 0.5rem;
}
</style>
