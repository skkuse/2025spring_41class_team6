import { useNavigate, useParams } from "react-router-dom";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import SendIcon from "@mui/icons-material/Send";
import useMessagesList from "@/hooks/chat/useMessagesList";
import CircularProgress from "@mui/material/CircularProgress";
import { useState, useRef, useEffect, useCallback, useMemo, memo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import fetchChatSSE from "@/apis/chat/fetchchatSSE";
import MarkdownChat from "@/components/chat/MarkdownChat";
import SendChat from "@/components/chat/SendChat";
import MovieRecommend from "@/components/layout/MovieRecommend";
import MenuOpenIcon from "@mui/icons-material/MenuOpen";

// 메모이제이션된 메시지 컴포넌트
const MemoizedMessage = memo(({ msg }) => (
  <div className="flex flex-col gap-8 max-w-[600px]">
    {msg.user_message && <SendChat message={msg.user_message} />}
    {msg.ai_message && (
      <span className="p-3 rounded-lg">
        <MarkdownChat>{msg.ai_message}</MarkdownChat>
      </span>
    )}
  </div>
));

const ChatRoom = () => {
  const [message, setMessage] = useState("");
  const [sendMessage, setSendMessage] = useState("");
  const [displayedMessage, setDisplayedMessage] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const queryClient = useQueryClient();
  const tokenQueue = useRef([]);
  const animationFrameId = useRef(null);
  const lastScrollTime = useRef(0);
  const [isMovieRecommendOpen, setIsMovieRecommendOpen] = useState(false);

  const navigate = useNavigate();
  const { chatId } = useParams();
  const { data: messages, isLoading } = useMessagesList(chatId);
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);

  const getRandomTypingDelay = useCallback(() => {
    const randomVariation = Math.random();
    if (randomVariation < 0.4) return 20;
    else if (randomVariation < 0.85) return 70;
    else return 150;
  }, []);

  // 스크롤 최적화 - debounce와 requestAnimationFrame 사용
  const scrollToBottom = useCallback(() => {
    const now = Date.now();
    if (now - lastScrollTime.current < 100) return; // 100ms 디바운스

    lastScrollTime.current = now;
    if (animationFrameId.current) {
      cancelAnimationFrame(animationFrameId.current);
    }

    animationFrameId.current = requestAnimationFrame(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    });
  }, []);

  // 타이핑 애니메이션 최적화
  useEffect(() => {
    if (!isStreaming) return;

    let animationId;
    let lastTime = 0;

    const animate = (currentTime) => {
      if (currentTime - lastTime >= getRandomTypingDelay()) {
        if (tokenQueue.current.length > 0) {
          // 한 번에 여러 토큰 처리하여 성능 개선
          const tokensToAdd = tokenQueue.current.splice(
            0,
            Math.min(3, tokenQueue.current.length)
          );
          setDisplayedMessage((prev) => prev + tokensToAdd.join(""));
        }
        lastTime = currentTime;
      }

      if (isStreaming || tokenQueue.current.length > 0) {
        animationId = requestAnimationFrame(animate);
      }
    };

    animationId = requestAnimationFrame(animate);

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
    };
  }, [isStreaming, getRandomTypingDelay]);

  // 스크롤 이벤트 최적화 - 의존성 분리
  useEffect(() => {
    scrollToBottom();
  }, [messages?.length, scrollToBottom]);
  // 임시 메시지 전송 시 스크롤
  useEffect(() => {
    if (sendMessage) {
      scrollToBottom();
    }
  }, [sendMessage, scrollToBottom]);

  // 스트리밍 중일 때만 스크롤
  useEffect(() => {
    if (isStreaming && displayedMessage) {
      scrollToBottom();
    }
  }, [displayedMessage, isStreaming, scrollToBottom]);

  // 메시지 전송 - ref를 사용하여 최신 값 참조
  const messageRef = useRef(message);
  messageRef.current = message;

  const handleSendMessage = useCallback(async () => {
    const currentMessage = messageRef.current;
    if (currentMessage.trim() && !isStreaming) {
      setSendMessage(currentMessage);
      setDisplayedMessage("");
      setIsStreaming(true);
      setMessage("");
      tokenQueue.current = [];

      try {
        await fetchChatSSE(
          chatId,
          currentMessage,
          async (token) => {
            tokenQueue.current.push(token);
          },
          async () => {
            setSendMessage("");
            setDisplayedMessage("");
            setIsStreaming(false);
            // 배치 업데이트로 리렌더링 최소화
            queryClient.invalidateQueries(["messagesList", chatId]);
          },
          (err) => {
            setIsStreaming(false);
            setSendMessage("");
            setDisplayedMessage("");
            alert("에러! " + err.message);
          }
        );
      } catch (error) {
        console.error("Failed to send message:", error);
        setIsStreaming(false);
        setSendMessage("");
        setDisplayedMessage("");
      }
    }
  }, [isStreaming, chatId, queryClient]); // message 의존성 제거

  // handleKeyPress를 독립적으로 만들어 재생성 방지
  const handleKeyPress = useCallback(
    (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    },
    [handleSendMessage]
  );

  // 메시지 리스트 메모이제이션
  const messagesList = useMemo(
    () =>
      messages?.map((msg, idx) => (
        <MemoizedMessage
          key={`${msg.id || idx}-${msg.timestamp || ""}`}
          msg={msg}
        />
      )),
    [messages]
  );

  // Cleanup
  useEffect(() => {
    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
      tokenQueue.current = [];
    };
  }, []);

  return (
    <div className="flex bg-white h-full w-full">
      {/* 메인 채팅 영역 */}
      <div className=" flex flex-col w-full">
        {/* 북마크 버튼 */}
        <div className="flex justify-end p-6">
          <button
            onClick={() => navigate("/history")}
            className="flex items-center gap-2 px-4 py-2 mr-4 border border-gray-200 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition"
          >
            <BookmarkBorderIcon className="w-5 h-5" />
            <span className="text-sm font-medium">북마크</span>
          </button>
          <button
            onClick={() => setIsMovieRecommendOpen(true)}
            className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition"
          >
            <MenuOpenIcon className="w-5 h-5" />
          </button>
        </div>

        {/* 채팅 메시지 영역 */}
        <div ref={containerRef} className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <CircularProgress />
            </div>
          ) : (
            <div className="flex flex-col gap-8 w-[600px] mx-auto p-4">
              {/* 메모이제이션된 메시지 리스트 */}
              {messagesList}

              {/* 임시 메시지: 내가 막 보낸 것 */}
              {sendMessage && <SendChat message={sendMessage} />}

              {/* 스트리밍 중인 메시지 */}
              {displayedMessage && (
                <div className="p-3 rounded-lg opacity-90 animate-pulse border-gray-200 shadow-md transition-all duration-200">
                  <MarkdownChat>{displayedMessage}</MarkdownChat>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* 하단 입력창 */}
        <div className="w-full border-t border-[#ececec] p-4 flex items-center justify-center bg-white mb-4">
          <div className="w-[600px] flex items-center">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              className="flex-1 border border-[#ececec] rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-100"
              placeholder="메시지를 입력하세요..."
              disabled={isStreaming}
            />
            <button
              className="ml-2 bg-black text-white rounded-md p-2 hover:bg-gray-800 transition"
              onClick={handleSendMessage}
              disabled={isStreaming}
            >
              <SendIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* 영화 추천 사이드바 */}
      <div
        className={`h-full transition-all duration-300 ease-in-out ${
          isMovieRecommendOpen ? "w-120 opacity-100" : "w-0 opacity-0"
        }`}
      >
        {isMovieRecommendOpen && (
          <MovieRecommend onClose={() => setIsMovieRecommendOpen(false)} />
        )}
      </div>
    </div>
  );
};

export default ChatRoom;
