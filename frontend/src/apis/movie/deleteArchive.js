import axiosInstance from "@/apis/utils/axiosInterceptor";

const deleteArchive = async (movieId) => {
  const response = await axiosInstance.delete(`/api/movies/archive`, {
    id: movieId,
  });
  return response.data;
};

export default deleteArchive;
