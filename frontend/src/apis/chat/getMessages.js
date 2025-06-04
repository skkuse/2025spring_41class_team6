import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const getMessages = async (room_id) => {
  const response = await axiosInterceptor.get(`/chatrooms/${room_id}/messages`);
  return response.data;
};

export { getMessages };
