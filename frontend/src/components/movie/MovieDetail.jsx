import { useState } from "react";
import Modal from "@mui/material/Modal";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";
import useMovie from "@/hooks/movie/useMovie";
import ActorCard from "@/components/movie/ActorCard";
import { usePostBookmark, useDeleteBookmark } from "@/hooks/movie/useBookmark";
import {
  usePostArchive,
  useDeleteArchive,
  usePutArchive,
} from "@/hooks/movie/useArchive";

const MovieDetail = ({ open, onClose, id }) => {
  const [tabIndex, setTabIndex] = useState(0);

  const { mutate: postBookmark } = usePostBookmark();
  const { mutate: deleteBookmark } = useDeleteBookmark();
  const { mutate: postArchive } = usePostArchive();
  const { mutate: putArchive } = usePutArchive();
  const { mutate: deleteArchive } = useDeleteArchive();

  const { data: movie, isLoading } = useMovie(id);

  if (!open) return null;
  if (isLoading) return <div>Loading...</div>;

  // 디버깅용 로그
  console.log("Movie data:", movie);
  console.log("Current rating:", movie.rating, "Type:", typeof movie.rating);

  const tabLabels = ["개요", "출연진"];

  const handleBookmark = () => {
    if (movie.bookmarked) {
      deleteBookmark(id);
    } else {
      postBookmark(id);
    }
  };

  const handleLike = () => {
    if (
      movie.rating === 0 ||
      movie.rating === null ||
      movie.rating === undefined
    ) {
      postArchive({ movieId: id, rating: 5 });
    } else if (movie.rating === 1) {
      putArchive({ movieId: id, rating: 5 });
    } else if (movie.rating === 5) {
      deleteArchive({ movieId: id });
    }
  };

  const handleDislike = () => {
    if (
      movie.rating === 0 ||
      movie.rating === null ||
      movie.rating === undefined
    ) {
      postArchive({ movieId: id, rating: 1 });
    } else if (movie.rating === 5) {
      putArchive({ movieId: id, rating: 1 });
    } else if (movie.rating === 1) {
      deleteArchive({ movieId: id });
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="movie-modal-title"
      aria-describedby="movie-modal-description"
    >
      <Box className="absolute top-1/2 left-1/2 w-[800px] max-h-[90vh] -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl shadow-2xl p-8 outline-none overflow-y-auto">
        <IconButton
          aria-label="close"
          onClick={onClose}
          className="!absolute right-4 top-4"
        >
          <CloseIcon />
        </IconButton>

        {/* 영화 포스터와 정보 영역 */}
        <div className="flex gap-8 mb-6">
          {/* 포스터 */}
          <div className="w-[300px] h-[450px] bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
            {movie.poster_img_url ? (
              <img
                src={movie.poster_img_url}
                alt={movie.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                이미지 없음
              </div>
            )}
          </div>

          {/* 정보 */}
          <div className="flex-1 flex flex-col">
            <div>
              <h2 id="movie-modal-title" className="text-3xl font-bold mb-4">
                {movie.title}
              </h2>
              <div className="text-gray-500 text-sm mb-6">
                <span>{movie.release_date}</span> ·{" "}
                <span>{movie.directors[0]?.name}</span> ·{" "}
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                {movie.genres.map((genre, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-700"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            </div>

            {/* 상호작용 버튼 */}
            <div className="flex gap-4 mt-auto pt-6">
              {/* 북마크 */}
              <button
                onClick={handleBookmark}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
                  movie.bookmarked
                    ? "bg-blue-50 border-blue-200 text-blue-600"
                    : "border-gray-200 text-gray-600 hover:bg-gray-50"
                } transition`}
              >
                <BookmarkBorderIcon className="w-5 h-5" />
                <span className="text-sm font-medium">북마크</span>
              </button>
              {/* 좋아요 */}
              <button
                onClick={handleLike}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
                  movie.rating === 5
                    ? "bg-green-50 border-green-200 text-green-600"
                    : "border-gray-200 text-gray-600 hover:bg-gray-50"
                } transition`}
              >
                <ThumbUpAltOutlinedIcon className="w-5 h-5" />
                <span className="text-sm font-medium">좋아요</span>
              </button>
              {/* 싫어요 */}
              <button
                onClick={handleDislike}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
                  movie.rating === 1
                    ? "bg-red-50 border-red-200 text-red-600"
                    : "border-gray-200 text-gray-600 hover:bg-gray-50"
                } transition`}
              >
                <ThumbDownAltOutlinedIcon className="w-5 h-5" />
                <span className="text-sm font-medium">싫어요</span>
              </button>
            </div>
          </div>
        </div>

        <Tabs
          value={tabIndex}
          onChange={(_, newValue) => setTabIndex(newValue)}
          aria-label="movie detail tabs"
          className="mb-4 border-b border-gray-200"
          TabIndicatorProps={{ style: { background: "#222" } }}
        >
          {tabLabels.map((label, idx) => (
            <Tab
              key={label}
              label={label}
              className={
                "text-base font-medium normal-case " +
                (tabIndex === idx ? "text-black" : "text-gray-400")
              }
            />
          ))}
        </Tabs>
        <Box className="min-h-[120px]">
          {tabIndex === 0 && (
            <div>
              <h4 className="font-semibold mb-1">줄거리</h4>
              <p className="text-gray-700 text-base leading-relaxed">
                {movie.overview}
              </p>
            </div>
          )}
          {tabIndex === 1 && (
            <div>
              <h2 className="text-2xl font-bold mb-4">출연진</h2>
              <div className="flex flex-wrap gap-4 justify-center">
                {movie.characters.length === 0 ? (
                  <div className="text-gray-500">출연진 정보가 없습니다.</div>
                ) : (
                  movie.characters.map((character, idx) => (
                    <div
                      key={idx}
                      className="w-[200px] flex flex-col items-center bg-white rounded-lg shadow-md overflow-hidden"
                    >
                      <ActorCard
                        character_name={character.name}
                        actor_name={character.actor.name}
                        image_url={character.actor.profile_image}
                        character_id={character.id}
                      />
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </Box>
      </Box>
    </Modal>
  );
};

export default MovieDetail;
