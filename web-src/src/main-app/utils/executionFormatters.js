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
 * Format next execution time with relative display for near times
 * @param {Object} schedule - Schedule object with next_execution property
 * @returns {string} Formatted next execution time
 */
export function formatNextExecution(schedule) {
  if (!schedule.next_execution) {
    return 'No upcoming execution';
  }
  const date = new Date(schedule.next_execution);
  const now = new Date();
  const diff = date - now;

  // Show relative time if within 24 hours
  if (diff > 0 && diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    const minutes = Math.floor((diff % (60 * 60 * 1000)) / (60 * 1000));
    if (hours > 0) {
      return `In ${hours}h ${minutes}m`;
    }
    return `In ${minutes}m`;
  }

  return date.toLocaleString();
}

/**
 * Format last execution time with relative display for recent times
 * @param {Object} schedule - Schedule object with last_execution property
 * @returns {string} Formatted last execution time
 */
export function formatLastExecution(schedule) {
  if (!schedule.last_execution) {
    return 'Never';
  }
  const date = new Date(schedule.last_execution);
  const now = new Date();
  const diff = now - date;

  // Show relative time if within 24 hours
  if (diff > 0 && diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    const minutes = Math.floor((diff % (60 * 60 * 1000)) / (60 * 1000));
    if (hours > 0) {
      return `${hours}h ${minutes}m ago`;
    }
    if (minutes > 0) {
      return `${minutes}m ago`;
    }
    return 'Just now';
  }

  return date.toLocaleString();
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
 * @param {string|number} scheduleId - Schedule ID to find
 * @param {Array} schedules - Array of schedule objects
 * @returns {string} Schedule description or empty string
 */
export function getScheduleDescription(scheduleId, schedules) {
  if (!scheduleId || !schedules) return '';
  const schedule = schedules.find(s => String(s.id) === String(scheduleId));
  return schedule ? schedule.description || '' : '';
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
