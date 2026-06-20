import type { TtsService } from './tts.types'
import type { TtsResult } from '~/types/voice'

export function createStubTtsService(): TtsService {
    return {
        async synthesize(text: string): Promise<TtsResult> {
            await new Promise((r)=>setTimeout(r, 500))
            if ('speechSynthesis' in window) {
                await speakWithBrowser(text)
            }
            return {
                audio: new Blob([], { type: 'audio/wav' }),
                mimeType: 'audio/wav',
            }
        }
    }
}

function speakWithBrowser(text: string): Promise<void> {
    return new Promise((resolve) => {
        const u = new SpeechSynthesisUtterance(text)
        u.lang = 'ru-RU'
        u.onend = () => resolve()
        u.onerror = () => resolve()
        speechSynthesis.speak(u)  
    })
}