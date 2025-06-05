import MenuOpenIcon from "@mui/icons-material/MenuOpen";
import { getMovies } from "@/apis/testApi";
import MovieCard from "@/components/movie/MovieCard";
import { useState } from "react";

const MovieRecommend = ({ onClose }) => {
  const movieList = getMovies();
  const [currentPage, setCurrentPage] = useState(1);
  const moviesPerPage = 5;
  const totalPages = Math.ceil(movieList.length / moviesPerPage);

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

  const startIndex = (currentPage - 1) * moviesPerPage;
  const endIndex = startIndex + moviesPerPage;
  const currentMovies = movieList.slice(startIndex, endIndex);

  return (
    <>
      <div
        className={`h-full w-120 bg-white border-l border-gray-500 flex flex-col transform transition-transform duration-300 ease-in-out`}
      >
        <div className="p-4 flex-none">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
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
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <MenuOpenIcon className="w-5 h-5" />
            </button>
          </div>
          <h1 className="text-2xl font-bold mb-4">영화 추천</h1>
        </div>
        <div className="flex-1 overflow-y-auto px-4 pb-4">
          <div className="flex flex-col gap-4 items-center">
            {currentMovies.map((movie) => (
              <MovieCard
                key={movie.id}
                id={movie.id}
                title={movie.title}
                year={movie.year}
                director={movie.director}
                description={movie.description}
                imageUrl={movie.imageUrl}
                viewMode={0}
              />
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export default MovieRecommend;
