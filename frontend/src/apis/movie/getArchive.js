import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const getArchive = async () => {
  const response = await axiosInterceptor.get(`/movies/archive`);
  return response.data;
};

export default getArchive;
