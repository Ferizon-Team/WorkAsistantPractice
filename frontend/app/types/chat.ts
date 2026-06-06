export type MessageRole = 'user' | 'assistant';

export interface ChatSource {
    title: string;
    snippet: string;
    similarity: number;
}

export interface RagAnswerResponse {
    answer: string;
    sources: ChatSource[];
    confidence: number;
    context_used: number;
}

export interface ChatMessage {
    id: string;
    role: MessageRole;
    content: string;
    createdAt: Date;
    sources?: ChatSource[];
    pending?: boolean;
}

export function createMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}


export function assistantMessageFromRag(response: RagAnswerResponse, id = createMessageId()): ChatMessage {
    return {
        id,
        role: 'assistant',
        content: response.answer,
        sources: response.sources.length > 0 ? response.sources : undefined,
        createdAt: new Date(),
        pending: false
    }
}

export function userMessageFromText(text: string, id = createMessageId()): ChatMessage {
    return {
        id,
        role: 'user',
        content: text.trim(),
        createdAt: new Date(),
    }
}

