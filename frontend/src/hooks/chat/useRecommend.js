import { useQuery } from "@tanstack/react-query";
import getRecommend from "@/apis/chat/getRecommend";

const useRecommend = (roomId) => {
  return useQuery({
    queryKey: ["recommend", roomId],
    queryFn: () => getRecommend(roomId),
    enabled: !!roomId,
  });
};

export default useRecommend;
