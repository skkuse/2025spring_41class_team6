import { useBookmarkList } from "@/hooks/movie/useBookmark";
import MovieCard from "@/components/movie/MovieCard";
import { useState } from "react";
import { TextField, InputAdornment } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import useWatchMovies from "@/hooks/movie/useWatchMovies";
const ImmersiveSelect = () => {
  const { data: movies, isLoading } = useWatchMovies();

  const [searchQuery, setSearchQuery] = useState("");

  if (isLoading) {
    return <div>Loading...</div>;
  }

  const filteredMovies = movies.filter((movie) =>
    movie.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-row items-center justify-between m-4">
        <h3 className="text-lg font-semibold">몰입형 대화를 위한 영화 선택</h3>
        {/* 검색창 */}
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
      </div>

      {/* 영화 카드 목록 */}
      <div className="flex flex-wrap justify-center gap-4 p-4">
        {filteredMovies.map((movie) => (
          <MovieCard
            key={movie.id}
            id={movie.id}
            title={movie.title}
            year={movie.release_date}
            director={movie.directors[0]?.name || "Unknown"}
            description={movie.overview}
            imageUrl={movie.poster_img_url}
            viewMode={0}
          />
        ))}
      </div>
    </div>
  );
};

export default ImmersiveSelect;
