import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const getRecommend = async (roomId) => {
  const response = await axiosInterceptor.get(
    `/chatrooms/${roomId}/recommended`
  );
  return response.data;
};

export default getRecommend;
