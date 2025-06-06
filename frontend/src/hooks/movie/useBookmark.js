import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import getBookmarkList from "@/apis/movie/getBookmarkList";
import postBookmark from "@/apis/movie/postBookmark";
import deleteBookmark from "@/apis/movie/deleteBookmark";

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
    onSuccess: (data, movieId) => {
      queryClient.invalidateQueries({ queryKey: ["bookmarkList"] });
      queryClient.invalidateQueries({ queryKey: ["movie", movieId] });
    },
  });
};

const useDeleteBookmark = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (movieId) => deleteBookmark(movieId),
    onSuccess: (data, movieId) => {
      queryClient.invalidateQueries({ queryKey: ["bookmarkList"] });
      queryClient.invalidateQueries({ queryKey: ["movie", movieId] });
    },
  });
};

export { useBookmarkList, usePostBookmark, useDeleteBookmark };
