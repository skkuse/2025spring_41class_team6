import { useQuery } from "@tanstack/react-query";
import getChatrooms from "@/apis/chat/getChatrooms";

const useChatroomsList = () => {
  return useQuery({
    queryKey: ["chatroomList"],
    queryFn: () => getChatrooms(),
  });
};

export default useChatroomsList;
