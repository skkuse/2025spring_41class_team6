import { useQuery } from "@tanstack/react-query";
import { getBookmarkList } from "../../apis/movie/getBookmarkList";

const useBookmarkList = () => {
  return useQuery({
    queryKey: ["bookmarkList"],
    queryFn: getBookmarkList,
  });
};

const usePostBookmark = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (movieId) => postBookmark(movieId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarkList"] });
    },
  });
};

const useDeleteBookmark = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (movieId) => deleteBookmark(movieId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarkList"] });
    },
  });
};

export { useBookmarkList, usePostBookmark, useDeleteBookmark };
