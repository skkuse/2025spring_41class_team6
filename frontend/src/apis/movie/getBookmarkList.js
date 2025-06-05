import axiosInstance from "@/apis/utils/axiosInterceptor";

const getBookmarkList = async () => {
  const response = await axiosInstance.get("/api/movies/bookmarked");
  return response.data;
};

export default getBookmarkList;
