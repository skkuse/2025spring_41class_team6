import { axiosInterceptor, vanillaAxios } from "@/apis/utils/axiosInterceptor";

const registerUser = async ({ email, password, nickname, login = false }) => {
  const response = await axiosInterceptor.post("/auth/register", {
    email,
    password,
    nickname,
    login,
  });
  return response.data;
};

const loginUser = async ({ email, password }) => {
  const response = await axiosInterceptor.post("/auth/login", {
    email,
    password,
  });
  return response.data;
};

const logoutUser = async () => {
  const response = await vanillaAxios.post("/auth/logout");
  return response.data;
};

export { registerUser, loginUser, logoutUser };
