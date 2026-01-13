/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  // Vite 内置的 DEV, MODE, PROD, SSR 等属性已经在 vite/client 中定义
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
