import { useMutation, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { IMember, IMemberCreate, IMemberUpdate } from "../types";

export function useCreateMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: IMemberCreate) => {
      const res = await apiClient.post<IResponseEnvelope<IMember>>("/members", data);
      return res.data.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
    },
  });
}

export function useUpdateMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: IMemberUpdate }) => {
      const res = await apiClient.patch<IResponseEnvelope<IMember>>(`/members/${id}`, data);
      return res.data.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
    },
  });
}

export function useDeleteMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/members/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
    },
  });
}
