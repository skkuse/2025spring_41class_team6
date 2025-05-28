import MovieCard from "@/components/movie/MovieCard";
import getMovies from "@/apis/getMovies";

const BookmarkList = () => {
  const movies = getMovies();
  return (
    <div className="flex flex-wrap justify-start gap-4 p-4">
      {movies.map((movie) => (
        <MovieCard key={movie.id} {...movie} />
      ))}
    </div>
  );
};

export default BookmarkList;
