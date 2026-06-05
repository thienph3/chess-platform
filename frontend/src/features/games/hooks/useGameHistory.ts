import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { IGameRoom } from "../types";

export function useGameHistory(limit = 50) {
  return useQuery({
    queryKey: ["games", "history", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IGameRoom[]>>("/games/history/all", {
        params: { limit },
      });
      return data.data || [];
    },
  });
}

export function useReviewGame() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (roomId: string) => {
      const { data } = await apiClient.post<IResponseEnvelope<IGameRoom>>(`/games/${roomId}/review`);
      return data.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["games", "history"] });
    },
  });
}
