import axiosInstance from "@/apis/utils/axiosInterceptor";

const postBookmark = async (movieId) => {
  const response = await axiosInstance.post(`/api/movies/bookmarked`, {
    id: movieId,
  });
  return response.data;
};

export default postBookmark;
