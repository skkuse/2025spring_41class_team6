import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import getArchive from "@/apis/movie/getArchive";
import postArchive from "@/apis/movie/postArchive";
import putArchive from "@/apis/movie/putArchive"; // putArchive import 추가
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
    onSuccess: (data, variables) => {
      // variables로 전달된 원본 매개변수 사용
      queryClient.invalidateQueries({ queryKey: ["archiveList"] });
      queryClient.invalidateQueries({ queryKey: ["movie", variables.movieId] });
    },
  });
};

const usePutArchive = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ movieId, rating }) => putArchive(movieId, rating),
    onSuccess: (data, variables) => {
      // variables로 전달된 원본 매개변수 사용
      queryClient.invalidateQueries({ queryKey: ["archiveList"] });
      queryClient.invalidateQueries({ queryKey: ["movie", variables.movieId] });
    },
  });
};

const useDeleteArchive = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ movieId }) => deleteArchive(movieId),
    onSuccess: (data, variables) => {
      // variables로 전달된 원본 매개변수 사용
      queryClient.invalidateQueries({ queryKey: ["archiveList"] });
      queryClient.invalidateQueries({ queryKey: ["movie", variables.movieId] });
    },
  });
};

export { useGetArchiveList, usePostArchive, usePutArchive, useDeleteArchive };
