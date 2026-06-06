import { ref, computed, onUnmounted } from 'vue'
import { createTtsService } from '~/services/voice/tts.factory'
import type { TtsService } from '~/services/voice/tts.types'
import type { VoiceServiceStatus } from '~/types/voice'
import { AudioPlayer } from '~/utils/audio/player'

export function useTts(service?: TtsService) {
    const config = useRuntimeConfig()
    const tts = service ?? createTtsService(config.public.voiceMode, config.public.wsUrl)
    const player = new AudioPlayer()
    const status = ref<VoiceServiceStatus>('idle')

    async function speak(text: string): Promise<void>{
        if (!text.trim()) return
        status.value = 'processing'

        try{
            const { audio } = await tts.synthesize(text)
            status.value = 'playing'
            if (audio.size > 0) {
                await player.play(audio)
            }

        }finally {
            status.value = 'idle'
        }
    }

    function stop() {
        player.stop()
        status.value = 'idle'
    }

    onUnmounted(() => {
        stop()
        tts.dispose?.()
    })

    return { status, speak, stop, isPlaying: computed(() => status.value === 'playing' || status.value === 'processing') }
}