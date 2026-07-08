import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

// Create centralized API client
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  timeout: 10000,
  withCredentials: true, // For HttpOnly cookies
});

// Request interceptor for inserting tokens and adding exponential backoff defaults
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // If we had a token stored in localStorage (optional, if not using HttpOnly cookies)
  // const token = localStorage.getItem("hrip_access_token");
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`;
  // }
  return config;
});

// Response interceptor for handling 401s and global errors
api.interceptors.response.use(
  (response) => response.data,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    // Handle Token Expiry / 401 Unauthorized
    if (error.response?.status === 401 && originalRequest && !(originalRequest as any)._retry) {
      (originalRequest as any)._retry = true;
      
      try {
        // Attempt to refresh the token
        await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/refresh`,
          {},
          { withCredentials: true }
        );
        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        if (typeof window !== "undefined") {
          window.location.href = "/";
        }
        return Promise.reject(refreshError);
      }
    }
    
    // Format error uniformly
    const customError = new Error(
      (error.response?.data as any)?.message || error.message || "An unexpected error occurred"
    );
    (customError as any).status = error.response?.status;
    return Promise.reject(customError);
  }
);
