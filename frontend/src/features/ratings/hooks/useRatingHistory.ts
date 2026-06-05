import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { GameType, TimeFormat } from "../types";

export interface IRatingChange {
  id: string;
  rating_id: string;
  match_id: string;
  old_rating: number;
  new_rating: number;
  change: number;
  created_at: string;
}

export interface IRating {
  id: string;
  member_id: string;
  game_type: GameType;
  time_format: TimeFormat;
  rating: number;
  games_played: number;
  wins: number;
  draws: number;
  losses: number;
}

export function useMemberRatings(memberId: string) {
  return useQuery({
    queryKey: ["ratings", memberId],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IRating[]>>(`/ratings/${memberId}`);
      return data.data || [];
    },
    enabled: !!memberId,
  });
}

export function useRatingHistory(memberId: string, gameType: GameType, timeFormat: TimeFormat) {
  return useQuery({
    queryKey: ["ratings", memberId, "history", gameType, timeFormat],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IRatingChange[]>>(
        `/ratings/${memberId}/history`,
        { params: { game_type: gameType, time_format: timeFormat } }
      );
      return data.data || [];
    },
    enabled: !!memberId,
  });
}
