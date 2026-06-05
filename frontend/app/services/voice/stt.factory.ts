import type { SttService } from './stt.types'
import { createStubSttService } from './stt.stub'
import { createWebsocketSttService } from './stt.websocket'

export function createSttService(mode: 'stub' | 'websocket', wsUrl: string): SttService {
    if (mode === 'websocket') return createWebsocketSttService(wsUrl)
    return createStubSttService()
}
