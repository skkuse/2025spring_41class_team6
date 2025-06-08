import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const deleteChatroom = async (chatroomId) => {
  const response = await axiosInterceptor.delete(`/chatrooms`, {
    data: {
      id: chatroomId,
    },
  });
  return response.data;
};

export default deleteChatroom;
