import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const getChatrooms = async () => {
  const response = await axiosInterceptor.get("/chatrooms");
  return response.data;
};

export default getChatrooms;
