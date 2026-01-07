import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@shared/services/api'
import type { Script } from '@shared/types/api'

export const useScriptsStore = defineStore('scripts', () => {
  const scripts = ref<Script[]>([])
  const selectedScript = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')

  // Group scripts by their group property
  const groupedScripts = computed(() => {
    const filtered = searchQuery.value
      ? scripts.value.filter((s) =>
          s.name.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      : scripts.value

    return filtered.reduce(
      (groups, script) => {
        const group = script.group || 'Ungrouped'
        if (!groups[group]) {
          groups[group] = []
        }
        groups[group].push(script)
        return groups
      },
      {} as Record<string, Script[]>
    )
  })

  // Sorted group names (Ungrouped last)
  const sortedGroups = computed(() => {
    const groups = Object.keys(groupedScripts.value)
    return groups.sort((a, b) => {
      if (a === 'Ungrouped') return 1
      if (b === 'Ungrouped') return -1
      return a.localeCompare(b)
    })
  })

  async function loadScripts(mode?: string) {
    loading.value = true
    error.value = null

    try {
      const response = await api.getScripts(mode)
      scripts.value = response.scripts
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load scripts'
    } finally {
      loading.value = false
    }
  }

  function selectScript(name: string) {
    selectedScript.value = name
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  return {
    scripts,
    selectedScript,
    loading,
    error,
    searchQuery,
    groupedScripts,
    sortedGroups,
    loadScripts,
    selectScript,
    setSearchQuery,
  }
})
