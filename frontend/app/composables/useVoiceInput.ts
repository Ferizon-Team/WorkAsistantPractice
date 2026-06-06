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
                const blob = await recorder.stopRecording()
                return await stt.transcribe(blob)

            }catch (e) {
                const msg = e instanceof VoiceError ? e.message : 'Не удалось распознать аудио'
                toast.add({ title: 'STT', description: msg, color: 'error' })
                return null
            }
        }
        try {
            await recorder.startRecording()
            return null
        } catch (e) {
            const msg = e instanceof VoiceError ? e.message : 'Не удалось начать запись'
            toast.add({ title: 'Audio Recorder', description: msg, color: 'error' })
            return null
        }
    }

    return { isRecording: recorder.isRecording, isBusy, toggleRecording, cancelRecording: recorder.cancelRecording }
}