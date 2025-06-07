import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const createChatroom = async () => {
  const response = await axiosInterceptor.post("/chatrooms");
  return response.data;
};

export default createChatroom;
