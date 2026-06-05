import { useMutation, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { ITransaction, ITransactionCreate, ITransactionUpdate } from "../types";

export function useCreateTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: ITransactionCreate) => {
      const res = await apiClient.post<IResponseEnvelope<ITransaction>>("/transactions", data);
      return res.data.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["finance"] });
    },
  });
}

export function useUpdateTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: ITransactionUpdate }) => {
      const res = await apiClient.patch<IResponseEnvelope<ITransaction>>(`/transactions/${id}`, data);
      return res.data.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["finance"] });
    },
  });
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/transactions/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["finance"] });
    },
  });
}
