<script setup lang="ts">
import { computed, toRef, watch } from 'vue'
import type { ChatMessage } from '~/types/chat'

const props = defineProps<{
  message: ChatMessage
}>()

const content = toRef(() => props.message.content)

watch(content, (newContent) => {
  console.log('Content updated:', newContent)
})

const isUser = computed(() => props.message.role === 'user')
const isAssistant = computed(() => props.message.role === 'assistant')

const timeLabel = computed(() =>
  props.message.createdAt.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })
)

const bubbleClass = computed(() => {
  if (isUser.value) {
    return 'bg-primary text-inverted ml-auto'
  }
  return 'bg-elevated text-default mr-auto'
})

const wrapperClass = computed(() =>
  isUser.value ? 'justify-end' : 'justify-start'
)
</script>

<template>
  <article
    class="flex w-full"
    :class="wrapperClass"
    :aria-label="isUser ? 'Ваше сообщение' : 'Ответ ассистента'"
  >
    <div
      class="flex max-w-[85%] flex-col sm:max-w-[75%]"
      :class="{ 'items-end': isUser, 'items-start': isAssistant }"
    >
      <div
        class="rounded-2xl px-4 py-3 shadow-sm"
        :class="[
          bubbleClass,
          isUser ? 'rounded-br-md' : 'rounded-bl-md',
        ]"
      >
        <!-- Ожидание ответа -->
        <div
          v-if="message.pending"
          class="flex items-center gap-2 text-sm"
          aria-live="polite"
        >
          <span class="inline-flex gap-1">
            <span class="size-2 animate-bounce rounded-full bg-current opacity-60 [animation-delay:-0.3s]" />
            <span class="size-2 animate-bounce rounded-full bg-current opacity-60 [animation-delay:-0.15s]" />
            <span class="size-2 animate-bounce rounded-full bg-current opacity-60" />
          </span>
          <span class="text-muted">Думаю…</span>
        </div>

        <!-- Текст -->
        <p
          v-else
          class="whitespace-pre-wrap text-sm leading-relaxed"
        >
          {{ content }}
        </p>
      </div>

      <div
        v-if="isAssistant && !message.pending && message.sources?.length"
        class="mt-1 w-full min-w-0 max-w-full rounded-2xl rounded-tl-md border border-default bg-default px-4 py-2 shadow-sm"
      >
        <ChatSources :sources="message.sources" />
      </div>

      <time
        class="mt-1 px-1 text-[11px] text-muted"
        :datetime="message.createdAt.toISOString()"
      >
        {{ timeLabel }}
      </time>
    </div>
  </article>
</template>