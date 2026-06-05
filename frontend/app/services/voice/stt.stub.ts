import type { SttService } from './stt.types'
import type { SttResult } from '~/types/voice'

export function createStubSttService(): SttService {
    return {
        async transcribe(audio: Blob): Promise<SttResult> {
            await delay(800)
            return {
                text: 'Сколько дней отпуска у меня в год?',
                confidence: 1,
                isFinal: true,
            }
        },

    }

}

function delay(ms: number) {
    return new Promise((r)=>setTimeout(r, ms))
}
