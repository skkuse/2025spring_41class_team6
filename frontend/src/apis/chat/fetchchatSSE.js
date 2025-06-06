const fetchChatSSE = async (
  roomId,
  content,
  onToken,
  onDone,
  onError,
  onRecommendation
) => {
  try {
    const response = await fetch(
      `/api/chatrooms/${roomId}/messages?stream=true`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      }
    );

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
                  onRecommendation(true);
                }
              }

              onToken(parsed.content);
            } catch {
              onToken(data);
            }
          }
        }
      }
    }

    onDone && onDone();
  } catch (err) {
    onError && onError(err);
  }
};

export default fetchChatSSE;
