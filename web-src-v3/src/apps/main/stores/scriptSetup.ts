import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useScriptConfigStore } from './scriptConfig'
import type { Parameter } from '@shared/types/api'

type ParameterValue = string | number | boolean | string[] | File | null

export const useScriptSetupStore = defineStore('scriptSetup', () => {
  const configStore = useScriptConfigStore()

  const parameterValues = ref<Record<string, ParameterValue>>({})
  const errors = ref<Record<string, string | null>>({})
  const forcedValueParameters = ref<string[]>([])

  const hasErrors = computed(() => {
    return Object.values(errors.value).some((e) => e !== null)
  })

  const isValid = computed(() => {
    // Check required parameters
    for (const param of configStore.parameters) {
      if (param.required) {
        const value = parameterValues.value[param.name]
        if (value === undefined || value === null || value === '') {
          return false
        }
      }
    }
    return !hasErrors.value
  })

  // Watch for parameter changes and initialize values
  watch(
    () => configStore.parameters,
    (newParams) => {
      initFromParameters(newParams)
    },
    { immediate: true }
  )

  function initFromParameters(params: Parameter[]) {
    for (const param of params) {
      // Only set if not already set
      if (parameterValues.value[param.name] === undefined) {
        parameterValues.value[param.name] = getDefaultValue(param)
      }
    }

    // Remove values for parameters that no longer exist
    const paramNames = new Set(params.map((p) => p.name))
    for (const key of Object.keys(parameterValues.value)) {
      if (!paramNames.has(key)) {
        delete parameterValues.value[key]
        delete errors.value[key]
      }
    }
  }

  function getDefaultValue(param: Parameter): ParameterValue {
    if (param.default !== undefined) {
      return param.default as ParameterValue
    }

    // Default based on type
    switch (param.type) {
      case 'multiselect':
        return []
      case 'file_upload':
        return null
      default:
        // For checkbox/flag type parameters (withoutValue)
        if (param.withoutValue) {
          return false
        }
        return ''
    }
  }

  function setValue(paramName: string, value: ParameterValue) {
    parameterValues.value[paramName] = value

    // Notify server of value change
    configStore.sendParameterValue(paramName, value)

    // Validate
    const param = configStore.parameters.find((p) => p.name === paramName)
    if (param) {
      validateParameter(param, value)
    }
  }

  function validateParameter(param: Parameter, value: ParameterValue) {
    errors.value[param.name] = null

    // Required check
    if (param.required) {
      if (value === undefined || value === null || value === '') {
        errors.value[param.name] = 'This field is required'
        return
      }
      if (Array.isArray(value) && value.length === 0) {
        errors.value[param.name] = 'Please select at least one option'
        return
      }
    }

    // Type-specific validation
    if (param.type === 'int' && value !== '' && value !== null) {
      const num = Number(value)
      if (isNaN(num)) {
        errors.value[param.name] = 'Must be a number'
        return
      }
      if (param.min !== undefined && num < param.min) {
        errors.value[param.name] = `Minimum value is ${param.min}`
        return
      }
      if (param.max !== undefined && num > param.max) {
        errors.value[param.name] = `Maximum value is ${param.max}`
        return
      }
    }
  }

  function setForced(paramName: string, forced: boolean) {
    if (forced && !forcedValueParameters.value.includes(paramName)) {
      forcedValueParameters.value.push(paramName)
    } else if (!forced) {
      const index = forcedValueParameters.value.indexOf(paramName)
      if (index !== -1) {
        forcedValueParameters.value.splice(index, 1)
      }
    }
  }

  function reset() {
    parameterValues.value = {}
    errors.value = {}
    forcedValueParameters.value = []
    initFromParameters(configStore.parameters)
  }

  function buildFormData(): FormData {
    const formData = new FormData()

    for (const param of configStore.parameters) {
      const value = parameterValues.value[param.name]

      if (value === undefined || value === null) {
        continue
      }

      // Handle file uploads
      if (value instanceof File) {
        formData.append(param.name, value)
        continue
      }

      // Handle arrays (multiselect)
      if (Array.isArray(value)) {
        for (const item of value) {
          formData.append(param.name, String(item))
        }
        continue
      }

      // Handle boolean (checkbox/flag)
      if (typeof value === 'boolean') {
        if (value) {
          formData.append(param.name, 'true')
        }
        continue
      }

      // Handle other values
      if (value !== '') {
        formData.append(param.name, String(value))
      }
    }

    return formData
  }

  return {
    parameterValues,
    errors,
    forcedValueParameters,
    hasErrors,
    isValid,
    setValue,
    setForced,
    reset,
    buildFormData,
  }
})
