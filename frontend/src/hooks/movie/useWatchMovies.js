import { useQuery } from "@tanstack/react-query";
import getWatchMovies from "@/apis/movie/getWatchMovies";

const useWatchMovies = () => {
  return useQuery({ queryKey: ["watchMovies"], queryFn: getWatchMovies });
};

export default useWatchMovies;
