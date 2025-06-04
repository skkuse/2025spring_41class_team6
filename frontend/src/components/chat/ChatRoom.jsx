import { useNavigate, useParams } from "react-router-dom";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import SendIcon from "@mui/icons-material/Send";
import useMessagesList from "@/hooks/chat/useMessagesList";
import CircularProgress from "@mui/material/CircularProgress";
import { useState, useRef, useEffect } from "react";
import useCreateMessage from "@/hooks/chat/useCreateMessage";

const ChatRoom = () => {
  const [message, setMessage] = useState("");
  const navigate = useNavigate();
  const { chatId } = useParams();
  const { data: messages, isLoading } = useMessagesList(chatId);
  const { mutate: createMessage } = useCreateMessage();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (message.trim()) {
      createMessage({ room_id: chatId, content: message });
      setMessage("");
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
      {/* 채팅 메시지 영역 (임시 비움) */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <CircularProgress />
          </div>
        ) : (
          <div className="flex flex-col gap-8 w-140 mx-auto p-4">
            {messages.map((message, index) => (
              <div key={index} className="flex flex-col gap-8 max-w-[600px]">
                {message.user_message && (
                  <span className="text-left bg-gray-100 p-3 rounded-lg">
                    {message.user_message}
                  </span>
                )}
                {message.ai_message && (
                  <span className="text-right bg-blue-100 p-3 rounded-lg">
                    {message.ai_message}
                  </span>
                )}
              </div>
            ))}
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
          />
          <button
            className="ml-2 bg-black text-white rounded-md p-2 hover:bg-gray-800 transition"
            onClick={handleSendMessage}
          >
            <SendIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatRoom;
