import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";
import { IGameRoom } from "@/features/games/types";

export interface IActivityItem {
  id: string;
  gameType: string;
  white: string;
  black: string;
  result: string;
  date: string;
}

function formatResult(result: string | null): string {
  if (result === "white_win") return "Trắng thắng";
  if (result === "black_win") return "Đen thắng";
  if (result === "draw") return "Hòa";
  return "Chưa kết thúc";
}

export function useActivityFeed() {
  return useQuery({
    queryKey: ["activity-feed"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IGameRoom[]>>("/games/history/all", {
        params: { limit: 5 },
      });
      const games = data.data || [];

      return games.map((game): IActivityItem => ({
        id: game.id,
        gameType: game.game_type,
        white: game.white_player_id.slice(0, 8),
        black: game.black_player_id?.slice(0, 8) || "—",
        result: formatResult(game.result),
        date: new Date(game.created_at).toLocaleDateString("vi-VN"),
      }));
    },
  });
}
