import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const postMessage = async ({ room_id, content }) => {
  const response = await axiosInterceptor.post(
    `/chatrooms/${room_id}/messages`,
    {
      content,
    }
  );
  return response.data;
};
