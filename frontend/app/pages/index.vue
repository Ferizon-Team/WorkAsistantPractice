<script setup lang="ts">
import { ref, watch  } from 'vue'
import { useTts } from '~/composables/useTts'
import { useVoiceInput } from '~/composables/useVoiceInput'
import { useRagStream } from '~/composables/useRagStream'
import type { ChatMessage, RagAnswerResponse } from '~/types/chat'
import {
  assistantMessageFromRag,
  createMessageId,
  userMessageFromText,
} from '~/types/chat'

const config = useRuntimeConfig()
const toast = useToast()
const rag = useRagStream()

const messages = ref<ChatMessage[]>([])
const draft = ref('')
const isLoading = ref(false)

function getLastAssistantIndex(): number {
  return messages.value.findLastIndex((m) => m.role === 'assistant')
}

watch(rag.fullAnswer, (newAnswer) => {
  if (!newAnswer) return

  const index = getLastAssistantIndex()
  if (index === -1) return

  const msg = messages.value[index]
  if (!msg) return

  messages.value.splice(index, 1, {
    ...msg,
    content: newAnswer,
    pending: false,
  })
})

watch(rag.audioChunks, async (newChunks, oldChunks) => {
    if (newChunks.length === 0) return
    
    const lastChunk = newChunks[newChunks.length - 1]
    if (!lastChunk) return
    
    try {
        await tts.appendChunk(lastChunk)
    } catch (e) {
        console.error('TTS chunk playback error:', e)
    }
}, { deep: true })

watch(rag.isStreaming, async (streaming) => {
    if (streaming) {
        try {
            await tts.initStreaming()
        } catch (e) {
            console.warn('Failed to init streaming audio:', e)
        }
    } else {
        setTimeout(() => {
            if (!tts.isPlaying.value) {
                tts.stopStreaming()
            }
        }, 2000)
    }
})

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
    await rag.ask(text)
  } catch (wsError) {
    console.warn('WebSocket failed, falling back to HTTP:', wsError)
    try {
      const response = await $fetch('/api/v1/document/request', {
        baseURL: config.public.apiUrl,
        query: { question: text },
      }) as unknown as RagAnswerResponse

      const index = messages.value.findIndex((m) => m.id === pendingId)
      if (index !== -1) {
        messages.value[index] = assistantMessageFromRag(response, pendingId)
      }
      void tts.speak(response.answer)
    } catch (httpError) {
      console.error(httpError)
      const index = messages.value.findIndex((m) => m.id === pendingId)
      if (index !== -1) {
        messages.value[index] = {
          id: pendingId,
          role: 'assistant',
          content: 'Не удалось получить ответ. Проверьте, что бэкенд запущен и база заполнена документами.',
          createdAt: new Date(),
          pending: false,
        }
      }
      toast.add({
        title: 'Ошибка',
        description: 'Сервер недоступен или вернул ошибку.',
        color: 'error',
      })
    }
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