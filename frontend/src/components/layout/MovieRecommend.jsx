import CloseTwoToneIcon from "@mui/icons-material/CloseTwoTone";
import MovieCard from "@/components/movie/MovieCard";
import { useState, useEffect } from "react";
import useRecommend from "@/hooks/chat/useRecommend";

const MovieRecommend = ({ onClose, chatroomId }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const { data: recommendation, isLoading } = useRecommend(chatroomId);

  // useEffect를 사용해서 데이터가 로드되면 currentPage를 설정
  useEffect(() => {
    if (recommendation?.length) {
      setCurrentPage(recommendation.length);
    }
  }, [recommendation]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  const totalPages = recommendation?.length ? recommendation.length : 0;

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  return (
    <>
      <div
        className={`h-full w-120 bg-white shadow-lg flex flex-col transform transition-transform duration-300 ease-in-out`}
      >
        <div className="p-4 flex-none">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2 p-2">
              <button
                onClick={handlePrevPage}
                className="text-gray-500 hover:text-gray-700"
                disabled={currentPage === 1}
              >
                &lt;
              </button>
              <span className="text-sm">
                {currentPage}/{totalPages}
              </span>
              <button
                onClick={handleNextPage}
                className="text-gray-500 hover:text-gray-700"
                disabled={currentPage === totalPages}
              >
                &gt;
              </button>
            </div>
            <h1 className="text-2xl font-bold m-4">영화 추천</h1>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 mx-8"
            >
              <CloseTwoToneIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
        {totalPages > 0 ? (
          <div className="flex-1 overflow-y-auto px-4 pb-4">
            <div className="flex flex-col gap-4 items-center">
              {recommendation[currentPage - 1].map((movie) => (
                <MovieCard
                  key={movie.id}
                  id={movie.id}
                  title={movie.title}
                  year={movie.release_date}
                  director={movie.directors?.[0]?.name || ""}
                  description={movie.overview}
                  imageUrl={movie.poster_img_url}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto px-4 pb-4">
            <div className="flex flex-col gap-4 items-center">
              <div>추천 영화가 없습니다.</div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default MovieRecommend;
