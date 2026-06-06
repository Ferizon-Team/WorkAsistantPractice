import type { TtsResult } from '~/types/voice'

export interface TtsService {
    synthesize(text: string): Promise<TtsResult>
    dispose?(): void
}