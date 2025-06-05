import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const putArchive = async (movieId, rating) => {
  const response = await axiosInterceptor.put(`/movies/archive`, {
    id: movieId,
    rating: rating,
  });
  return response.data;
};

export default putArchive;
