import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach Bearer token from localStorage on every request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("vcc_access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't transform auth errors - let useAuth handle 401s
    if (error.response?.status === 401) {
      return Promise.reject(error);
    }
    const message = error.response?.data?.message || "Đã xảy ra lỗi";
    return Promise.reject(new Error(message));
  }
);

export default apiClient;
