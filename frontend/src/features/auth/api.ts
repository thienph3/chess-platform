import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { ILoginRequest, IRegisterRequest, ITokenResponse, IUser } from "./types";

export const authApi = {
  login: (data: ILoginRequest) =>
    apiClient.post<IResponseEnvelope<ITokenResponse>>("/auth/login", data),

  register: (data: IRegisterRequest) =>
    apiClient.post<IResponseEnvelope<IUser>>("/auth/register", data),

  refresh: (refreshToken: string) =>
    apiClient.post<IResponseEnvelope<ITokenResponse>>("/auth/refresh", {
      refresh_token: refreshToken,
    }),

  getMe: () => apiClient.get<IResponseEnvelope<IUser>>("/auth/me"),

  forgotPassword: (email: string) =>
    apiClient.post<IResponseEnvelope<null>>("/auth/forgot-password", { email }),

  resetPassword: (token: string, new_password: string) =>
    apiClient.post<IResponseEnvelope<null>>("/auth/reset-password", { token, new_password }),
};
