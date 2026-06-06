import { ref } from 'vue'
import { MicrophoneRecorder } from '~/utils/audio/microphone'
import type { VoiceServiceStatus} from '~/types/voice'
import { VoiceError } from '~/types/voice'

export function useAudioRecorder() {
    const status = ref<VoiceServiceStatus>('idle')
    const error = ref<VoiceError | null>(null)
    const recorder = new MicrophoneRecorder()

    async function startRecording() {
        error.value = null
        status.value = 'recording'
        
        try {
            await recorder.start()

        } catch (e) {
            status.value = 'error'
            error.value = e instanceof VoiceError ? e : new VoiceError('Ошибка записи', 'RECORD_FAILED')
            throw e
        }
    }

    async function stopRecording(): Promise<Blob> {
        try {
            const blob = await recorder.stop()
            status.value = 'idle'
            return blob
        } catch (e) {
            status.value = 'error'
            error.value = e instanceof VoiceError ? e : new VoiceError('Ошибка записи', 'RECORD_FAILED')
            throw e
        }
    }

    function cancelRecording() {
        recorder.cancel()
        status.value = 'idle'
    }

    const isRecording = computed(() => status.value === 'recording')

    return { status, error, startRecording, stopRecording, cancelRecording, isRecording }

}