import { axiosInterceptor } from "@/apis/utils/axiosInterceptor";

const createChatroom = async (characterId = null) => {
  const response = await axiosInterceptor.post("/chatrooms", {
    data: {
      character_id: characterId,
    },
  });
  return response.data;
};

export default createChatroom;
