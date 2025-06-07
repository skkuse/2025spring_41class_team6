import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const deleteBookmark = async (movieId) => {
  const response = await axiosInterceptor.delete(`/movies/bookmarked`, {
    data: {
      id: movieId,
    },
  });
  console.log(response.data);
  return response.data;
};

export default deleteBookmark;
