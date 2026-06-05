import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IPaginatedResponse } from "@/types/api";

import { ITransaction, TransactionType } from "../types";

interface UseTransactionsParams {
  page?: number;
  pageSize?: number;
  type?: TransactionType | "";
}

export function useTransactions({ page = 1, pageSize = 20, type }: UseTransactionsParams = {}) {
  return useQuery({
    queryKey: ["transactions", page, pageSize, type],
    queryFn: async () => {
      const params: Record<string, unknown> = { page, page_size: pageSize };
      if (type) params.type = type;

      const { data } = await apiClient.get<IPaginatedResponse<ITransaction>>("/transactions", { params });
      return data;
    },
  });
}
