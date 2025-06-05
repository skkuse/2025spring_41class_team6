import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const deleteBookmark = async (movieId) => {
  const response = await axiosInterceptor.delete(`/movies/bookmarked`, {
    id: movieId,
  });
  return response.data;
};

export default deleteBookmark;
