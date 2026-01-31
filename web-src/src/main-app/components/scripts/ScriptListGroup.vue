<template>
  <div :class="{active:group.isActive}" class="script-list-group">
    <a :key="group.name"
       class="collection-item waves-effect script-group"
       :title="groupValidationTooltip"
       @click="$emit('group-clicked', group.name)">
      <span>{{ group.name }}</span>
      <i v-if="hasInvalidScripts" class="material-icons group-warning-icon">warning</i>
      <i class="material-icons">
        {{ group.isActive ? 'expand_less' : 'expand_more' }}
      </i>
    </a>

    <ScriptListItem v-for="innerScript in group.scripts"
                    v-if="group.isActive" :key="innerScript.name"
                    :script="innerScript"/>
  </div>
</template>

<script>
import ScriptListItem from './ScriptListItem';

export default {
  name: 'ScriptListGroup',
  components: {ScriptListItem},
  props: {
    group: {
      type: Object
    }
  },
  computed: {
    hasInvalidScripts() {
      if (!this.group || !this.group.scripts) return false;
      return this.group.scripts.some(script => {
        const validation = script.validation || {};
        return validation.valid === false;
      });
    },
    groupValidationTooltip() {
      if (!this.hasInvalidScripts) return '';
      const invalidCount = this.group.scripts.filter(s => s.validation?.valid === false).length;
      return `This group contains ${invalidCount} invalid script${invalidCount > 1 ? 's' : ''}`;
    }
  }
}
</script>

<style scoped>

.script-list-group .collection-item.script-group {
  border: none;
  display: flex;
  flex-direction: row;
  padding-right: 16px;
  align-items: center;
}

.script-list-group .collection-item.script-group span {
  flex: 1 1 auto;
}

.script-list-group .collection-item.script-group i {
  flex: 0 0 auto;
  line-height: 16px;
}

.script-list-group .collection-item.script-group .group-warning-icon {
  color: #ff9800;
  font-size: 20px;
  margin-right: 8px;
}

.script-list-group >>> .collection-item.script-list-item {
  padding-left: 36px;
}

</style>