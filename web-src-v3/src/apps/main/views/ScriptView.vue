<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import ScriptViewComponent from '../components/ScriptView.vue'

const route = useRoute()
const scriptName = computed(() => route.params.name as string)
</script>

<template>
  <AppLayout>
    <template #content>
      <ScriptViewComponent :script-name="scriptName" />
    </template>
  </AppLayout>
</template>
