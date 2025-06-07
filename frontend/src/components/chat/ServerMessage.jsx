import { memo } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import SearchIcon from "@mui/icons-material/Search";
import StorageIcon from "@mui/icons-material/Storage";
import MovieIcon from "@mui/icons-material/Movie";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import AnalyticsIcon from "@mui/icons-material/Analytics";

// 상태별 메시지와 아이콘 정의
const STATUS_CONFIG = {
  1: {
    message: "크롤링 진행하는 중...",
    icon: <SearchIcon className="w-4 h-4 text-blue-500" />,
    color: "text-blue-600",
    bgColor: "bg-blue-50",
    borderColor: "border-blue-200",
  },
  2: {
    message: "메시지 작성 중...",
    icon: <StorageIcon className="w-4 h-4 text-green-500" />,
    color: "text-green-600",
    bgColor: "bg-green-50",
    borderColor: "border-green-200",
  },
  3: {
    message: "데이터베이스 탐색 중...",
    icon: <MovieIcon className="w-4 h-4 text-purple-500" />,
    color: "text-purple-600",
    bgColor: "bg-purple-50",
    borderColor: "border-purple-200",
  },
  4: {
    message: "에러 발생..",
    icon: <AutoAwesomeIcon className="w-4 h-4 text-orange-500" />,
    color: "text-orange-600",
    bgColor: "bg-orange-50",
    borderColor: "border-orange-200",
  },
  5: {
    message: "결과 정리 중...",
    icon: <AnalyticsIcon className="w-4 h-4 text-indigo-500" />,
    color: "text-indigo-600",
    bgColor: "bg-indigo-50",
    borderColor: "border-indigo-200",
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
      <div className="flex items-center gap-3 px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg shadow-sm">
        <CircularProgress size={16} className="text-gray-400" />
        <span className="text-sm text-gray-600 font-medium">
          처리 중... (상태: {status})
        </span>
      </div>
    );
  }

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-sm border transition-all duration-300 ${config.bgColor} ${config.borderColor}`}
    >
      {/* 아이콘과 로딩 스피너 */}
      <div className="flex items-center gap-2">
        {config.icon}
        <CircularProgress
          size={16}
          className={config.color.replace("text-", "text-")}
        />
      </div>

      {/* 상태 메시지 */}
      <span className={`text-sm font-medium ${config.color}`}>
        {config.message}
      </span>

      {/* 점점점 애니메이션 */}
      <div className="flex gap-1">
        <div
          className={`w-1 h-1 rounded-full ${config.color.replace(
            "text-",
            "bg-"
          )} animate-pulse`}
          style={{ animationDelay: "0ms" }}
        ></div>
        <div
          className={`w-1 h-1 rounded-full ${config.color.replace(
            "text-",
            "bg-"
          )} animate-pulse`}
          style={{ animationDelay: "200ms" }}
        ></div>
        <div
          className={`w-1 h-1 rounded-full ${config.color.replace(
            "text-",
            "bg-"
          )} animate-pulse`}
          style={{ animationDelay: "400ms" }}
        ></div>
      </div>
    </div>
  );
});

ServerMessage.displayName = "ServerMessage";

export default ServerMessage;
