module.exports = {
  env: {
    node: true,
    browser: true,
    es2022: true,
  },
  plugins: [
    'vue'
  ],
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
  ],
  rules: {
    'vue/multi-word-component-names': 'off',
  }
}