import {ref} from 'vue'
import { createSttService } from '~/services/voice/stt.factory'
import type { SttService } from '~/services/voice/stt.types'
import type { VoiceServiceStatus } from '~/types/voice'

export function useStt(service?: SttService) {
    const config = useRuntimeConfig()
    const stt = service ?? createSttService(config.public.voiceMode, config.public.wsUrl)
    const status = ref<VoiceServiceStatus>('idle')
    const lastResult = ref<string>('')

    async function transcribe(audio: Blob): Promise<string>{
        status.value = 'processing'
        try {
            const result = await stt.transcribe(audio)
            lastResult.value = result.text
            status.value = 'idle'
            return result.text
        } catch (e) {
            status.value = 'error'
            throw e
        }
    }   

    onUnmounted(() => stt.dispose?.())

    return { status, lastResult, transcribe, isProcessing: computed(() => status.value === 'processing') }
}