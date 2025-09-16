import { useState, useRef, useCallback } from 'react';

interface StreamResponse {
  type: 'conversation_id' | 'content' | 'complete' | 'error';
  data: any;
}

interface UseStreamingOptions {
  onComplete?: (data: { raw_content: string; formatted_content: string }) => void;
  onError?: (error: string) => void;
  onConversationId?: (conversationId: number) => void;
}

export const useStreaming = (options: UseStreamingOptions = {}) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = useCallback(async (
    message: string, 
    agentType: string = 'general_qa', 
    conversationId?: number
  ) => {
    // 重置状态
    setIsStreaming(true);
    setStreamContent('');
    setError(null);
    
    // 创建新的 AbortController
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/agents/stream-chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          agent_type: agentType,
          conversation_id: conversationId
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        
        // 处理服务器发送的事件
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 保留未完成的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData: StreamResponse = JSON.parse(line.slice(6));
              
              switch (eventData.type) {
                case 'conversation_id':
                  options.onConversationId?.(eventData.data);
                  break;
                  
                case 'content':
                  setStreamContent(prev => prev + eventData.data);
                  break;
                  
                case 'complete':
                  setIsStreaming(false);
                  options.onComplete?.(eventData.data);
                  break;
                  
                case 'error':
                  setIsStreaming(false);
                  setError(eventData.data);
                  options.onError?.(eventData.data);
                  break;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', line, e);
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // 请求被取消，不设置错误状态
        return;
      }
      
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      options.onError?.(errorMessage);
    } finally {
      setIsStreaming(false);
    }
  }, [options]);

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsStreaming(false);
  }, []);

  return {
    isStreaming,
    streamContent,
    error,
    startStream,
    stopStream
  };
};