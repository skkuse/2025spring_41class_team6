import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const getUserInfo = async () => {
  const response = await axiosInterceptor.get("/user");
  return response.data;
};

export { getUserInfo };
