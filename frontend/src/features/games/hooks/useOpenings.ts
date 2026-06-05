import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

export interface INextMoveStats {
  move: string;
  count: number;
  win_rate_white: number;
  draw_rate: number;
  win_rate_black: number;
}

export interface IOpeningStats {
  total_games: number;
  white_wins: number;
  black_wins: number;
  draws: number;
  next_moves: INextMoveStats[];
}

export function useOpeningStats(moves: string[], gameType: string) {
  const firstMoves = moves.join(",");
  return useQuery({
    queryKey: ["openings", "stats", firstMoves, gameType],
    queryFn: async () => {
      const params: Record<string, string> = { game_type: gameType };
      if (firstMoves) params.first_moves = firstMoves;
      const { data } = await apiClient.get<IResponseEnvelope<IOpeningStats>>("/games/openings/stats", { params });
      return data.data!;
    },
  });
}
