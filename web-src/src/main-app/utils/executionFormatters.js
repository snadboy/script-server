/**
 * Shared utility functions for formatting execution and schedule data
 */

/**
 * Extract display name from a user object
 * @param {Object|string} user - User object or string
 * @returns {string} Display name
 */
export function getUserName(user) {
  if (!user) return 'Unknown';
  if (typeof user === 'string') return user;
  if (user.user_id) return user.user_id;
  if (user.audit_names && user.audit_names.auth_username) {
    return user.audit_names.auth_username;
  }
  return 'Unknown';
}

/**
 * Format next execution time
 * @param {Object} schedule - Schedule object with next_execution property
 * @returns {string} Formatted next execution time
 */
export function formatNextExecution(schedule) {
  if (!schedule.next_execution) {
    return 'No upcoming execution';
  }
  const date = new Date(schedule.next_execution);
  return formatDateCompact(date);
}

/**
 * Format a date as 'M/D/YYYY @ HH:MM'
 * @param {Date} date - Date object to format
 * @returns {string} Formatted date string
 */
function formatDateCompact(date) {
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const year = date.getFullYear();
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${month}/${day}/${year} @ ${hours}:${minutes}`;
}

/**
 * Format last execution time
 * @param {Object} schedule - Schedule object with last_execution property
 * @returns {string} Formatted last execution time
 */
export function formatLastExecution(schedule) {
  if (!schedule.last_execution) {
    return 'Never';
  }
  const date = new Date(schedule.last_execution);
  return formatDateCompact(date);
}

/**
 * Format a parameter value for display
 * @param {*} value - Parameter value
 * @returns {string} Formatted value
 */
export function formatParamValue(value) {
  if (value === null || value === undefined) {
    return '(empty)';
  }
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }
  return String(value);
}

/**
 * Get schedule description from schedules array by ID
 * Returns the user's custom description if set, otherwise returns timing info
 * @param {string|number} scheduleId - Schedule ID to find
 * @param {Array} schedules - Array of schedule objects
 * @returns {string} Schedule description or empty string
 */
export function getScheduleDescription(scheduleId, schedules) {
  if (!scheduleId || !schedules) return '';
  const schedule = schedules.find(s => String(s.id) === String(scheduleId));
  if (!schedule) return '';

  // Return user's description if set
  if (schedule.description) {
    return schedule.description;
  }

  // Otherwise return timing info
  if (schedule.schedule && schedule.schedule.repeatable) {
    return `Every ${schedule.schedule.repeat_period} ${schedule.schedule.repeat_unit}`;
  }

  return 'One-time';
}

/**
 * Determine execution status category
 * @param {Object} execution - Execution object
 * @returns {string} Status category: 'running', 'success', or 'error'
 */
export function getExecutionStatus(execution) {
  if (!execution.status) return 'success';
  const status = execution.status.toLowerCase();
  if (status === 'running') return 'running';
  if (status === 'finished') {
    return execution.exitCode === 0 ? 'success' : 'error';
  }
  return 'error';
}

/**
 * Check if a schedule has parameters
 * @param {Object} schedule - Schedule object
 * @returns {boolean} True if schedule has parameters
 */
export function hasParameters(schedule) {
  return schedule.parameter_values && Object.keys(schedule.parameter_values).length > 0;
}

/**
 * Get script description from scripts array by name
 * @param {string} scriptName - Script name to find
 * @param {Array} scripts - Array of script objects from scripts store
 * @returns {string} Script description or empty string
 */
export function getScriptDescription(scriptName, scripts) {
  if (!scriptName || !scripts) return '';
  const script = scripts.find(s => s.name === scriptName);
  return script?.description || '';
}

/**
 * Get script configuration from scripts array by name
 * @param {string} scriptName - Script name to find
 * @param {Array} scripts - Array of script objects from scripts store
 * @returns {Object|null} Script configuration object or null
 */
export function getScriptConfig(scriptName, scripts) {
  if (!scriptName || !scripts) return null;
  return scripts.find(s => s.name === scriptName) || null;
}

/**
 * Filter parameters based on verb configuration
 * Returns only parameters relevant to the verb that was used in the execution
 * @param {Object} parameterValues - All parameter values from execution
 * @param {Object} scriptConfig - Full script configuration object
 * @returns {Object} Filtered parameter values
 */
export function filterParametersByVerb(parameterValues, scriptConfig) {
  if (!parameterValues || !scriptConfig) {
    return parameterValues;
  }

  // If script doesn't use verbs, return all parameters
  if (!scriptConfig.verbs || !scriptConfig.verbs.parameterName) {
    return parameterValues;
  }

  const verbParamName = scriptConfig.verbs.parameterName;
  const verbValue = parameterValues[verbParamName];

  // If no verb value found, return all parameters
  if (!verbValue) {
    return parameterValues;
  }

  // Find the verb option that was used
  const verbOption = scriptConfig.verbs.options?.find(opt => opt.name === verbValue);
  if (!verbOption) {
    return parameterValues;
  }

  // Build set of allowed parameter names
  const allowedParams = new Set();

  // Always include the verb parameter itself
  allowedParams.add(verbParamName);

  // Include shared parameters
  if (scriptConfig.sharedParameters) {
    scriptConfig.sharedParameters.forEach(p => allowedParams.add(p));
  }

  // Include parameters specific to this verb
  if (verbOption.parameters) {
    verbOption.parameters.forEach(p => allowedParams.add(p));
  }

  // Filter the parameter values
  const filtered = {};
  for (const [key, value] of Object.entries(parameterValues)) {
    if (allowedParams.has(key)) {
      filtered[key] = value;
    }
  }

  return filtered;
}
