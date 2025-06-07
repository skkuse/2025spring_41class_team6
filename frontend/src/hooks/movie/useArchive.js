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
    mutationFn: ({ movieId, rating }) => postArchive(movieId, rating),
    onSuccess: (data, payload) => {
      queryClient.invalidateQueries({ queryKey: ["archiveList"] });
      queryClient.invalidateQueries({ queryKey: ["movie", payload.movie_id] });
      console.log("Test");
      console.log(data, payload);
    },
  });
};

const usePutArchive = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ movieId, rating }) => putArchive(movieId, rating),
    onSuccess: (data, payload) => {
      queryClient.invalidateQueries({ queryKey: ["archiveList"] });
      queryClient.invalidateQueries({ queryKey: ["movie", payload] });
      console.log("Test");
      console.log(data, payload);
    },
  });
};

const useDeleteArchive = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ movieId }) => deleteArchive(movieId),
    onSuccess: (data, payload) => {
      queryClient.invalidateQueries({ queryKey: ["archiveList"] });
      queryClient.invalidateQueries({ queryKey: ["movie", payload] });
      console.log("Test");
      console.log(data, payload);
    },
  });
};

export { useGetArchiveList, usePostArchive, usePutArchive, useDeleteArchive };
