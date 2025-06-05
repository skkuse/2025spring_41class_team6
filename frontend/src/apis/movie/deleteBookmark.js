import axiosInstance from "@/apis/utils/axiosInterceptor";

const deleteBookmark = async (movieId) => {
  const response = await axiosInstance.delete(`/api/movies/bookmarked`, {
    id: movieId,
  });
  return response.data;
};

export default deleteBookmark;
