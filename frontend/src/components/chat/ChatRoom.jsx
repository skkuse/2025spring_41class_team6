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
    resetChatroom,
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

  // 자동 스크롤 - 의존성 배열에 필요한 값들 추가
  const { messagesEndRef } = useAutoScroll([
    messages?.length,
    sendMessage,
    streamingMessage && isStreaming,
  ]);

  // chatId 변경 시 상태 초기화
  useEffect(() => {
    resetChatroom();
  }, [chatId, resetChatroom]);

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

              {/* 서버 프로세싱 안내 메시지 */}
              <ServerMessage status={serverStatus} />

              {/* 스트리밍 중인 메시지 */}
              {streamingMessage && (
                <div className="p-3 rounded-lg opacity-90 animate-pulse border-gray-200 shadow-md transition-all duration-200">
                  <MarkdownChat>{streamingMessage}</MarkdownChat>
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
              value={writeMessage}
              onChange={(e) => setWriteMessage(e.target.value)}
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
