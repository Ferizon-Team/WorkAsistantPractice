<script setup lang="ts">
import { ref } from 'vue'
import { useTts } from '~/composables/useTts'
import { useVoiceInput } from '~/composables/useVoiceInput'
import type { ChatMessage, RagAnswerResponse } from '~/types/chat'
import {
  assistantMessageFromRag,
  createMessageId,
  userMessageFromText,
} from '~/types/chat'

const config = useRuntimeConfig()
const toast = useToast()

const messages = ref<ChatMessage[]>([])
const draft = ref('')
const isLoading = ref(false)

async function onSubmit() {
  const text = draft.value.trim()
  if (!text || isLoading.value) return

  messages.value.push(userMessageFromText(text))
  draft.value = ''

  const pendingId = createMessageId()
  messages.value.push({
    id: pendingId,
    role: 'assistant',
    content: '',
    createdAt: new Date(),
    pending: true,
  })

  isLoading.value = true

  try {
    const response = await $fetch<RagAnswerResponse>(
      '/api/v1/document/request',
      {
        baseURL: config.public.apiUrl,
        query: { question: text },
      }
    )

    replacePendingMessage(pendingId, assistantMessageFromRag(response, pendingId))
    const answer = messages.value.find((m) => m.id === pendingId)
    if (answer?.content) {
        void tts.speak(answer.content)
    }
  } catch (error) {
    console.error(error)
    replacePendingMessage(pendingId, {
      id: pendingId,
      role: 'assistant',
      content:
        'Не удалось получить ответ. Проверьте, что бэкенд запущен и база заполнена документами.',
      createdAt: new Date(),
      pending: false,
    })
    toast.add({
      title: 'Ошибка',
      description: 'Сервер недоступен или вернул ошибку.',
      color: 'error',
    })
  } finally {
    isLoading.value = false
  }
}

const voice = useVoiceInput()
const tts = useTts()

const isRecording = voice.isRecording

async function onRecord() {
    const text = await voice. toggleRecording()
    if (text) {
        draft.value = text
        await onSubmit()
    }
}

function replacePendingMessage(id: string, message: ChatMessage) {
  const index = messages.value.findIndex((m) => m.id === id)
  if (index !== -1) {
    messages.value[index] = message
  }
}
</script>

<template>
  <ChatLayout
    v-model:draft="draft"
    :messages="messages"
    :loading="isLoading"
    :recording="isRecording"
    @submit="onSubmit"
    @record="onRecord"
  />
</template>