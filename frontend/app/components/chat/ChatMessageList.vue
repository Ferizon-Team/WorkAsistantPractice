<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import type { ChatMessage } from '~/types/chat'

const props = defineProps<{
  messages: ChatMessage[]
}>()

const listRef = ref<HTMLElement | null>(null)

async function scrollToBottom(smooth = true) {
  await nextTick()
  const el = listRef.value
  if (!el) return
  el.scrollTo({
    top: el.scrollHeight,
    behavior: smooth ? 'smooth' : 'auto',
  })
}

watch(
  () => props.messages.length,
  () => scrollToBottom(true)
)

watch(
  () => props.messages.map((m) => m.content + String(m.pending)).join('|'),
  () => scrollToBottom(false)
)

onMounted(() => scrollToBottom(false))
</script>

<template>
  <div
    ref="listRef"
    class="min-h-0 flex-1 overflow-y-auto px-4 py-4 sm:px-6"
    role="log"
    aria-live="polite"
    aria-relevant="additions"
  >
    <div
      v-if="messages.length === 0"
      class="flex h-full min-h-[200px] flex-col items-center justify-center text-center"
    >
      <UIcon
        name="i-lucide-message-circle"
        class="mb-3 size-10 text-muted"
      />
      <p class="text-sm font-medium text-highlighted">
        Задайте вопрос
      </p>
      <p class="mt-1 max-w-sm text-sm text-muted">
        Например: «Сколько дней отпуска?» или «Какой пароль от Wi‑Fi?»
      </p>
    </div>

    <div
      v-else
      class="flex flex-col gap-4"
    >
      <ChatMessage
        v-for="msg in messages"
        :key="msg.id"
        :message="msg"
      />
    </div>
  </div>
</template>