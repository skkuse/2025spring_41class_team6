import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const getChatrooms = async () => {
  const response = await axiosInterceptor.get("/chatrooms");
  console.log(response.data);
  return response.data;
};

export default getChatrooms;
