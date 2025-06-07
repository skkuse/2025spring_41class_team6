import {
  FaPlus,
  FaRegCommentDots,
  FaEllipsisH,
  FaUser,
  FaSignOutAlt,
} from "react-icons/fa";
import { useState, useEffect } from "react";
import useChatroomsList from "@/hooks/chat/useChatroomsList";
import { useNavigate, useParams } from "react-router-dom";
import useChatroomStore from "@/stores/useChatroomStore";
import useDeleteChatroom from "@/hooks/chat/useDeleteChatroom";
import { getUserInfo } from "@/apis/auth/getUserInfo";
import { logoutUser } from "@/apis/auth/auth";
const DeleteConfirmModal = ({ isOpen, onClose, onConfirm }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-500/30 backdrop-blur-[2px] flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-80 shadow-lg">
        <h3 className="text-lg font-semibold mb-4">채팅방 삭제</h3>
        <p className="text-gray-600 mb-6">
          정말로 이 채팅방을 삭제하시겠습니까?
        </p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
          >
            취소
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            삭제
          </button>
        </div>
      </div>
    </div>
  );
};

const Sidebar = () => {
  const [mode, setMode] = useState("normal"); // "normal" 또는 "immersiveㅅ"
  const [showDeleteMenu, setShowDeleteMenu] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });
  const [hoveredChatId, setHoveredChatId] = useState(null);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const navigate = useNavigate();
  const { data: chatrooms, isLoading } = useChatroomsList();
  const { chatId } = useParams();
  const { resetChatroom } = useChatroomStore();
  const { mutate: deleteChatroom } = useDeleteChatroom();

  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        const info = await getUserInfo();
        setUserInfo(info);
      } catch (error) {
        console.error("사용자 정보 조회 실패:", error);
      }
    };
    fetchUserInfo();
  }, []);

  useEffect(() => {
    const handleClick = () => {
      setShowDeleteMenu(false);
    };

    document.addEventListener("click", handleClick);
    return () => {
      document.removeEventListener("click", handleClick);
    };
  }, []);

  const handleMoreClick = (e, conversationId) => {
    e.stopPropagation();
    const rect = e.currentTarget.getBoundingClientRect();
    setMenuPosition({ x: rect.right + 10, y: rect.top });
    setSelectedChatId(conversationId);
    setShowDeleteMenu(true);
  };

  const handleDelete = () => {
    setShowDeleteMenu(false);
    setShowDeleteModal(true);
  };

  const confirmDelete = () => {
    // TODO: 실제 삭제 로직 구현
    console.log("Deleting chat:", selectedChatId);
    console.log("Current chatId:", chatId);
    setShowDeleteModal(false);
    if (selectedChatId == chatId) {
      navigate("/chat");
    }
    deleteChatroom({ id: selectedChatId });
  };

  const cancelDelete = () => {
    setShowDeleteModal(false);
  };

  const handleLogout = () => {
    logoutUser();
    navigate("/");
  };

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
              className={`group flex items-center justify-between gap-2 px-3 py-3 rounded-lg text-gray-700 text-sm cursor-pointer hover:bg-gray-200 transition mb-2 ${
                conversation.id == chatId ? "bg-gray-200 font-medium" : ""
              }`}
              onClick={() => {
                navigate(`/chat/${conversation.id}`);
                resetChatroom();
              }}
              onMouseEnter={() => setHoveredChatId(conversation.id)}
              onMouseLeave={() => setHoveredChatId(null)}
            >
              <div className="flex items-center gap-2 py-1">
                <FaRegCommentDots className="text-lg text-gray-400" />
                {conversation.title}
              </div>
              {hoveredChatId === conversation.id && (
                <button
                  className="p-1 hover:bg-gray-300 rounded-full"
                  onClick={(e) => handleMoreClick(e, conversation.id)}
                >
                  <FaEllipsisH className="text-gray-500" />
                </button>
              )}
            </div>
          )
        )}
      </div>

      {/* 사용자 정보 및 로그아웃 */}
      <div className="mt-4 pt-4 border-t border-[#ececec]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
              <FaUser className="text-gray-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">
                {userInfo?.nickname || "사용자"}
              </p>
              <p className="text-xs text-gray-500">{userInfo?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-4 px-2 py-4 text-lg text-gray-600 hover:bg-gray-200 rounded-lg transition"
          >
            <FaSignOutAlt />
          </button>
        </div>
      </div>

      {/* 삭제 메뉴 */}
      {showDeleteMenu && (
        <div
          className="fixed bg-white shadow-lg rounded-lg py-2 z-50"
          style={{
            top: menuPosition.y,
            left: menuPosition.x,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            className="w-full px-4 py-2 text-left hover:bg-gray-100"
            onClick={handleDelete}
          >
            채팅방 삭제
          </button>
        </div>
      )}

      {/* 삭제 확인 모달 */}
      <DeleteConfirmModal
        isOpen={showDeleteModal}
        onClose={cancelDelete}
        onConfirm={confirmDelete}
      />
    </div>
  );
};

export default Sidebar;
