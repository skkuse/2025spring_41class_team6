import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import Tooltip from "@mui/material/Tooltip";

const ActorCard = ({ character_name, actor_name, image_url, character_id }) => {
  const handleChat = () => {
    console.log("대화 시작 ", character_id);
  };
  return (
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
          <h3 className="text-lg font-semibold text-gray-800 truncate">
            {actor_name}
          </h3>
          <Tooltip title="몰입형 대화 시작" arrow>
            <button
              className="p-1 rounded-full hover:bg-gray-100 transition-colors text-gray-400 hover:text-blue-500"
              aria-label="대화 시작"
              type="button"
              onClick={handleChat}
            >
              <ChatBubbleOutlineIcon style={{ fontSize: 20 }} />
            </button>
          </Tooltip>
        </div>
        <p className="text-sm text-gray-600 truncate">{character_name}</p>
      </div>
    </div>
  );
};

export default ActorCard;
