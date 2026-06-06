import { VoiceError } from '~/types/voice'

export class AudioPlayer {
    private audio: HTMLAudioElement | null = null

    async play(blob: Blob): Promise<void> {
        this.stop()
        const url = URL.createObjectURL(blob)
        this.audio = new Audio(url)

        return new Promise((resolve, reject) => {
            if (!this.audio) return reject(new VoiceError('Плеер не создан', 'PLAYBACK_FAILED'))

            this.audio.onended = () => {
                URL.revokeObjectURL(url)
                resolve()
            }
            this.audio.onerror = () => {
                URL.revokeObjectURL(url)
                reject(new VoiceError('Не удалось воспроизвести', 'PLAYBACK_FAILED'))
            }
            void this.audio.play().catch(() => {
                URL.revokeObjectURL(url)
                reject(new VoiceError('Воспроизведение заблокировано', 'PLAYBACK_FAILED'))
            })
        })
    }

    stop(): void {
        if (!this.audio) return
        this.audio.pause()
        this.audio.src = ''
        this.audio = null
    }

    get isPlaying(): boolean {
        return !!this.audio && !this.audio.paused
    }
}