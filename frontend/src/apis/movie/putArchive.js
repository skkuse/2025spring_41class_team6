import axiosInstance from "@/apis/utils/axiosInterceptor";

const putArchive = async (movieId, rating) => {
  const response = await axiosInstance.put(`/api/movies/archive`, {
    id: movieId,
    rating: rating,
  });
  return response.data;
};

export default putArchive;
