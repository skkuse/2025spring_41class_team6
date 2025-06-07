import { FaPlus, FaRegCommentDots } from "react-icons/fa";
import { useState } from "react";
import useChatroomsList from "@/hooks/chat/useChatroomsList";
import { useNavigate, useParams } from "react-router-dom";
import useChatroomStore from "@/stores/useChatroomStore";

const Sidebar = () => {
  const [mode, setMode] = useState("normal"); // "normal" 또는 "immersive"
  const navigate = useNavigate();
  const { data: chatrooms, isLoading } = useChatroomsList();
  const { chatId } = useParams();
  const { resetChatroom } = useChatroomStore();
  if (isLoading) {
    return <div>Loading...</div>;
  }

  const normalConversations = chatrooms.normal;
  const immersiveConversations = chatrooms.immersive;

  return (
    <div className="w-72 bg-[#f5f6fa] border-r border-[#ececec] p-6 flex flex-col min-h-0 rounded-r-xl">
      {/* 대화 모드 선택 탭 */}
      <div className="flex mb-6">
        <button
          className={`flex-1 py-3 rounded-t-lg ${
            mode === "normal"
              ? "bg-white text-black"
              : "bg-[#f5f6fa] text-gray-400"
          } font-semibold shadow-sm border border-b-0 border-[#ececec]`}
          onClick={() => setMode("normal")}
        >
          일반대화
        </button>
        <button
          className={`flex-1 py-3 rounded-t-lg ${
            mode === "immersive"
              ? "bg-white text-black"
              : "bg-[#f5f6fa] text-gray-400"
          } font-semibold border border-b-0 border-l-0 border-[#ececec]`}
          onClick={() => setMode("immersive")}
        >
          몰입형
        </button>
      </div>
      {/* 새 대화 버튼 */}
      <button
        onClick={() => navigate("/chat")}
        className="flex items-center justify-center gap-2 w-full py-3 mb-6 bg-white border border-[#ececec] rounded-lg text-sm font-medium hover:bg-gray-100 transition"
      >
        <FaPlus className="text-gray-500" />새 대화
      </button>
      {/* 대화 컨텍스트 목록 */}
      <div className="flex-1 overflow-y-auto">
        {(mode === "normal" ? normalConversations : immersiveConversations).map(
          (conversation) => (
            <div
              key={conversation.id}
              className={`flex items-center gap-2 px-3 py-3 rounded-lg text-gray-700 text-sm cursor-pointer hover:bg-gray-200 transition mb-2 ${
                conversation.id == chatId ? "bg-gray-200 font-medium" : ""
              }`}
              onClick={() => {
                navigate(`/chat/${conversation.id}`);
                resetChatroom();
              }}
            >
              <FaRegCommentDots className="text-lg text-gray-400" />
              {conversation.title}
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default Sidebar;
