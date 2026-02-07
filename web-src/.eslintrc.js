module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es6: true
  },
  extends: [
    'plugin:vue/essential',
    'eslint:recommended'
  ],
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module'
  },
  rules: {
    // Prevent console.log statements (console.error and console.warn are allowed)
    'no-console': ['error', { allow: ['warn', 'error'] }],

    // Prevent debugger statements in production
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn'
  }
}
