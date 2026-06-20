import {ref} from 'vue'
import { createSttService } from '~/services/voice/stt.factory'
import type { SttService } from '~/services/voice/stt.types'
import type { VoiceServiceStatus } from '~/types/voice'

export function useStt(service?: SttService) {
    const config = useRuntimeConfig()
    const url = config.public.apiUrl || 'http://localhost:8000'
    const stt = service ?? createSttService(config.public.voiceMode, url)
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