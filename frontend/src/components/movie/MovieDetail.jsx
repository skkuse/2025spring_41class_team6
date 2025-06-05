import React, { useState } from "react";
import Modal from "@mui/material/Modal";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";
import { getMovie } from "@/apis/testApi";
const MovieDetail = ({ open, onClose, id }) => {
  const [tabIndex, setTabIndex] = useState(0);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isDisliked, setIsDisliked] = useState(false);

  if (!open) return null;

  const data = getMovie(id);
  const tabLabels = ["개요", "출연진"];

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
            {data.imageUrl ? (
              <img
                src={data.imageUrl}
                alt={data.title}
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
              <h2 id="movie-modal-title" className="text-2xl font-bold mb-2">
                {data.title}
              </h2>
              <div className="text-gray-500 text-sm mb-4">
                <span>{data.year}</span> · <span>{data.director}</span> ·{" "}
                <span>⭐ {data.rating}</span>
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                {data.genres.map((genre, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-700"
                  >
                    {genre}
                  </span>
                ))}
              </div>
              <p className="text-gray-700 text-base leading-relaxed">
                {data.description}
              </p>
            </div>

            {/* 상호작용 버튼 */}
            <div className="flex gap-4 mt-auto pt-6">
              <button
                onClick={() => setIsBookmarked(!isBookmarked)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
                  isBookmarked
                    ? "bg-blue-50 border-blue-200 text-blue-600"
                    : "border-gray-200 text-gray-600 hover:bg-gray-50"
                } transition`}
              >
                <BookmarkBorderIcon className="w-5 h-5" />
                <span className="text-sm font-medium">북마크</span>
              </button>
              <button
                onClick={() => {
                  setIsLiked(!isLiked);
                  if (isLiked) setIsDisliked(false);
                }}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
                  isLiked
                    ? "bg-green-50 border-green-200 text-green-600"
                    : "border-gray-200 text-gray-600 hover:bg-gray-50"
                } transition`}
              >
                <ThumbUpAltOutlinedIcon className="w-5 h-5" />
                <span className="text-sm font-medium">좋아요</span>
              </button>
              <button
                onClick={() => {
                  setIsDisliked(!isDisliked);
                  if (isDisliked) setIsLiked(false);
                }}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
                  isDisliked
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
                {data.overview}
              </p>
            </div>
          )}
          {tabIndex === 1 && (
            <div>
              <h4 className="font-semibold mb-1">출연진</h4>
              <ul className="list-disc pl-5 text-gray-700">
                {data.cast.map((actor, idx) => (
                  <li key={idx}>
                    {actor.name} - {actor.role}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Box>
      </Box>
    </Modal>
  );
};

export default MovieDetail;
