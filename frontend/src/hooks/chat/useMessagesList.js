import { useQuery } from "@tanstack/react-query";
import { getMessages } from "@/apis/chat/getMessages";

const useMessagesList = (room_id) => {
  return useQuery({
    queryKey: ["messagesList", room_id],
    queryFn: () => getMessages(room_id),
  });
};

export default useMessagesList;
