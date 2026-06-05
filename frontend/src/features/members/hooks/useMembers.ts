import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IPaginatedResponse } from "@/types/api";

import { IMember } from "../types";

interface UseMembersParams {
  page?: number;
  pageSize?: number;
  search?: string;
}

export function useMembers({ page = 1, pageSize = 20, search }: UseMembersParams = {}) {
  return useQuery({
    queryKey: ["members", page, pageSize, search],
    queryFn: async () => {
      const params: Record<string, unknown> = { page, page_size: pageSize };
      if (search) params.search = search;

      const { data } = await apiClient.get<IPaginatedResponse<IMember>>("/members", { params });
      return data;
    },
  });
}

export function useMember(id: string) {
  return useQuery({
    queryKey: ["members", id],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: IMember }>(`/members/${id}`);
      return data.data;
    },
    enabled: !!id,
  });
}
