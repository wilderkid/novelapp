module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2022: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:vue/vue3-essential",
    "@vue/eslint-config-prettier",
  ],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off",
    "vue/multi-word-component-names": "off",
    "no-unused-vars": "warn",
    "no-dupe-keys": "warn",
    "no-constant-condition": "warn",
  },
  ignorePatterns: [
    "dist/",
    "dist-electron/",
    "node_modules/",
    "public/static/UEditorPlus/",
  ],
};
