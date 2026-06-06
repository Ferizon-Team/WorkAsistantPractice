import { VoiceError } from '@/types/voice'

export interface RecorderOptions {
  mimeType?: string
  timesliceMs?: number
}

export class MicrophoneRecorder {

    private stream: MediaStream | null = null
    private mediaRecorder: MediaRecorder | null = null
    private chunks: Blob[] = []

    async start(options: RecorderOptions = {}): Promise<void> {
        if (!navigator.mediaDevices?.getUserMedia) {
            throw new VoiceError('Микрофон недоступен', 'MIC_UNAVAILABLE')
        }

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        } catch {
            throw new VoiceError('Нет доступа к микрофону', 'MIC_DENIED')
        }

        const mimeType = options.mimeType ?? pickMimeType()
        this.chunks = []

        this.mediaRecorder = new MediaRecorder(
            this.stream,
            mimeType ? { mimeType } : undefined
        )

        this.mediaRecorder.ondataavailable = (e) => {
           if (e.data.size > 0) this.chunks.push(e.data)
        }

        this.mediaRecorder.start(options.timesliceMs ?? 250)
    }

    async stop(): Promise<Blob> {
        const recorder = this.mediaRecorder
        if (!recorder || recorder.state === 'inactive') {
            throw new VoiceError('Запись не была начата', 'RECORD_FAILED')
        }

        return new Promise((resolve, reject) => {
            recorder.onstop = () => {
                const type = recorder.mimeType || 'audio/webm'
                const blob = new Blob(this.chunks, { type })
                this.cleanup()
                resolve(blob)
            }
            recorder.onerror = () => {
                this.cleanup()
                reject(new VoiceError('Ошибка записи', 'RECORD_FAILED'))
            }
            recorder.stop()
        })
    }

    cancel(): void {
        if (this.mediaRecorder?.state !== 'inactive') {
            this.mediaRecorder?.stop()
        }
        this.cleanup()
    }

    private cleanup(): void {
        this.stream?.getTracks().forEach((t) => t.stop())
        this.stream = null
        this.mediaRecorder = null
        this.chunks = []
    }
}

function pickMimeType(): string | undefined {
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
  ]
  return candidates.find((t) => MediaRecorder.isTypeSupported(t))
}