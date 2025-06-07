import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const createChatroom = async ({ initial_message }) => {
  const response = await axiosInterceptor.post("/chatrooms", {
    initial_message: initial_message,
  });
  return response.data;
};

export default createChatroom;
