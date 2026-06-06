import type { TtsService } from './tts.types'
import { createStubTtsService } from './tts.stub'
import { createWebsocketTtsService } from './tts.websocket'

export function createTtsService(mode: 'stub' | 'websocket', wsUrl: string): TtsService {

    if (mode === 'websocket') return createWebsocketTtsService(wsUrl)
    return createStubTtsService()

}
