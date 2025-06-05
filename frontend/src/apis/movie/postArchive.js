import axiosInstance from "@/apis/utils/axiosInterceptor";

const postArchive = async (movieId, rating) => {
  const response = await axiosInstance.post(`/api/movies/archive`, {
    id: movieId,
    rating: rating,
  });
  return response.data;
};

export default postArchive;
