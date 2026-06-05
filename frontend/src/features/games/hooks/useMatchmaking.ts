import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

export interface IMatchmakingStatus {
  in_queue: boolean;
  matched: boolean;
  opponent_id: string | null;
  game_type: string | null;
  time_format: string | null;
}

interface JoinRequest {
  game_type: string;
  time_format: string;
  rating: number;
}

export function useMatchmakingStatus(enabled: boolean) {
  return useQuery({
    queryKey: ["matchmaking", "status"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IMatchmakingStatus>>("/games/matchmaking/status");
      return data.data!;
    },
    enabled,
    refetchInterval: 3000,
  });
}

export function useJoinMatchmaking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (req: JoinRequest) => {
      const { data } = await apiClient.post<IResponseEnvelope<IMatchmakingStatus>>("/games/matchmaking/join", req);
      return data.data!;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["matchmaking"] }),
  });
}

export function useLeaveMatchmaking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (req: JoinRequest) => {
      await apiClient.post("/games/matchmaking/leave", req);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["matchmaking"] }),
  });
}
