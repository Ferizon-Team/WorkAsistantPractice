import { ref, reactive, onUnmounted, toRefs } from 'vue'

export interface RagChunk {
    event: string
    content: string | null
}

export function useRagStream() {
    const config = useRuntimeConfig()
    const ws = ref<WebSocket | null>(null)
     const state = reactive({
        isConnected: false,
        isStreaming: false,
        chunks: [] as string[],
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
                            state.chunks = []
                            state.fullAnswer = ''
                            state.isStreaming = true
                            break
                            
                        case 'llm.token':
                            if (data.content) {
                                state.chunks.push(data.content)
                                state.fullAnswer += data.content
                                console.log('fullAnswer updated:', state.fullAnswer)
                            }
                            break
                            
                        case 'llm.finish':
                        case 'llm.done':
                            state.isStreaming = false
                            break

                        case 'search.not_found':
                            state.isStreaming = false
                            state.fullAnswer = data.content || 'Информация не найдена'
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