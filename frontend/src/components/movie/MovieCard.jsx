import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
export default function MovieCard({
  id,
  title,
  year,
  director,
  description,
  imageUrl,
}) {
  return (
    <div className="w-72 rounded-2xl overflow-hidden border border-gray-200 shadow-sm flex flex-col transition-all duration-200 hover:shadow-lg hover:shadow-gray-300/50">
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
        </div>
        <p className="text-xs text-gray-500">
          {year} · {director}
        </p>
        <p className="text-xs text-gray-600 mt-2 line-clamp-2">{description}</p>

        {/* Like / Dislike buttons */}
        {/* <div className="absolute bottom-2 right-2 flex gap-1">
          <button
            className="w-6 h-6 flex items-center justify-center hover:text-blue-500 transition"
            aria-label="좋아요"
          >
            <ThumbUpAltOutlinedIcon sx={{ fontSize: 14 }} />
          </button>
          <button
            className="w-6 h-6 flex items-center justify-center hover:text-red-500 transition"
            aria-label="싫어요"
          >
            <ThumbDownAltOutlinedIcon sx={{ fontSize: 14 }} />
          </button>
        </div> */}
      </div>
    </div>
  );
}
