import { useNavigate, useParams } from "react-router-dom";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import SendIcon from "@mui/icons-material/Send";
import useMessagesList from "@/hooks/chat/useMessagesList";
import CircularProgress from "@mui/material/CircularProgress";
import { useState, useRef, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

// --- (1) 버퍼링 + slice 방식 타이핑 애니메이션 구현 ---
const TYPING_DELAY = 200; // ms

const ChatRoom = () => {
  const [message, setMessage] = useState("");
  const [sendMessage, setSendMessage] = useState("");
  const [fullReceiveMessage, setFullReceiveMessage] = useState(""); // 누적된 실제 답변(전체)
  const [displayedMessage, setDisplayedMessage] = useState(""); // 화면에 보여줄 (천천히 늘어남)
  const [isStreaming, setIsStreaming] = useState(false);
  const queryClient = useQueryClient();
  const tokenQueue = useRef([]); // ← 토큰 큐

  const navigate = useNavigate();
  const { chatId } = useParams();
  const { data: messages, isLoading } = useMessagesList(chatId);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (!isStreaming) return;
    let stopped = false;

    function typeNext() {
      if (stopped) return;
      if (tokenQueue.current.length > 0) {
        const token = tokenQueue.current.shift();
        setDisplayedMessage((prev) => prev + token);
        setTimeout(typeNext, TYPING_DELAY);
      }
    }
    typeNext();

    return () => {
      stopped = true;
    };
  }, [isStreaming]);

  // 스크롤 항상 맨 아래로
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sendMessage, displayedMessage, isStreaming]);

  // SSE fetch 함수
  const fetchChatSSE = async (roomId, content, onDone, onError) => {
    try {
      const response = await fetch(
        `/api/chatrooms/${roomId}/messages?stream=true`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content }),
        }
      );

      if (!response.body) throw new Error("No stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let done = false;

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");
          for (let line of lines) {
            if (line.startsWith("data: ")) {
              const token = line.replace("data: ", "");
              tokenQueue.current.push(token);
            }
          }
        }
      }
      onDone && onDone();
    } catch (err) {
      onError && onError(err);
    }
  };

  // 메시지 전송
  const handleSendMessage = async () => {
    if (message.trim() && !isStreaming) {
      setSendMessage(message);
      setDisplayedMessage(""); // 화면 초기화
      setIsStreaming(true);
      setMessage("");
      tokenQueue.current = []; // 새로 시작할 때 큐 비우기

      await fetchChatSSE(
        chatId,
        message,
        async () => {
          setSendMessage("");
          setFullReceiveMessage("");
          setTimeout(() => setDisplayedMessage(""), 400); // 애니메이션 잔상 살짝 유지
          setIsStreaming(false);
          await queryClient.invalidateQueries(["chatMessages", chatId]);
        },
        (err) => {
          setIsStreaming(false);
          setSendMessage("");
          setDisplayedMessage("");
          alert("에러! " + err.message);
        }
      );
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-1 flex-col bg-white h-full">
      {/* 북마크 버튼 */}
      <div className="flex justify-end p-6">
        <button
          onClick={() => navigate("/history")}
          className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition "
        >
          <BookmarkBorderIcon className="w-5 h-5" />
          <span className="text-sm font-medium">북마크</span>
        </button>
      </div>
      {/* 채팅 메시지 영역 */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <CircularProgress />
          </div>
        ) : (
          <div className="flex flex-col gap-8 w-140 mx-auto p-4">
            {messages.map((msg, idx) => (
              <div key={idx} className="flex flex-col gap-8 max-w-[600px]">
                {msg.user_message && (
                  <span className="text-left bg-gray-100 p-3 rounded-lg">
                    {msg.user_message}
                  </span>
                )}
                {msg.ai_message && (
                  <span className="text-right bg-blue-100 p-3 rounded-lg">
                    {msg.ai_message}
                  </span>
                )}
              </div>
            ))}
            {/* 임시 메시지: 내가 막 보낸 것 */}
            {sendMessage && (
              <span className="text-left bg-gray-200 p-3 rounded-lg opacity-70 animate-pulse">
                {sendMessage}
              </span>
            )}
            {/* 스트리밍 중인 메시지: LLM 답변 (애니메이션) */}
            {displayedMessage && (
              <span className="text-right bg-blue-200 p-3 rounded-lg opacity-90 animate-pulse border border-blue-400 shadow-md transition-all duration-200">
                {displayedMessage}
                {/* 커서 애니메이션 효과 */}
                <span className="inline-block w-2 h-5 align-middle bg-blue-400 animate-blink ml-1 rounded-sm" />
              </span>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      {/* 하단 입력창 */}
      <div className="w-full border-t border-[#ececec] p-4 flex items-center justify-center bg-white mb-4">
        <div className="w-3/4 flex items-center">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
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
      {/* 블링크 커서 애니메이션 keyframes */}
      <style>
        {`
        @keyframes blink {
          0% { opacity: 1 }
          50% { opacity: 0.2 }
          100% { opacity: 1 }
        }
        .animate-blink {
          animation: blink 1s steps(1) infinite;
        }
        `}
      </style>
    </div>
  );
};

export default ChatRoom;
