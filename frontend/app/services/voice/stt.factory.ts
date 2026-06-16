import type { SttService } from './stt.types'
import { createStubSttService } from './stt.stub'
import { createWebsocketSttService } from './stt.websocket'
import { createHttpSttService } from './stt.http'

export function createSttService(mode: 'stub' | 'websocket' | 'http', Url: string): SttService {
    
    switch (mode) {
            case 'websocket':
                return createWebsocketSttService(Url)
                break;
            case 'http':
                return createHttpSttService(Url)
                break;
            default:
                return createStubSttService()
                break;
        }
}
