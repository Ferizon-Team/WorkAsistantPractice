// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  ssr: false,
  devtools: { enabled: true },
  modules: [
    '@nuxt/ui',
    '@nuxtjs/google-fonts',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxt/image',
    '@nuxtjs/color-mode'
  ],
  
  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    public: {
      voiceMode: process.env.VOICE_MODE || 'http',
      apiUrl: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      wsUrl: process.env.NUXT_PUBLIC_WS_URL || 'ws://localhost:8000',
    },
  },
})