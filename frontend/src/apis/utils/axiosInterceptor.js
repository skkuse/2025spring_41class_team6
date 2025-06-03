import axios from "axios";

const axiosInterceptor = axios.create({
  baseURL: "/api",
  withCredentials: true,
});

const vanillaAxios = axios.create({
  baseURL: "/api",
  withCredentials: true,
});

axiosInterceptor.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosInterceptor.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response.status === 422) {
      vanillaAxios.post("auth/logout");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

export { axiosInterceptor, vanillaAxios };
