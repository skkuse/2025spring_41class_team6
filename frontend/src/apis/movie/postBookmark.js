import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const postBookmark = async (movieId) => {
  const response = await axiosInterceptor.post(`/movies/bookmarked`, {
    id: movieId,
  });
  return response.data;
};

export default postBookmark;
