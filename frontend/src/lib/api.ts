import axios from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

// リクエストインターセプター: アクセストークンを付与
apiClient.interceptors.request.use((config) => {
  const token = Cookies.get("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// レスポンスインターセプター: 401時にトークンリフレッシュ
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh_token = Cookies.get("refresh_token");
        if (!refresh_token) throw new Error("no refresh token");

        const res = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
          refresh_token,
        });
        const { access_token } = res.data;
        Cookies.set("access_token", access_token, { secure: true, sameSite: "strict" });
        original.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(original);
      } catch {
        Cookies.remove("access_token");
        Cookies.remove("refresh_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export function setAuthCookies(access_token: string, refresh_token: string) {
  Cookies.set("access_token", access_token, { secure: true, sameSite: "strict" });
  Cookies.set("refresh_token", refresh_token, { secure: true, sameSite: "strict" });
}

export function clearAuthCookies() {
  Cookies.remove("access_token");
  Cookies.remove("refresh_token");
}
