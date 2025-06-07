import MovieCard from "@/components/movie/MovieCard";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";
import { useGetArchiveList } from "@/hooks/movie/useArchive";

const WatchHistory = () => {
  const { data: archiveList, isLoading } = useGetArchiveList();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  console.log(archiveList);

  const likedMovies = archiveList.filter((movie) => movie.rating === 5);
  const dislikedMovies = archiveList.filter((movie) => movie.rating === 1);

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
              <MovieCard
                id={movie.id}
                title={movie.title}
                year={movie.release_date}
                director={movie.directors[0].name}
                description={movie.overview}
                imageUrl={movie.poster_img_url}
              />
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
              <MovieCard
                id={movie.id}
                title={movie.title}
                year={movie.release_date}
                director={movie.directors[0].name}
                description={movie.overview}
                imageUrl={movie.poster_img_url}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WatchHistory;
