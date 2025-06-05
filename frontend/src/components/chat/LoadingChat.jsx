import { useState, useEffect } from "react";

const LoadingChat = ({ content, isStreaming = false }) => {
  const [showCursor, setShowCursor] = useState(true);

  // 스트리밍 중일 때 커서 깜빡임
  useEffect(() => {
    const interval = setInterval(() => {
      setShowCursor((prev) => !prev);
    }, 500);

    return () => clearInterval(interval);
  }, []);

  // 스트리밍 중: 플레인 텍스트만
  return (
    <div className="whitespace-pre-wrap text-gray-700 leading-7 font-normal">
      {content}
      {isStreaming && showCursor && (
        <span className="inline-block w-0.5 h-5 bg-gray-400 ml-1 animate-pulse" />
      )}
    </div>
  );
};

export default LoadingChat;
