// ~/utils/audio/streamingPlayer.ts
import { VoiceError } from '~/types/voice'


export class StreamingAudioPlayer {
    private audioContext: AudioContext | null = null
    private gainNode: GainNode | null = null
    private nextStartTime: number = 0
    private isStarted: boolean = false
    private bufferQueue: AudioBuffer[] = []
    private isProcessing: boolean = false
    private scheduledSources: AudioBufferSourceNode[] = []

    get isInitialized(): boolean {
        return this.audioContext !== null
    }

    async init(): Promise<void> {
        if (this.audioContext) return

        this.audioContext = new AudioContext()
        this.gainNode = this.audioContext.createGain()
        this.gainNode.connect(this.audioContext.destination)
        this.gainNode.gain.value = 1.0

        this.nextStartTime = this.audioContext.currentTime + 0.1
    }

    
    async appendChunk(base64Chunk: string): Promise<void> {
        if (!base64Chunk || base64Chunk.trim() === '') return
        if (!this.audioContext) {
            await this.init()
        }

        const audioBuffer = await this.decodeBase64ToAudioBuffer(base64Chunk)
        this.bufferQueue.push(audioBuffer)
        
        if (!this.isProcessing) {
            this.schedulePlayback()
        }
    }

    private async decodeBase64ToAudioBuffer(base64: string): Promise<AudioBuffer> {
        if (!this.audioContext) {
            throw new VoiceError('AudioContext не инициализирован', 'PLAYBACK_FAILED')
        }

        const binaryString = atob(base64)
        const bytes = new Uint8Array(binaryString.length)
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i)
        }

        try {
            const audioBuffer = await this.audioContext.decodeAudioData(bytes.buffer)
            return audioBuffer
        } catch (e) {
            throw new VoiceError('Не удалось декодировать аудио-чанк', 'PLAYBACK_FAILED')
        }
    }

   
    private schedulePlayback(): void {
        if (!this.audioContext || !this.gainNode) return

        this.isProcessing = true

        while (this.bufferQueue.length > 0) {
            const buffer = this.bufferQueue.shift()
            if (!buffer) continue

            const source = this.audioContext.createBufferSource()
            source.buffer = buffer
            source.connect(this.gainNode)

            const startTime = Math.max(this.nextStartTime, this.audioContext.currentTime + 0.05)
            
            source.start(startTime)
            this.scheduledSources.push(source)

            this.nextStartTime = startTime + buffer.duration

            source.onended = () => {
                const idx = this.scheduledSources.indexOf(source)
                if (idx > -1) this.scheduledSources.splice(idx, 1)
            }
        }

        this.isProcessing = false
    }

    stop(): void {
        this.scheduledSources.forEach(source => {
            source.stop()
            source.disconnect()
        })
        this.scheduledSources = []

        this.bufferQueue = []

        if (this.audioContext) {
            this.nextStartTime = this.audioContext.currentTime + 0.1
        }

        this.isProcessing = false
    }

    dispose(): void {
        this.stop()
        
        if (this.gainNode) {
            this.gainNode.disconnect()
            this.gainNode = null
        }
        
        if (this.audioContext) {
            this.audioContext.close()
            this.audioContext = null
        }
    }

    get isPlaying(): boolean {
        if (!this.audioContext) return false
        return this.nextStartTime > this.audioContext.currentTime || this.isProcessing
    }
}