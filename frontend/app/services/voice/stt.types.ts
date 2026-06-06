import type { SttResult } from '~/types/voice'

export interface SttService {
    transcribe(audio: Blob): Promise<SttResult>
    dispose?(): void
}