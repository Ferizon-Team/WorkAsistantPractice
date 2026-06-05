<script setup lang="ts">
import { computed, ref } from 'vue'

const draft = defineModel<string>({ default: '' })

const props = withDefaults(
  defineProps<{
    loading?: boolean
    recording?: boolean
    placeholder?: string
  }>(),
  {
    loading: false,
    recording: false,
    placeholder: 'Введите вопрос по регламентам компании…',
  }
)

const emit = defineEmits<{
  submit: []
  record: []
}>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)

const canSubmit = computed(
  () => draft.value.trim().length > 0 && !props.loading && !props.recording
)

function submit() {
  if (!canSubmit.value) return
  emit('submit')
}

function onKeydown(event: KeyboardEvent) {
  if (event.key !== 'Enter' || event.shiftKey) return
  event.preventDefault()
  submit()
}

function onRecordClick() {
  if (props.loading) return
  emit('record')
}
</script>

<template>
  <footer class="shrink-0 border-t border-default px-4 py-4 sm:px-6">
    <form
      class="flex items-end gap-2"
      @submit.prevent="submit"
    >
      <UButton
        type="button"
        :icon="recording ? 'i-lucide-square' : 'i-lucide-mic'"
        :color="recording ? 'error' : 'neutral'"
        :variant="recording ? 'solid' : 'soft'"
        :disabled="loading"
        :aria-label="recording ? 'Остановить запись' : 'Записать голос'"
        :class="{ 'animate-pulse': recording }"
        class="shrink-0"
        @click="onRecordClick"
      />

      <UTextarea
        ref="textareaRef"
        v-model="draft"
        :rows="1"
        autoresize
        :maxrows="6"
        :placeholder="placeholder"
        :disabled="loading || recording"
        aria-label="Вопрос ассистенту"
        class="flex-1"
        @keydown="onKeydown"
      />

      <UButton
        type="submit"
        icon="i-lucide-send"
        color="primary"
        :loading="loading"
        :disabled="!canSubmit"
        aria-label="Отправить"
        class="shrink-0"
      />
    </form>

    <p class="mt-2 text-center text-[11px] text-muted">
      <template v-if="recording">
        Идёт запись… Нажмите квадрат, чтобы остановить
      </template>
      <template v-else>
        Enter — отправить · Shift+Enter — новая строка · Микрофон — голос 
      </template>
    </p>
  </footer>
</template>