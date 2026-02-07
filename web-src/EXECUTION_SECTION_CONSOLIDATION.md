# Execution Section Consolidation Guide

## Summary
Created `ExecutionListSection.vue` to consolidate common patterns across RunningSection, ScheduledSection, and CompletedSection components.

## Current Duplication
- **RunningSection.vue** (128 lines)
- **ScheduledSection.vue** (182 lines)
- **CompletedSection.vue** (294 lines)
- **Total**: 604 lines

## Common Patterns (Duplicated ~70%)
1. CollapsibleSection wrapper
2. Loading state with spinner
3. Empty state handling
4. Filtered data display
5. Card rendering loop
6. Script filter logic
7. Badge count calculation
8. Collapse state management (via mixin)

## Created: ExecutionListSection.vue

Generic section component that:
- ✅ Handles loading/empty states
- ✅ Manages collapse state
- ✅ Provides item slot for custom rendering
- ✅ Supports optional actions slot
- ✅ Flexible key generation

## Refactoring Pattern

### Before (RunningSection.vue - 128 lines):
```vue
<template>
  <CollapsibleSection
    title="Running"
    :count="badgeCount"
    :isEmpty="!loading && filteredExecutions.length === 0"
    emptyMessage="No scripts currently running"
    :collapsed="collapsed"
    @toggle="handleToggle">
    <template v-if="loading">
      <div class="loading-state">
        <div class="spinner"></div>
      </div>
    </template>
    <template v-else>
      <ExecutionCard
        v-for="execution in filteredExecutions"
        :key="'running-' + execution.id"
        <!-- 15+ props -->
      />
    </template>
  </CollapsibleSection>
</template>

<script>
// 100+ lines of filtering, props, methods, state
</script>
```

### After (40-50 lines):
```vue
<template>
  <ExecutionListSection
    title="Running"
    :items="filteredExecutions"
    :loading="loading"
    :collapsed="collapsed"
    emptyMessage="No scripts currently running"
    keyPrefix="running"
    @toggle="handleToggle">
    <template #item="{ item }">
      <ExecutionCard
        :title="getExecutionTitle(item)"
        status="running"
        :user="item.user"
        <!-- other props -->
        @click="handleClick(item)">
        <template #actions>
          <StopButton :executionId="item.id" />
        </template>
      </ExecutionCard>
    </template>
  </ExecutionListSection>
</template>

<script>
// Only filtering logic and card props - ~40 lines
</script>
```

## Benefits

### 1. Code Reduction
- Eliminates ~400 lines of duplicate boilerplate
- Each section: 128/182/294 lines → ~40-60 lines
- Total savings: **~60% reduction**

### 2. Consistency
- All sections have identical structure
- Loading states look the same
- Empty states handled uniformly

### 3. Maintainability
- Fix bugs once in ExecutionListSection
- Add features (search, pagination) in one place
- Easier to test

### 4. Flexibility
- Item slot allows complete customization
- Actions slot for section-level actions
- Props for configuration

## Migration Steps

### 1. RunningSection.vue
```vue
<ExecutionListSection
  title="Running"
  :items="filteredExecutions"
  :loading="loading"
  :collapsed="collapsed"
  emptyMessage="No scripts currently running"
  keyPrefix="running"
  @toggle="handleToggle">
  <template #item="{ item: execution }">
    <ExecutionCard
      :title="getExecutionTitle(execution)"
      status="running"
      statusText="Running"
      :user="execution.user"
      :description="getScriptDesc(execution.script)"
      :instanceName="execution.instanceName"
      timeLabel="Started"
      :timeValue="execution.startTimeString"
      :isScheduled="!!execution.scheduleId"
      :scheduleDescription="getScheduleDesc(execution.scheduleId)"
      :parameters="showParameters ? getFilteredParameters(execution) : null"
      :verbParameterName="showParameters ? getVerbParameterName(execution.script) : null"
      @click="handleClick(execution)">
      <template #actions>
        <StopButton :executionId="execution.id" />
      </template>
    </ExecutionCard>
  </template>
</ExecutionListSection>
```

### 2. ScheduledSection.vue
```vue
<ExecutionListSection
  title="Scheduled"
  :items="filteredSchedules"
  :loading="loading"
  :collapsed="collapsed"
  :emptyMessage="emptyMessage"
  keyPrefix="schedule"
  @toggle="handleToggle">
  <template #item="{ item: schedule }">
    <ScheduleCard
      :schedule="schedule"
      :showScriptName="showScriptName"
      :showParams="showParams"
      :scriptDescription="getScriptDesc(schedule.script_name)"
      :paramsExpanded="expandedParams === schedule.id"
      :deleting="deleting === schedule.id"
      :toggling="toggling === schedule.id"
      @toggle-params="toggleParams(schedule.id)"
      @toggle-enabled="handleToggleEnabled(schedule)"
      @edit="handleEdit(schedule)"
      @delete="confirmDelete(schedule)"
    />
  </template>
</ExecutionListSection>
```

### 3. CompletedSection.vue
```vue
<ExecutionListSection
  title="Completed"
  :items="displayedExecutions"
  :loading="loading"
  :collapsed="collapsed"
  :emptyMessage="emptyMessage"
  keyPrefix="completed"
  sectionClass="completed-section"
  @toggle="handleToggle">
  <template #actions>
    <button v-if="filteredExecutions.length > 0 || deleting"
            class="delete-all-btn"
            :disabled="deleting"
            @click="confirmDeleteAll">
      <i class="material-icons">delete_sweep</i>
    </button>
  </template>

  <template #item="{ item: execution }">
    <ExecutionCard
      :title="execution.script + ' (Execution ID: ' + execution.id + ')'"
      :status="getStatus(execution)"
      :statusText="execution.fullStatus || execution.status"
      <!-- other props -->
      @click="handleClick(execution)">
      <template #actions>
        <button class="action-btn view-btn" @click="viewLog(execution)">
          <i class="material-icons">description</i>
        </button>
        <button class="action-btn delete-btn" @click="confirmDelete(execution)">
          <i class="material-icons">delete</i>
        </button>
      </template>
    </ExecutionCard>
  </template>
</ExecutionListSection>
```

## Component API

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| title | String | required | Section title |
| items | Array | required | Items to display |
| loading | Boolean | false | Show loading spinner |
| collapsed | Boolean | false | Section collapsed state |
| emptyMessage | String | 'No items' | Message when items empty |
| sectionClass | String/Object/Array | '' | Custom CSS class |
| keyPrefix | String | 'item' | Prefix for item keys |
| keyField | String | 'id' | Field to use for item key |

### Events

| Event | Payload | Description |
|-------|---------|-------------|
| toggle | none | Emitted when section toggled |

### Slots

| Slot | Props | Description |
|------|-------|-------------|
| item | { item } | Render individual item (required) |
| actions | none | Section-level actions (optional) |

## Estimated Savings

- RunningSection: 128 → 45 lines (**65% reduction**)
- ScheduledSection: 182 → 55 lines (**70% reduction**)
- CompletedSection: 294 → 65 lines (**78% reduction**)
- **Total: 604 → 165 lines (73% reduction)**
- **Lines saved: ~440 lines**

## Status

✅ ExecutionListSection.vue created
✅ Pattern documented
⏳ Sections to migrate: 3

Estimated time to complete migration: 30-45 minutes
