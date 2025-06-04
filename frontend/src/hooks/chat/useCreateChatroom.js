import { useMutation, useQueryClient } from "@tanstack/react-query";
import createChatroom from "@/apis/chat/createChatroom";
import { useNavigate } from "react-router-dom";

const useCreateChatroom = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: ({ initial_message }) => createChatroom({ initial_message }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["chatroomList"] });
      navigate(`/chat/${data.id}`);
    },
  });
};

export default useCreateChatroom;
