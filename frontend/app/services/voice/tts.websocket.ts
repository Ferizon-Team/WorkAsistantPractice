import type { TtsService } from './tts.types'
import type { TtsResult } from '~/types/voice'
import { VoiceError } from '~/types/voice'

export function createWebsocketTtsService(wsUrl: string): TtsService {
    return {
        async synthesize(text: string): Promise<TtsResult> {
            void wsUrl
            throw new VoiceError('websocket TTS не подключен', 'WS_DISCONNECTED')
        }
    }
}