import React from "react";
import MovieCard from "@/components/movie/MovieCard";
import { getMovies } from "@/apis/testApi";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";

const WatchHistory = () => {
  // 임시 분류: id 홀수는 좋아요, 짝수는 싫어요
  const movies = getMovies();
  const likedMovies = movies.filter((movie) => movie.id % 2 === 1);
  const dislikedMovies = movies.filter((movie) => movie.id % 2 === 0);

  return (
    <div className="p-8">
      {/* 좋아요 표시한 영화 */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <ThumbUpAltOutlinedIcon className="text-green-600" />
          <span className="font-semibold text-lg">좋아요 표시한 영화</span>
        </div>
        <div className="flex gap-4 overflow-x-auto w-full pb-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
          {likedMovies.map((movie) => (
            <div className="flex-shrink-0" key={movie.id}>
              <MovieCard {...movie} />
            </div>
          ))}
        </div>
      </div>
      {/* 싫어요 표시한 영화 */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <ThumbDownAltOutlinedIcon className="text-red-500" />
          <span className="font-semibold text-lg">싫어요 표시한 영화</span>
        </div>
        <div className="flex gap-4 overflow-x-auto w-full pb-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
          {dislikedMovies.map((movie) => (
            <div className="flex-shrink-0" key={movie.id}>
              <MovieCard {...movie} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WatchHistory;
