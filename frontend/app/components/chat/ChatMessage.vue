<script setup lang="ts">
import { computed, toRef, watch, ref, nextTick } from 'vue'
import type { ChatMessage } from '~/types/chat'

const props = defineProps<{
  message: ChatMessage
}>()

const content = toRef(() => props.message.content)

const displayText = ref('')
const targetText = ref('')
const isTyping = ref(false)
const hasAnimated = ref(false)

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

let typingTimer: ReturnType<typeof setTimeout> | null = null
let charIndex = 0

function startTyping(fullText: string) {
  if (hasAnimated.value && displayText.value === fullText) return
  
  targetText.value = fullText
  isTyping.value = true
  
  if (displayText.value === fullText) {
    isTyping.value = false
    hasAnimated.value = true
    return
  }
  
  charIndex = displayText.value.length
  
  const typeNext = () => {
    if (charIndex < targetText.value.length) {
      const charsPerFrame = Math.min(3, targetText.value.length - charIndex)
      displayText.value = targetText.value.slice(0, charIndex + charsPerFrame)
      charIndex += charsPerFrame
      
      typingTimer = setTimeout(typeNext, 25 + Math.random() * 30)
    } else {
      isTyping.value = false
      hasAnimated.value = true
    }
  }
  
  typeNext()
}

function stopTyping() {
  if (typingTimer) {
    clearTimeout(typingTimer)
    typingTimer = null
  }
  isTyping.value = false
}

watch(content, (newContent) => {
  if (!newContent) return
  
  if (isUser.value) {
    displayText.value = newContent
    return
  }
  
  startTyping(newContent)
}, { immediate: true })

onBeforeUnmount(() => {
  stopTyping()
})
</script>

<template>
  <article
    class="flex w-full message-enter"
    :class="wrapperClass"
    :aria-label="isUser ? 'Ваше сообщение' : 'Ответ ассистента'"
  >
    <div
      class="flex max-w-[85%] flex-col sm:max-w-[75%]"
      :class="{ 'items-end': isUser, 'items-start': isAssistant }"
    >
      <div
        class="rounded-2xl px-4 py-3 shadow-sm transition-all duration-300 relative overflow-hidden"
        :class="[
          bubbleClass,
          isUser ? 'rounded-br-md' : 'rounded-bl-md',
          isAssistant && isTyping ? 'ring-1 ring-primary/30 shadow-md shadow-primary/10' : '',
        ]"
      >
        <div
          v-if="message.pending && !displayText && !targetText"
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

        <p
          v-else
          class="whitespace-pre-wrap text-sm leading-relaxed min-h-[1.5em]"
        >
          {{ displayText }}
          <!-- Мигающий курсор -->
          <span
            v-if="isTyping"
            class="typing-cursor"
          />
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

<style scoped>
.message-enter {
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1.1em;
  background: currentColor;
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: cursorBlink 0.8s ease-in-out infinite;
}

@keyframes cursorBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.bg-elevated {
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
</style>