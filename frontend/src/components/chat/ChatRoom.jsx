import { useNavigate } from "react-router-dom";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import SendIcon from "@mui/icons-material/Send";
const ChatRoom = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-1 flex-col bg-white h-full">
      {/* 북마크 버튼 */}
      <div className="flex justify-end p-6">
        <button
          onClick={() => navigate("/bookmark")}
          className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition"
        >
          <BookmarkBorderIcon className="w-5 h-5" />
          <span className="text-sm font-medium">북마크</span>
        </button>
      </div>
      {/* 채팅 메시지 영역 (임시 비움) */}
      <div className="flex-1" />
      {/* 하단 입력창 */}
      <div className="w-full border-t border-[#ececec] p-4 flex items-center justify-center bg-white mb-4">
        <div className="w-3/4 flex items-center">
          <input
            type="text"
            className="flex-1 border border-[#ececec] rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-100"
            placeholder="메시지를 입력하세요..."
          />
          <button className="ml-2 bg-black text-white rounded-md p-2 hover:bg-gray-800 transition">
            <SendIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatRoom;
