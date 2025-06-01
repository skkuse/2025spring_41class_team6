import { useNavigate } from "react-router-dom";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import SendIcon from "@mui/icons-material/Send";
const ChatLanding = ({ mode = "normal" }) => {
  const navigate = useNavigate();
  const title =
    mode === "normal"
      ? "영화에 대해 궁금한게 있으신가요?"
      : "본인이 좋아하는 영화 속 인물과 대화해보세요";

  return (
    <div className="flex flex-1 flex-col items-center justify-center bg-white h-full">
      <div className="absolute top-6 right-6">
        <button
          onClick={() => navigate("/history")}
          className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition"
        >
          <BookmarkBorderIcon className="w-5 h-5" />
          <span className="text-sm font-medium">북마크</span>
        </button>
      </div>
      <div className="mb-8 text-2xl text-gray-700 font-semibold">{title}</div>
      <div className="w-full max-w-xl flex items-center">
        <input
          type="text"
          className="flex-1 border border-[#ececec] rounded-md px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-blue-100"
          placeholder="질문을 입력해보세요..."
        />
        <button className="ml-2 bg-black text-white rounded-md p-3 hover:bg-gray-800 transition">
          <SendIcon className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
};

export default ChatLanding;
