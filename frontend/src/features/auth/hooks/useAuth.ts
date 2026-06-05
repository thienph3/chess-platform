import { useCallback, useEffect, useState } from "react";

import { authApi } from "../api";
import { ILoginRequest, IRegisterRequest, IUser } from "../types";

const TOKEN_KEY = "vcc_access_token";
const REFRESH_KEY = "vcc_refresh_token";

export function useAuth() {
  const [user, setUser] = useState<IUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const saveTokens = (accessToken: string, refreshToken: string) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_KEY, refreshToken);
  };

  const clearTokens = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
  };

  const fetchUser = useCallback(async () => {
    try {
      const response = await authApi.getMe();
      setUser(response.data.data);
    } catch {
      clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      fetchUser();
    } else {
      setIsLoading(false);
    }
  }, [fetchUser]);

  const login = async (data: ILoginRequest) => {
    const response = await authApi.login(data);
    const tokens = response.data.data!;
    saveTokens(tokens.access_token, tokens.refresh_token);
    await fetchUser();
  };

  const register = async (data: IRegisterRequest) => {
    await authApi.register(data);
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return { user, isLoading, isAuthenticated: !!user, login, register, logout };
}
