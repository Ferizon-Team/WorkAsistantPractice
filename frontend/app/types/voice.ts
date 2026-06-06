export type VoiceServiceStatus = 'idle' | 'recording' | 'processing' | 'playing' | 'error'

export interface SttResult {
  text: string
  confidence?: number
  isFinal?: boolean
}

export interface TtsResult {
  audio: Blob
  mimeType: string
}

export class VoiceError extends Error {
  constructor(
    message: string,
    public readonly code:
      | 'MIC_DENIED'
      | 'MIC_UNAVAILABLE'
      | 'RECORD_FAILED'
      | 'STT_FAILED'
      | 'TTS_FAILED'
      | 'PLAYBACK_FAILED'
      | 'WS_DISCONNECTED'
  ) {
    super(message)
    this.name = 'VoiceError'
  }
}