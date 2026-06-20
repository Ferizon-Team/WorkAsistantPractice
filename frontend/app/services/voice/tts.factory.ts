import type { TtsService } from './tts.types'
import { createStubTtsService } from './tts.stub'
import { createWebsocketTtsService } from './tts.websocket'
import { createHttpTtsService } from './tts.http'

export function createTtsService(mode: 'stub' | 'websocket' | 'http', Url: string): TtsService {


    switch (mode) {
        case 'websocket':
            return createWebsocketTtsService(Url)
            break;
        case 'http':
            return createHttpTtsService(Url)
            break;
        default:
            return createStubTtsService()
            break;
    }
}
