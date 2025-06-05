import axiosInstance from "@/apis/utils/axiosInterceptor";

const getArchive = async () => {
  const response = await axiosInstance.get(`/api/movies/archive`);
  return response.data;
};

export default getArchive;
