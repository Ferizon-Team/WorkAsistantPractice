import { ref, reactive, onUnmounted, toRefs } from 'vue'
import type { RagChunk, StreamContentAnswer } from '~/types/chat'


interface RagStreamState {
    isConnected: boolean;
    isStreaming: boolean;
    chunks: string[];
    audioChunks: string[];
    fullAnswer: string;
}

export function useRagStream() {
    const config = useRuntimeConfig()
    const ws = ref<WebSocket | null>(null)
     const state = reactive<RagStreamState>({
        isConnected: false,
        isStreaming: false,
        chunks: [] as string[],
        audioChunks: [] as string[],
        fullAnswer: '',
    })

    function connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            if (ws.value?.readyState === WebSocket.OPEN) {
                resolve()
                return
            }

            const wsUrl = (config.public.apiUrl as string)
                .replace('http://', 'ws://')
                .replace('https://', 'wss://')

            const socket = new WebSocket(`${wsUrl}/api/v1/document/ws`)

            socket.onopen = () => {
                state.isConnected = true
                ws.value = socket
                resolve()
            }

            socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) as RagChunk
                    
                    switch (data.event) {
                        case 'llm.start':
                            if (state.isStreaming) {
                                break
                            }
                            state.chunks = []
                            state.audioChunks = []
                            state.fullAnswer = ''
                            state.isStreaming = true
                            break
                            
                        case 'llm.token':
                            if (data.content && typeof data.content === 'object') {
                                const content = data.content as StreamContentAnswer
                                
                                if (content.text) {
                                    state.chunks.push(content.text)
                                    state.fullAnswer += content.text
                                }
                                
                                if (content.media) {
                                    state.audioChunks.push(content.media)
                                }
                            } else if (typeof data.content === 'string') {
                                state.chunks.push(data.content)
                                state.fullAnswer += data.content
                            }
                            break
                            
                        case 'llm.finish':
                        case 'llm.done':
                            state.isStreaming = false
                            break

                        case 'search.not_found':
                            state.isStreaming = false
                            if (typeof data.content === 'string') {
                                state.fullAnswer = data.content
                            } else if (data.content && typeof data.content === 'object') {
                                state.fullAnswer = (data.content as StreamContentAnswer).text || 'Информация не найдена'
                            } else {
                                state.fullAnswer = 'Информация не найдена'
                            }
                            break
                            
                        case 'llm.error':
                            state.isStreaming = false
                            console.error('RAG error:', data.content)
                            break
                    }
                } catch (e) {
                    console.error('WS parse error:', e, event.data)
                }
            }

            socket.onerror = (error) => {
                console.error('WS error:', error)
                state.isConnected = false
                reject(error)
            }

            socket.onclose = () => {
                state.isConnected = false
                ws.value = null
            }
        })
    }

    async function ask(question: string): Promise<void> {
        if (state.isStreaming) {
            console.warn('Already streaming, ignoring duplicate ask()')
            return
        }
        await connect()

        if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
            throw new Error('WebSocket not connected')
        }

        state.chunks = []
        state.fullAnswer = ''
        state.isStreaming = true

        ws.value.send(JSON.stringify({
            event: 'question',
            question,
        }))
    }

    function disconnect() {
        ws.value?.close()
        ws.value = null
        state.isConnected = false
    }

    onUnmounted(() => disconnect())

    return {
        ...toRefs(state),
        connect,
        disconnect,
        ask,
    }
}