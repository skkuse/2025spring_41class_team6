import MovieCard from "@/components/movie/MovieCard";
import { useBookmarkList } from "@/hooks/movie/useBookmark";

const BookmarkList = () => {
  const { data: movies, isLoading } = useBookmarkList();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="flex flex-wrap justify-start gap-4 p-4">
      {movies.map((movie) => (
        <MovieCard
          key={movie.id}
          id={movie.id}
          title={movie.title}
          year={movie.release_date}
          director={movie.directors[0].name}
          description={movie.overview}
          imageUrl={movie.poster_img_url}
        />
      ))}
    </div>
  );
};

export default BookmarkList;
