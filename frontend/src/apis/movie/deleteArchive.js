import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const deleteArchive = async (movieId) => {
  const response = await axiosInterceptor.delete(`/movies/archive`, {
    id: movieId,
  });
  return response.data;
};

export default deleteArchive;
