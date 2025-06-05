import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const postArchive = async (movieId, rating) => {
  const response = await axiosInterceptor.post(`/movies/archive`, {
    id: movieId,
    rating: rating,
  });
  return response.data;
};

export default postArchive;
