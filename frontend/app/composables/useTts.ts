import { ref, computed, onUnmounted } from 'vue'
import { createTtsService } from '~/services/voice/tts.factory'
import type { TtsService } from '~/services/voice/tts.types'
import type { VoiceServiceStatus } from '~/types/voice'
import { AudioPlayer } from '~/utils/audio/player'
import { StreamingAudioPlayer } from '~/utils/audio/streamingPlayer'

export function useTts(service?: TtsService) {
    const config = useRuntimeConfig()
    const url = config.public.apiUrl || 'http://localhost:8000'
    const tts = service ?? createTtsService(config.public.voiceMode, url)
    const legacyPlayer = new AudioPlayer()
    const streamingPlayer = new StreamingAudioPlayer()
    const status = ref<VoiceServiceStatus>('idle')

    async function speak(text: string): Promise<void>{
        if (!text.trim()) return
        status.value = 'processing'

        try {
            const { audio } = await tts.synthesize(text)
            status.value = 'playing'
            if (audio.size > 0) {
                await legacyPlayer.play(audio)
            }
        } finally {
            status.value = 'idle'
        }
    }

    function stopLegacy(): void {
        legacyPlayer.stop()
    }

    async function initStreaming(): Promise<void> {
        await streamingPlayer.init()
    }

    async function appendChunk(base64Chunk: string): Promise<void> {
        if (status.value === 'idle') {
            status.value = 'playing'
        }
        await streamingPlayer.appendChunk(base64Chunk)
    }

    function stopStreaming(): void {
        streamingPlayer.stop()
        status.value = 'idle'
    }

    function stop(): void {
        stopLegacy()
        stopStreaming()
        status.value = 'idle'
    }

    onUnmounted(() => {
        stop()
        streamingPlayer.dispose()
        tts.dispose?.()
    })

    return { status, speak, initStreaming, appendChunk, stopStreaming, stop, isPlaying: computed(() => status.value === 'playing' || status.value === 'processing') }
}