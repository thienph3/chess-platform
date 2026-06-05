import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { IBalance } from "../types";

export function useBalance() {
  return useQuery({
    queryKey: ["finance", "balance"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IBalance>>("/finance/balance");
      return data;
    },
  });
}
