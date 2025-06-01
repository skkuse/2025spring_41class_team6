import Sidebar from "@/components/layout/Sidebar";
import ChatLanding from "@/components/chat/ChatLanding";
import ChatRoom from "@/components/chat/ChatRoom";
import { useParams } from "react-router-dom";

const Chat = () => {
  const { chatId } = useParams();
  return (
    <div className="flex h-screen bg-[#fafbfc]">
      <Sidebar />
      {chatId ? <ChatRoom /> : <ChatLanding />}
    </div>
  );
};

export default Chat;
