import { useNavigate, useParams } from "react-router-dom";
import { useState } from "react";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import BookmarkList from "@/components/history/BookmarkList";
import WatchHistory from "@/components/history/WatchHistory";
import MovieDetail from "@/components/movie/MovieDetail";
const History = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState("bookmark");

  const handleClose = () => {
    navigate("/history");
  };

  return (
    <div className="px-60 py-12 w-full min-h-screen bg-gray-50 relative">
      <button
        className="flex items-center gap-2 px-6 py-2 border border-gray-200 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition absolute top-8 right-16"
        onClick={() => navigate("/")}
      >
        <ChatBubbleOutlineIcon className="w-5 h-5" />
        <span className="text-sm font-medium">대화</span>
      </button>
      <h2 className="text-2xl font-bold mb-6">영화 기록</h2>
      <div className="flex gap-2 mb-8">
        <button
          className={`px-24 py-2 rounded-md shadow text-gray-800 font-normal focus:outline-none text-sm transition-all duration-200 ease-in-out ${
            activeTab === "bookmark"
              ? "bg-white hover:bg-gray-50"
              : "bg-gray-200 text-gray-500 hover:bg-gray-300"
          }`}
          onClick={() => setActiveTab("bookmark")}
        >
          북마크
        </button>
        <button
          className={`px-24 py-2 rounded-md shadow text-gray-800 font-normal focus:outline-none text-sm transition-all duration-200 ease-in-out ${
            activeTab === "watch"
              ? "bg-white hover:bg-gray-50"
              : "bg-gray-200 text-gray-500 hover:bg-gray-300"
          }`}
          onClick={() => setActiveTab("watch")}
        >
          시청 기록
        </button>
      </div>
      <h3 className="text-lg font-semibold mb-4">
        {activeTab === "bookmark" ? "북마크한 영화" : "시청 기록"}
      </h3>
      {activeTab === "bookmark" ? <BookmarkList /> : <WatchHistory />}
      <MovieDetail open={!!id} onClose={handleClose} id={id} />
    </div>
  );
};

export default History;
