import { create } from "zustand";

const useChatroomStore = create((set, get) => ({
  // 채팅방 상태
  chatroomId: null,
  writeMessage: "",
  sendMessage: "",
  streamingMessage: "",
  isStreaming: false,
  serverStatus: 0,
  isMovieRecommendOpen: false,

  // 내부 상태 (UI 관련)
  tokenQueue: [],

  // Actions
  setChatroomId: (chatroomId) => set({ chatroomId }),
  setWriteMessage: (writeMessage) => set({ writeMessage }),
  setSendMessage: (sendMessage) => set({ sendMessage }),
  setStreamingMessage: (streamingMessage) => set({ streamingMessage }),
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  setServerStatus: (serverStatus) => set({ serverStatus }),
  setIsMovieRecommendOpen: (isMovieRecommendOpen) =>
    set({ isMovieRecommendOpen }),

  // 토큰 큐 관련
  addToTokenQueue: (tokens) =>
    set((state) => ({
      tokenQueue: [...state.tokenQueue, ...tokens],
    })),
  clearTokenQueue: () => set({ tokenQueue: [] }),
  popTokens: (count = 3) => {
    const state = get();
    const tokenQueue = [...state.tokenQueue];
    const tokens = tokenQueue.splice(0, Math.min(count, tokenQueue.length));
    set({ tokenQueue });
    return tokens;
  },

  // 스트리밍 메시지 추가
  appendToStreamingMessage: (text) =>
    set((state) => ({
      streamingMessage: state.streamingMessage + text,
    })),

  // 메시지 전송 준비
  prepareMessageSend: (message) => {
    set({
      sendMessage: message,
      streamingMessage: "",
      isStreaming: true,
      writeMessage: "",
      tokenQueue: [],
      serverStatus: 2,
    });
  },

  // 메시지 전송 완료
  completeMessageSend: () => {
    set({
      sendMessage: "",
      streamingMessage: "",
      isStreaming: false,
      tokenQueue: [],
      serverStatus: 0,
    });
  },

  // 메시지 전송 완료 with 콜백
  completeMessageSendWithCallback: (callback) => {
    set({
      sendMessage: "",
      streamingMessage: "",
      isStreaming: false,
      tokenQueue: [],
      serverStatus: 0,
    });
    callback && callback();
  },

  // 에러 처리
  handleError: () => {
    set({
      isStreaming: false,
      sendMessage: "",
      streamingMessage: "",
      tokenQueue: [],
      serverStatus: 4,
    });
  },

  // 채팅방 변경 시 초기화
  resetChatroom: () => {
    set({
      writeMessage: "",
      sendMessage: "",
      streamingMessage: "",
      isStreaming: false,
      serverStatus: 0,
      tokenQueue: [],
      isMovieRecommendOpen: false,
    });
  },

  // 전체 초기화
  resetAll: () => {
    set({
      chatroomId: null,
      writeMessage: "",
      sendMessage: "",
      streamingMessage: "",
      isStreaming: false,
      serverStatus: 3,
      tokenQueue: [],
      isMovieRecommendOpen: false,
    });
  },
}));

export default useChatroomStore;
