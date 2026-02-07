/**
 * Centralized API endpoint constants
 * All API paths use leading slashes for consistency with axios base URL
 */
export const API = {
  // Scripts
  SCRIPTS: '/scripts',

  // Configuration
  CONF: '/conf',

  // Authentication
  AUTH: {
    INFO: '/auth/info',
    CONFIG: '/auth/config',
    LOGOUT: '/logout',
  },

  // Executions
  EXECUTIONS: {
    START: '/executions/start',
    STOP: '/executions/stop',
    KILL: '/executions/kill',
    CLEANUP: '/executions/cleanup',
    STATUS: '/executions/status',
    ACTIVE: '/executions/active',
    CONFIG: '/executions/config',
  },

  // History
  HISTORY: {
    SHORT: '/history/execution_log/short',
    LONG: '/history/execution_log/long',
  },

  // Schedules
  SCHEDULES: '/schedules',
  SCHEDULE: '/schedule',

  // Schedule Settings
  SCHEDULE_SETTINGS: '/schedules/settings',

  // Admin
  ADMIN: {
    // Scripts
    SCRIPTS: '/admin/scripts',
    SCRIPTS_VALIDATE: '/admin/scripts/validate',

    // Projects
    PROJECTS: '/admin/projects',
    PROJECTS_IMPORT: '/admin/projects/import',

    // Connections
    CONNECTIONS: '/admin/connections',
    CONNECTION_TYPES: '/admin/connections/types',

    // GitHub
    GITHUB_REPOS: '/admin/github/repos',

    // Venv (Virtual Environment)
    VENV: {
      STATUS: '/admin/venv/status',
      PACKAGES: '/admin/venv/packages',
      PACKAGES_INSTALL: '/admin/venv/packages/install',
      PACKAGES_UNINSTALL: '/admin/venv/packages/uninstall',
      REQUIREMENTS: '/admin/venv/requirements',
      REQUIREMENTS_UPDATE: '/admin/venv/requirements/update',
      REQUIREMENTS_SYNC: '/admin/venv/requirements/sync',
      REQUIREMENTS_STATUS: '/admin/venv/requirements/status',
    },

    // Users
    USERS: '/admin/users',
    USERS_ADD: '/admin/users/add',

    // Auth
    AUTH_STATUS: '/admin/auth/status',
    AUTH_DEFAULT_PASSWORD_STATUS: '/admin/auth/default-password-status',

    // Logs
    LOGS_SERVER: '/admin/logs/server',

    // Filesystem
    FILESYSTEM_BROWSE: '/admin/filesystem/browse',
  },
};
