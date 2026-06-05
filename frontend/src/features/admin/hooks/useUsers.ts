import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

export interface IUserRow {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export function useUsers() {
  return useQuery({
    queryKey: ["admin", "users"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IUserRow[]>>("/auth/users");
      return data.data || [];
    },
  });
}
