declare module 'nuxt/schema' {
  interface PublicRuntimeConfig {
    apiUrl: string
    wsUrl: string
    voiceMode: 'stub' | 'websocket'
  }
}
export {}