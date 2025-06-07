import { useQuery } from "@tanstack/react-query";
import getMovie from "@/apis/movie/getMovie";

const useMovie = (id) => {
  return useQuery({
    queryKey: ["movie", id],
    queryFn: () => getMovie(id),
    enabled: !!id,
  });
};

export default useMovie;
