// hooks/useChatroom.js
import { useEffect, useCallback, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import useChatroomStore from "@/stores/useChatroomStore";
import fetchChatSSE from "@/apis/chat/fetchchatSSE";

// 채팅 메시지 전송 훅
export const useChatMessageSend = (chatId) => {
  const queryClient = useQueryClient();
  const { writeMessage, isStreaming, prepareMessageSend } = useChatroomStore();

  const sendMessage = useCallback(async () => {
    if (writeMessage.trim() && !isStreaming) {
      const currentMessage = writeMessage;
      prepareMessageSend(currentMessage);

      try {
        // fetchChatSSE 호출 시 완료 콜백 전달
        await fetchChatSSE(chatId, currentMessage, () => {
          // 쿼리 무효화
          queryClient.invalidateQueries(["chatroomList", chatId]);
          queryClient.invalidateQueries(["messagesList", chatId]);
          queryClient.invalidateQueries(["recommend", chatId]);
          useChatroomStore.getState().completeMessageSend();
        });
      } catch (error) {
        console.error("Failed to send message:", error);
      }
    }
  }, [writeMessage, isStreaming, chatId, queryClient, prepareMessageSend]);

  return sendMessage;
};

// 타이핑 애니메이션 훅
export const useTypingAnimation = () => {
  const { isStreaming, popTokens, appendToStreamingMessage } =
    useChatroomStore();
  const animationFrameId = useRef(null);

  const getRandomTypingDelay = useCallback(() => {
    const randomVariation = Math.random();
    if (randomVariation < 0.4) return 20;
    else if (randomVariation < 0.85) return 70;
    else return 150;
  }, []);

  useEffect(() => {
    if (!isStreaming) return;

    let lastTime = 0;

    const animate = (currentTime) => {
      if (currentTime - lastTime >= getRandomTypingDelay()) {
        const tokens = popTokens();
        if (tokens.length > 0) {
          appendToStreamingMessage(tokens.join(""));
        }
        lastTime = currentTime;
      }

      if (isStreaming || useChatroomStore.getState().tokenQueue.length > 0) {
        animationFrameId.current = requestAnimationFrame(animate);
      }
    };

    animationFrameId.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [isStreaming, getRandomTypingDelay, popTokens, appendToStreamingMessage]);
};

// 자동 스크롤 훅
export const useAutoScroll = (
  messages,
  sendMessage,
  streamingMessage,
  isStreaming
) => {
  const lastScrollTime = useRef(0);
  const animationFrameId = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    const now = Date.now();
    if (now - lastScrollTime.current < 50) return; // 스크롤 throttle을 50ms로 줄임

    lastScrollTime.current = now;
    if (animationFrameId.current) {
      cancelAnimationFrame(animationFrameId.current);
    }

    animationFrameId.current = requestAnimationFrame(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    });
  }, []);

  // 메시지 리스트 변경 시 스크롤
  useEffect(() => {
    scrollToBottom();
  }, [messages?.length, scrollToBottom]);

  // 메시지 전송 시 스크롤
  useEffect(() => {
    if (sendMessage) {
      scrollToBottom();
    }
  }, [sendMessage, scrollToBottom]);

  // 스트리밍 중일 때 스크롤 - 이 부분을 개선
  useEffect(() => {
    if (isStreaming && streamingMessage) {
      // throttle 없이 바로 스크롤
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [streamingMessage, isStreaming]);

  useEffect(() => {
    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, []);

  return { messagesEndRef, scrollToBottom };
};
