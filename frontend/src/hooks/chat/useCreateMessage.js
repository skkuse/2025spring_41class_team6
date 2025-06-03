import { useMutation, useQueryClient } from "@tanstack/react-query";
import postMessage from "@/apis/chat/postMessage";

const useCreateMessage = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ room_id, content }) => postMessage({ room_id, content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messagesList"] });
    },
  });
};

export default useCreateMessage;
