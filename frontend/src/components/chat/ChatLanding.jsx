import { useNavigate } from "react-router-dom";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import { useState, useEffect } from "react";
import useCreateChatroom from "@/hooks/chat/useCreateChatroom";
import CircularProgress from "@mui/material/CircularProgress";

const exampleQuestions = [
  "이 영화의 결말을 설명해줘",
  "비슷한 분위기의 영화 추천해줘",
  "실제 역사와 다른 점이 있나요?",
  "감독의 의도는 무엇인가요?",
  "결말에 대해서 해석해줘",
  "주인공이 왜 이런 선택을 했을까?",
];

const ChatLanding = ({ mode = "normal" }) => {
  const navigate = useNavigate();
  const { mutate: createChatroom, isPending } = useCreateChatroom();
  const [slideIdx, setSlideIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setSlideIdx((prev) => (prev + 1) % exampleQuestions.length);
    }, 1600);
    return () => clearInterval(timer);
  }, []);

  const title =
    mode === "normal"
      ? "영화에 대해 궁금한게 있으신가요?"
      : "본인이 좋아하는 영화 속 인물과 대화해보세요";

  const handleStartChat = () => {
    createChatroom({ initial_message: "" });
  };

  return (
    <div className="flex flex-1 flex-col items-center justify-center bg-white h-full w-full">
      <div className="absolute top-6 right-6">
        <button
          onClick={() => navigate("/history")}
          className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-4xl text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition"
        >
          <BookmarkBorderIcon className="w-5 h-5" />
          <span className="text-sm font-medium">북마크</span>
        </button>
      </div>
      <div className="mb-8 text-4xl text-gray-800 font-bold text-center">
        {title}
      </div>
      <div className="mb-10 h-8 flex items-center justify-center relative w-full max-w-xl overflow-hidden">
        <div
          className="text-2xl w-full h-full text-center text-gray-500 transition-all duration-500"
          style={{ transform: `translateY(-${slideIdx * 2}rem)` }}
        >
          {exampleQuestions.map((q, idx) => (
            <div
              key={q}
              className={`h-8 flex items-center justify-center ${
                slideIdx === idx ? "opacity-100" : "opacity-0"
              } transition-opacity duration-500`}
              style={{
                position: "absolute",
                width: "100%",
                top: `${idx * 2}rem`,
              }}
            >
              {q}
            </div>
          ))}
        </div>
      </div>
      <button
        onClick={handleStartChat}
        disabled={isPending}
        className="px-8 py-4  text-[#222] border border-[#d1d5db] rounded-lg text-lg font-medium shadow-sm hover:bg-[#ececec] hover:border-[#bbb] transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-gray-200"
        style={{ boxShadow: "0 2px 8px 0 rgba(60,60,60,0.04)" }}
      >
        {isPending ? (
          <CircularProgress size={24} color="inherit" />
        ) : (
          "채팅 시작하기"
        )}
      </button>
    </div>
  );
};

export default ChatLanding;
