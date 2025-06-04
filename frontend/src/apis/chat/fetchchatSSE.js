const fetchChatSSE = async (room_id, content, onToken, onDone, onError) => {
  try {
    const response = await fetch(
      `/api/chatrooms/${room_id}/messages?stream=true`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      }
    );

    if (!response.body) throw new Error("No stream");

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let done = false;
    let accumulated = "";

    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      if (value) {
        const chunk = decoder.decode(value, { stream: true });
        // SSE는 "data: ..." 형태로 오므로 파싱 필요
        const lines = chunk.split("\n");
        for (let line of lines) {
          if (line.startsWith("data: ")) {
            const token = line.replace("data: ", "");
            accumulated += token;
            onToken(token, accumulated); // token별/누적값 콜백
          }
        }
      }
    }
    onDone && onDone(accumulated);
  } catch (err) {
    onError && onError(err);
  }
};
