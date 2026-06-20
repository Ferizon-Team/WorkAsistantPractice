import type { TtsService } from './tts.types'
import type { TtsResult } from '~/types/voice'
import { VoiceError } from '~/types/voice'


export function createHttpTtsService(apiUrl: string): TtsService {
    return {
        async synthesize(text: string): Promise<TtsResult> {
            try {
                const response = await $fetch<{
                    audio_base64: string
                    file_name: string
                    format: string
                    text_length: number
                }>('/api/v1/tts/synthesize', {
                    baseURL: apiUrl,
                    method: 'POST',
                    body: { text, file_name: undefined },
                })

                const byteCharacters = atob(response.audio_base64)
                const byteNumbers = new Array(byteCharacters.length)
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i)
                }
                const byteArray = new Uint8Array(byteNumbers)
                const mimeType = `audio/${response.format === 'wav' ? 'wav' : response.format}`
                const audio = new Blob([byteArray], { type: mimeType })

                return {
                    audio,
                    mimeType,
                }
            } catch (error: any) {
                throw new VoiceError(
                    error?.data?.detail || error?.message || 'Ошибка синтеза речи',
                    'TTS_FAILED'
                )
            }
        },
    }
}