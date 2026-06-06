<script setup lang="ts">
import type { ChatMessage } from '~/types/chat'

const draft = defineModel<string>('draft', { default: '' })

defineProps<{
  messages: ChatMessage[]
  loading?: boolean
  recording?: boolean
}>()

const emit = defineEmits<{
  submit: []
  record: []
}>()
</script>

<template>
  <div class="min-h-dvh bg-muted p-3 sm:p-4">
    <div
      class="mx-auto flex h-[calc(100dvh-1.5rem)] w-full max-w-3xl flex-col overflow-hidden rounded-2xl border border-default bg-default shadow-lg sm:h-[calc(100dvh-2rem)]"
    >
      <ChatHeader />
      <ChatMessageList :messages="messages" />
      <ChatComposer
        v-model="draft"
        :loading="loading"
        :recording="recording"
        @submit="emit('submit')"
        @record="emit('record')"
      />
    </div>
  </div>
</template>