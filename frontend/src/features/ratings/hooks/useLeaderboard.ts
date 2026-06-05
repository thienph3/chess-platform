import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { GameType, ILeaderboardEntry, TimeFormat } from "../types";

interface UseLeaderboardParams {
  gameType: GameType;
  timeFormat: TimeFormat;
  limit?: number;
}

export function useLeaderboard({ gameType, timeFormat, limit = 20 }: UseLeaderboardParams) {
  return useQuery({
    queryKey: ["leaderboard", gameType, timeFormat, limit],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<ILeaderboardEntry[]>>("/leaderboard", {
        params: { game_type: gameType, time_format: timeFormat, limit },
      });
      return data;
    },
  });
}
