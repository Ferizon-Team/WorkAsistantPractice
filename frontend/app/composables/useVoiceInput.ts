import { ref , computed } from 'vue'
import { useAudioRecorder } from './useAudioRecorder'
import { useStt } from './useStt'
import { VoiceError } from '~/types/voice'

export function useVoiceInput() {
    const toast = useToast()
    const recorder = useAudioRecorder()
    const stt = useStt()

    const isBusy = computed(() => recorder.isRecording.value || stt.isProcessing.value)

    async function toggleRecording(): Promise<string | null> {
        if (recorder.isRecording.value) {
            try {
                console.log('Stopping recording...')
                const blob = await recorder.stopRecording()
                console.log('Blob size:', blob.size, 'type:', blob.type)
                
                console.log('Starting STT...')
                const text = await stt.transcribe(blob)
                console.log('STT result:', text)
                
                return text
            } catch (e) {
                console.error('Voice input error:', e)
                const msg = e instanceof VoiceError ? e.message : 'Не удалось распознать аудио'
                toast.add({ title: 'STT', description: msg, color: 'error' })
                return null
            }
        }
        try {
            console.log('Starting recording...')
            await recorder.startRecording()
            return null
        } catch (e) {
            console.error('Recording error:', e)
            const msg = e instanceof VoiceError ? e.message : 'Не удалось начать запись'
            toast.add({ title: 'Audio Recorder', description: msg, color: 'error' })
            return null
        }
    }

    return {
        isRecording: recorder.isRecording,
        isBusy,
        toggleRecording,
        cancelRecording: recorder.cancelRecording,
    }
}