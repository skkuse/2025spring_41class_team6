import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const getBookmarkList = async () => {
  const response = await axiosInterceptor.get("/movies/bookmarked");
  return response.data;
};

export default getBookmarkList;
