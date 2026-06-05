<script setup lang="ts">
import { ref } from 'vue'
import type { ChatSource } from '~/types/chat'

defineProps<{
  sources: ChatSource[]
}>()

const blockOpen = ref(false)

const expandedItems = ref<Set<number>>(new Set())

function toggleBlock() {
  blockOpen.value = !blockOpen.value
}

function toggleItem(index: number) {
  const next = new Set(expandedItems.value)
  if (next.has(index)) {
    next.delete(index)
  } else {
    next.add(index)
  }
  expandedItems.value = next
}

function isItemExpanded(index: number) {
  return expandedItems.value.has(index)
}
</script>

<template>
  <div v-if="sources.length > 0" class="mt-3 border-t border-default pt-3">
    <button
      type="button"
      class="flex w-full items-center justify-between gap-2 rounded-lg px-1 py-1 text-left transition-colors hover:bg-elevated/50"
      :aria-expanded="blockOpen"
      @click="toggleBlock"
    >
      <span class="text-xs font-medium text-muted">
        Источники ({{ sources.length }})
      </span>
      <UIcon
        name="i-lucide-chevron-down"
        class="size-4 shrink-0 text-muted transition-transform duration-200"
        :class="{ 'rotate-180': blockOpen }"
      />
    </button>

    <ul
      v-show="blockOpen"
      class="mt-2 space-y-1"
    >
      <li
        v-for="(source, index) in sources"
        :key="`${source.title}-${index}`"
        class="overflow-hidden rounded-lg border border-default/60 bg-elevated/30"
      >
        <button
          type="button"
          class="flex w-full items-start gap-2 px-3 py-2.5 text-left text-sm transition-colors hover:bg-elevated/60"
          :aria-expanded="isItemExpanded(index)"
          @click="toggleItem(index)"
        >
          <UIcon
            name="i-lucide-chevron-right"
            class="mt-0.5 size-4 shrink-0 text-muted transition-transform duration-200"
            :class="{ 'rotate-90': isItemExpanded(index) }"
          />
          <span class="min-w-0 flex-1 font-medium text-highlighted">
            {{ source.title }}
          </span>
        </button>

        <div
          v-show="isItemExpanded(index)"
          class="border-t border-default/60 px-3 py-2.5"
        >
          <p class="whitespace-pre-wrap text-sm leading-relaxed text-muted">
            {{ source.snippet }}
          </p>
        </div>

        <!-- Свернуто: одна строка -->
        <p
          v-if="!isItemExpanded(index)"
          class="line-clamp-2 px-3 pb-2.5 pl-9 text-xs text-muted"
        >
          {{ source.snippet }}
        </p>
      </li>
    </ul>
  </div>
</template>