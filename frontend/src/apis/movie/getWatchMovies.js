import { axiosInterceptor } from "../utils/axiosInterceptor";

const getWatchMovies = async () => {
  const response = await axiosInterceptor.get("/movies/watchlist");
  return response.data;
};

export default getWatchMovies;
