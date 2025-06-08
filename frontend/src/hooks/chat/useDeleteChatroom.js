import { useMutation, useQueryClient } from "@tanstack/react-query";
import deleteChatroom from "@/apis/chat/deleteChatroom";

const useDeleteChatroom = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id }) => deleteChatroom(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chatroomList"] });
    },
  });
};

export default useDeleteChatroom;
