import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import getArchive from "@/apis/movie/getArchive";
import postArchive from "@/apis/movie/postArchive";
import deleteArchive from "@/apis/movie/deleteArchive";

const useGetArchiveList = () => {
  return useQuery({
    queryKey: ["archiveList"],
    queryFn: getArchive,
  });
};

const usePostArchive = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (movieId, rating) => postArchive(movieId, rating),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["archiveList"] });
    },
  });
};

const usePutArchive = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (movieId, rating) => putArchive(movieId, rating),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["archiveList"] });
    },
  });
};

const useDeleteArchive = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (movieId) => deleteArchive(movieId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["archiveList"] });
    },
  });
};

export { useGetArchiveList, usePostArchive, usePutArchive, useDeleteArchive };
