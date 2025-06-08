import { memo } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import MovieIcon from "@mui/icons-material/Movie";

// 상태별 메시지 정의 - 차분한 톤으로 통일
const STATUS_CONFIG = {
  1: {
    message: "영화 정보를 검색하고 있습니다",
    color: "text-gray-600",
  },
  2: {
    message: "답변을 준비하고 있습니다",
    color: "text-gray-600",
  },
  3: {
    message: "데이터베이스를 확인하고 있습니다",
    color: "text-gray-600",
  },
  4: {
    message: "일시적인 문제가 발생했습니다",
    color: "text-gray-500",
  },
  5: {
    message: "결과를 정리하고 있습니다",
    color: "text-gray-600",
  },
};

const ServerMessage = memo(({ status }) => {
  // 상태가 0이거나 정의되지 않은 경우 아무것도 렌더링하지 않음
  if (!status || status === 0) {
    return null;
  }

  const config = STATUS_CONFIG[status];

  // 정의되지 않은 상태값에 대한 기본 처리
  if (!config) {
    return (
      <div className="flex items-center gap-3 px-4 py-2.5 bg-gray-50 rounded-lg">
        <MovieIcon className="w-4 h-4 text-gray-400" />
        <CircularProgress size={14} className="text-gray-400" />
        <span className="text-sm text-gray-500">처리 중입니다</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3 px-4 py-2.5 bg-gray-50 rounded-lg transition-all duration-300">
      {/* 영화 아이콘 */}
      <MovieIcon className="w-4 h-4 text-gray-400" />

      {/* 상태 메시지 */}
      <span className={`text-sm ${config.color}`}>{config.message}</span>

      {/* 점점점 애니메이션 - 더 차분하게 */}
      <div className="flex gap-0.5 ml-1">
        <div
          className="w-1 h-1 rounded-full bg-gray-400 opacity-60"
          style={{
            animation: "fade 1.4s infinite",
            animationDelay: "0ms",
          }}
        ></div>
        <div
          className="w-1 h-1 rounded-full bg-gray-400 opacity-60"
          style={{
            animation: "fade 1.4s infinite",
            animationDelay: "400ms",
          }}
        ></div>
        <div
          className="w-1 h-1 rounded-full bg-gray-400 opacity-60"
          style={{
            animation: "fade 1.4s infinite",
            animationDelay: "800ms",
          }}
        ></div>
      </div>

      <style jsx>{`
        @keyframes fade {
          0%,
          100% {
            opacity: 0.3;
          }
          50% {
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
});

ServerMessage.displayName = "ServerMessage";

export default ServerMessage;
