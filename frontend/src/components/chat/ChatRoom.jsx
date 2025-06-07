import { useNavigate, useParams } from "react-router-dom";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import SendIcon from "@mui/icons-material/Send";
import useMessagesList from "@/hooks/chat/useMessagesList";
import CircularProgress from "@mui/material/CircularProgress";
import { useRef, useEffect, useCallback, useMemo, memo } from "react";
import MarkdownChat from "@/components/chat/MarkdownChat";
import SendChat from "@/components/chat/SendChat";
import MovieRecommend from "@/components/layout/MovieRecommend";
import MenuOpenIcon from "@mui/icons-material/MenuOpen";
import ServerMessage from "@/components/chat/ServerMessage";
import useChatroomStore from "@/stores/useChatroomStore";
import {
  useChatMessageSend,
  useTypingAnimation,
  useAutoScroll,
} from "@/hooks/chat/useChatroom";

// 메모이제이션된 메시지 컴포넌트
const MemoizedMessage = memo(({ msg }) => (
  <div className="flex flex-col gap-8 max-w-[600px]">
    {msg.user_message && <SendChat message={msg.user_message} />}
    {msg.ai_message && (
      <span className="p-3 rounded-lg">
        <MarkdownChat>{msg.ai_message}</MarkdownChat>
      </span>
    )}
    {msg.timestamp && (
      <div className="text-xs text-gray-400 mt-2">
        {new Date(msg.timestamp).toLocaleString("ko-KR", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })}
      </div>
    )}
  </div>
));

const ChatRoom = () => {
  // Zustand store
  const {
    writeMessage,
    sendMessage,
    streamingMessage,
    isStreaming,
    serverStatus,
    isMovieRecommendOpen,
    setWriteMessage,
    setIsMovieRecommendOpen,
    clearTokenQueue,
  } = useChatroomStore();

  // 라우팅
  const navigate = useNavigate();
  const { chatId } = useParams();

  // 컴포넌트 레퍼런스
  const containerRef = useRef(null);

  // 서버 상태 fetch
  const { data: messages, isLoading } = useMessagesList(chatId);

  // 커스텀 훅
  const sendChatMessage = useChatMessageSend(chatId);
  useTypingAnimation();

  // 자동 스크롤 - 개별 dependency로 전달
  const { messagesEndRef } = useAutoScroll(
    messages,
    sendMessage,
    streamingMessage,
    isStreaming
  );

  // 메시지 전송 핸들러
  const handleSendMessage = useCallback(() => {
    sendChatMessage();
  }, [sendChatMessage]);

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
      clearTokenQueue();
    };
  }, [clearTokenQueue]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <CircularProgress />
      </div>
    );
  }

  return (
    <div className="flex flex-1 bg-white h-full w-full">
      {/* 메인 채팅 영역 */}
      <div className="flex flex-col w-full">
        {/* 북마크 버튼 */}
        <div className="flex justify-end p-6">
          <button
            onClick={() => navigate("/history")}
            className="flex items-center gap-2 px-4 py-2 mr-4 border border-gray-200 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition"
          >
            <BookmarkBorderIcon className="w-5 h-5" />
            <span className="text-sm font-medium">북마크</span>
          </button>
          {!isMovieRecommendOpen && (
            <button
              onClick={() => setIsMovieRecommendOpen(true)}
              className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition"
            >
              <MenuOpenIcon className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* 채팅 메시지 영역 */}
        {messages?.length > 0 || isStreaming ? (
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
                {streamingMessage && (
                  <div className="p-3 rounded-lg opacity-90 animate-pulse border-gray-200 shadow-md transition-all duration-200">
                    <MarkdownChat>{streamingMessage}</MarkdownChat>
                  </div>
                )}

                {/* 서버 프로세싱 안내 메시지 */}
                <ServerMessage status={serverStatus} />

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center mt-auto">
            <div className="mb-8 text-2xl text-gray-700 font-semibold">
              {"영화에 대해 궁금한게 있으신가요?"}
            </div>
          </div>
        )}

        {/* 하단 입력창 */}
        <div
          className={`w-full border-t border-gray-100 bg-white ${
            messages?.length === 0 && !isStreaming ? "mb-auto" : ""
          }
          }`}
        >
          <div className="px-4 py-6">
            <div className="max-w-[700px] mx-auto">
              <div className="relative flex items-center gap-3 bg-gray-50 rounded-2xl px-1 py-1 shadow-sm border border-gray-100 transition-all duration-200 hover:shadow-md focus-within:shadow-md focus-within:border-gray-200">
                <textarea
                  value={writeMessage}
                  onChange={(e) => setWriteMessage(e.target.value)}
                  onKeyDown={handleKeyPress}
                  className="
                    flex-1 bg-transparent px-5 py-4 text-base placeholder:text-gray-400
                    focus:outline-none resize-none overflow-y-auto
                  "
                  placeholder="영화에 대해 무엇이든 물어보세요..."
                  disabled={isStreaming}
                />
                <button
                  className={`
                    flex items-center justify-center
                    bg-gray-900 text-white 
                    rounded-xl p-3 mr-1
                    transition-all duration-200
                    ${
                      isStreaming
                        ? "opacity-50 cursor-not-allowed"
                        : "hover:bg-black hover:scale-105 active:scale-95"
                    }
                  `}
                  onClick={handleSendMessage}
                  disabled={isStreaming}
                >
                  {isStreaming ? (
                    <CircularProgress size={20} className="text-white" />
                  ) : (
                    <SendIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
              <div className="flex items-center justify-between mt-3 px-2">
                <p className="text-xs text-gray-400 ml-2">
                  Enter로 전송, Shift+Enter로 줄바꿈
                </p>
              </div>
            </div>
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
          <MovieRecommend
            onClose={() => setIsMovieRecommendOpen(false)}
            chatroomId={chatId}
          />
        )}
      </div>
    </div>
  );
};

export default ChatRoom;
