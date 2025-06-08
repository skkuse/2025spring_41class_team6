import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const getMovie = async (id) => {
  const response = await axiosInterceptor.get(`/movies/${id}`);
  return response.data;
};

export default getMovie;
