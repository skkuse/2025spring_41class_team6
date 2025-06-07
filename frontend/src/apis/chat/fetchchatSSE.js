import useChatroomStore from "@/stores/useChatroomStore";

const fetchChatSSE = async (roomId, content, onComplete) => {
  // Zustand store에서 필요한 함수들 가져오기
  const {
    addToTokenQueue,
    completeMessageSendWithCallback,
    handleError,
    setIsMovieRecommendOpen,
  } = useChatroomStore.getState();

  try {
    const response = await fetch(
      `/api/chatrooms/${roomId}/messages?stream=true`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);

          if (data === "[DONE]") {
            break;
          }

          if (data) {
            try {
              const parsed = JSON.parse(data);

              if (parsed.type === "recommendation") {
                if (parsed.content.length > 0) {
                  setIsMovieRecommendOpen(true);
                }
              }

              // 토큰을 큐에 추가
              addToTokenQueue([parsed.content]);
            } catch {
              // JSON 파싱 실패 시 raw data를 토큰으로 추가
              addToTokenQueue([data]);
            }
          }
        }
      }
    }

    // 완료 처리 with 콜백
    completeMessageSendWithCallback(onComplete);
  } catch (err) {
    // 에러 처리
    handleError();
    console.error("Chat SSE Error:", err);
    alert("에러! " + err.message);
  }
};

export default fetchChatSSE;
