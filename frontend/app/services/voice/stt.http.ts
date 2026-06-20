import type { SttService } from './stt.types'
import type { SttResult } from '~/types/voice'
import { VoiceError } from '~/types/voice'

export function createHttpSttService(apiUrl: string): SttService {
    return {
        async transcribe(audio: Blob): Promise<SttResult> {
            console.log('STT API URL:', apiUrl)
            try {
                const base64 = await blobToBase64(audio)
                const cleanBase64 = base64.includes(',') ? base64.split(',')[1] : base64

                const response = await $fetch<{
                    text: string
                    text_length: number
                    language: string | null
                    confidence: number | null
                }>('/api/v1/stt/transcribe', {
                    baseURL: apiUrl,
                    method: 'POST',
                    body: { audio_base64: cleanBase64 },
                })

                return {
                    text: response.text,
                    confidence: response.confidence ?? 1,
                    isFinal: true,
                }
            } catch (error: any) {
                throw new VoiceError(
                    error?.data?.detail || error?.message || 'Ошибка распознавания речи',
                    'STT_FAILED'
                )
            }
        },
    }
}

function blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onloadend = () => resolve(reader.result as string)
        reader.onerror = reject
        reader.readAsDataURL(blob)
    })
}