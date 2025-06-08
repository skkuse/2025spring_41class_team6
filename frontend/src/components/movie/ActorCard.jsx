import React, { useState, useRef } from "react";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import Tooltip from "@mui/material/Tooltip";
import { Modal, Box, CircularProgress, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";

const ActorCard = ({
  character_name,
  actor_name,
  image_url,
  character_id,
  onClose,
}) => {
  const [chatroomId, setChatroomId] = useState(null);
  const [status, setStatus] = useState(0); // 0:대기, 1:채팅방 생성 중, 2:정보 수집, 3:캐릭터 준비, 4:완료
  const navigate = useNavigate();
  const chatroomIdRef = useRef(null);
  const queryClient = useQueryClient();

  // 모던한 모노톤 메시지
  const loadingMessages = {
    1: "채팅방을 생성하고 있습니다...",
    2: "캐릭터 정보 수집 중...",
    3: "캐릭터를 준비하고 있습니다...",
    4: "거의 완료되었습니다!",
  };

  const handleChat = async () => {
    setStatus(1);
    const characterIdNum = parseInt(character_id, 10);

    const response = await fetch(`/api/chatrooms`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ character_id: characterIdNum }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const data = line.slice(6);
        if (data === "[DONE]") break;
        try {
          const parsed = JSON.parse(data);
          if (parsed.type === "created chatroom") {
            setChatroomId(parsed.content.id);
            chatroomIdRef.current = parsed.content.id;
          }
          if (parsed.type === "signal") {
            if (parsed.content === "cc create start") {
              setStatus(2);
              setTimeout(() => setStatus(3), 2000);
            }
            if (parsed.content === "cc create done") setStatus(4);
            if (parsed.content === "sse finish") {
              if (onClose) onClose();
              queryClient.invalidateQueries({ queryKey: ["chatroomList"] });
              navigate(`/chat/${chatroomIdRef.current}`);
              setStatus(0);
              return;
            }
          }
        } catch (error) {
          console.error("Error parsing data:", error);
        }
      }
    }
  };

  return (
    <>
      <div className="flex flex-col items-center w-[200px] bg-white rounded-lg shadow-md overflow-hidden">
        <div className="relative w-full h-[300px]">
          <img
            src={image_url}
            alt={actor_name}
            className="w-full h-full object-cover"
          />
        </div>
        <div className="p-4 w-full">
          <div className="flex items-center justify-between gap-2">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {actor_name}
            </h3>
            <Tooltip title="몰입형 대화 시작" arrow>
              <button
                className="p-1 rounded-full hover:bg-gray-200 transition-colors text-gray-600 hover:text-gray-900"
                aria-label="대화 시작"
                type="button"
                onClick={handleChat}
                disabled={status !== 0}
              >
                <ChatBubbleOutlineIcon style={{ fontSize: 20 }} />
              </button>
            </Tooltip>
          </div>
          <p className="text-sm text-gray-600 truncate">{character_name}</p>
        </div>
      </div>

      <Modal
        open={status > 0}
        aria-labelledby="loading-modal"
        aria-describedby="loading-description"
      >
        <Box
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: 400,
            bgcolor: "#f5f5f5",
            borderRadius: 2,
            boxShadow: 24,
            p: 4,
            textAlign: "center",
          }}
        >
          <Box sx={{ mb: 2 }}>
            <Box
              component="img"
              src={image_url}
              alt={actor_name}
              sx={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                objectFit: "cover",
                mx: "auto",
              }}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <CircularProgress
              size={60}
              thickness={4}
              sx={{
                color: status === 4 ? "#757575" : "#424242",
                transition: "color 0.3s ease",
              }}
            />
          </Box>

          <Typography
            id="loading-modal"
            variant="h6"
            component="h2"
            sx={{ mb: 1, fontWeight: 500, color: "#212121" }}
          >
            {character_name}와의 대화 준비 중
          </Typography>

          <Typography
            id="loading-description"
            sx={{ fontSize: "0.95rem", color: "#424242" }}
          >
            {loadingMessages[status]}
          </Typography>

          <Box
            sx={{ mt: 3, display: "flex", justifyContent: "center", gap: 1 }}
          >
            {[1, 2, 3, 4].map((step) => (
              <Box
                key={step}
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  bgcolor: status >= step ? "#424242" : "#BDBDBD",
                  transition: "background-color 0.3s ease",
                }}
              />
            ))}
          </Box>
        </Box>
      </Modal>
    </>
  );
};

export default ActorCard;
