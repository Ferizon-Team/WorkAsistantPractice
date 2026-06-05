<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
  }>(),
  {
    title: 'Work Assistant',
    subtitle: 'Корпоративный ассистент по базе знаний',
  }
)
</script>

<template>
  <header
    class="shrink-0 border-b border-default px-4 py-4 sm:px-6"
  >
    <div class="flex items-start gap-3">
      <div
        class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary"
        aria-hidden="true"
      >
        <UIcon name="i-lucide-bot" class="size-5" />
      </div>

      <div class="min-w-0">
        <h1 class="truncate text-lg font-semibold text-highlighted">
          {{ title }}
        </h1>
        <p class="mt-0.5 text-sm text-muted">
          {{ subtitle }}
        </p>
      </div>
    </div>
  </header>
</template>