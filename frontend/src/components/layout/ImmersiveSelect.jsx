import { useBookmarkList } from "@/hooks/movie/useBookmark";
import MovieCard from "@/components/movie/MovieCard";
import ActorCard from "@/components/movie/ActorCard";
import { useState } from "react";
import { TextField, InputAdornment, IconButton } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import CloseIcon from "@mui/icons-material/Close";
import useWatchMovies from "@/hooks/movie/useWatchMovies";
import useMovie from "@/hooks/movie/useMovie";

const ImmersiveSelect = ({ onClose }) => {
  const { data: movies, isLoading } = useWatchMovies();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const { data: movieData, isLoading: movieLoading } = useMovie(
    selectedMovieId,
    {
      enabled: !!selectedMovieId,
    }
  );

  if (isLoading) {
    return <div>Loading...</div>;
  }

  const filteredMovies = movies.filter((movie) =>
    movie.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedMovie = movies.find((movie) => movie.id === selectedMovieId);

  return (
    <div className="flex flex-col gap-4 relative">
      <div className="flex flex-row items-center justify-between m-4">
        <div className="flex items-center gap-2">
          {selectedMovieId && (
            <IconButton
              onClick={() => setSelectedMovieId(null)}
              className="hover:bg-gray-100"
            >
              <ArrowBackIcon />
            </IconButton>
          )}
          <h3 className="text-lg font-semibold">
            {selectedMovieId
              ? `${selectedMovie?.title}의 등장인물`
              : "몰입형 대화를 위한 영화 선택"}
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {!selectedMovieId && (
            <TextField
              placeholder="영화 제목 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="small"
              sx={{ width: "300px" }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          )}
          <IconButton onClick={onClose} className="hover:bg-gray-100">
            <CloseIcon />
          </IconButton>
        </div>
      </div>

      {selectedMovieId ? (
        <div className="grid grid-cols-4 gap-4 p-4">
          {movieLoading ? (
            <div>배우 정보를 불러오는 중...</div>
          ) : (
            movieData?.characters?.map((character) => (
              <ActorCard
                key={character.id}
                character_name={character.name}
                actor_name={character.actor.name}
                image_url={character.actor.profile_image}
                character_id={character.id}
              />
            ))
          )}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4 p-4">
          {filteredMovies.map((movie) => (
            <MovieCard
              key={movie.id}
              id={movie.id}
              title={movie.title}
              year={movie.release_date}
              director={movie.directors[0]?.name || "Unknown"}
              description={movie.overview}
              imageUrl={movie.poster_img_url}
              setId={setSelectedMovieId}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ImmersiveSelect;
