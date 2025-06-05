import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { createPortal } from "react-dom";
import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import BookmarkBorderOutlinedIcon from "@mui/icons-material/BookmarkBorderOutlined";
import MovieDetail from "@/components/movie/MovieDetail";

export default function MovieCard({
  id,
  title,
  year,
  director,
  description,
  imageUrl,
  viewMode,
}) {
  const navigate = useNavigate();
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isDisliked, setIsDisliked] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleClick = () => {
    setIsModalOpen(true);
  };

  const handleBookmark = (e) => {
    e.stopPropagation();
    setIsBookmarked(!isBookmarked);
  };

  const handleLike = (e) => {
    e.stopPropagation();
    setIsLiked(!isLiked);
    if (isDisliked) setIsDisliked(false);
  };

  const handleDislike = (e) => {
    e.stopPropagation();
    setIsDisliked(!isDisliked);
    if (isLiked) setIsLiked(false);
  };

  return (
    <>
      <div
        className="w-72 rounded-2xl overflow-hidden border border-gray-200 shadow-sm flex flex-col transition-all duration-200 hover:shadow-lg hover:shadow-gray-300/50 select-none cursor-pointer"
        onClick={handleClick}
      >
        {/* Movie Poster */}
        <div className="h-100 bg-gray-100 flex items-center justify-center">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={title}
              className="w-full h-full object-cover"
            />
          ) : (
            <span className="text-gray-400 text-sm">이미지 없음</span>
          )}
        </div>

        {/* Info */}
        <div className="p-4 flex flex-col gap-1 relative">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-semibold truncate">{title}</h3>
            <div className="flex gap-2">
              {viewMode === 0 && (
                <button
                  onClick={handleBookmark}
                  className={`p-1 rounded-full hover:bg-gray-100 transition-colors ${
                    isBookmarked ? "text-blue-500" : "text-gray-400"
                  }`}
                >
                  <BookmarkBorderOutlinedIcon size={16} />
                </button>
              )}
              {viewMode === 1 && (
                <>
                  <button
                    onClick={handleLike}
                    className={`p-1 rounded-full hover:bg-gray-100 transition-colors ${
                      isLiked ? "text-red-500" : "text-gray-400"
                    }`}
                  >
                    <ThumbUpAltOutlinedIcon size={16} />
                  </button>
                  <button
                    onClick={handleDislike}
                    className={`p-1 rounded-full hover:bg-gray-100 transition-colors ${
                      isDisliked ? "text-gray-700" : "text-gray-400"
                    }`}
                  >
                    <ThumbDownAltOutlinedIcon size={16} />
                  </button>
                </>
              )}
              {viewMode === 2 && (
                <>
                  <button
                    onClick={handleBookmark}
                    className={`p-1 rounded-full hover:bg-gray-100 transition-colors ${
                      isBookmarked ? "text-blue-500" : "text-gray-400"
                    }`}
                  >
                    <BookmarkBorderOutlinedIcon size={16} />
                  </button>
                  <button
                    onClick={handleLike}
                    className={`p-1 rounded-full hover:bg-gray-100 transition-colors ${
                      isLiked ? "text-red-500" : "text-gray-400"
                    }`}
                  >
                    <ThumbUpAltOutlinedIcon size={16} />
                  </button>
                  <button
                    onClick={handleDislike}
                    className={`p-1 rounded-full hover:bg-gray-100 transition-colors ${
                      isDisliked ? "text-blue-500" : "text-gray-400"
                    }`}
                  >
                    <ThumbDownAltOutlinedIcon size={16} />
                  </button>
                </>
              )}
            </div>
          </div>
          <p className="text-xs text-gray-500">
            {year} · {director}
          </p>
          <p className="text-xs text-gray-600 mt-2 line-clamp-2">
            {description}
          </p>
        </div>
      </div>

      {/* Modal을 카드 밖에서 렌더링 */}
      {isModalOpen &&
        createPortal(
          <MovieDetail
            open={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            id={id}
          />,
          document.body
        )}
    </>
  );
}
