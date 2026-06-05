import type { SttService } from './stt.types'
import type { SttResult } from '~/types/voice'
import { VoiceError } from '~/types/voice'

export function createWebsocketSttService(wsUrl: string): SttService {
    return {
        async transcribe(audio: Blob): Promise<SttResult> {
            void wsUrl
            throw new VoiceError('STT по WebSocket пока не реализован', 'STT_FAILED')
        }
    }
}