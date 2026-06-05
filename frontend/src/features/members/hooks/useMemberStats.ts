import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { IGameRoom } from "@/features/games/types";

export interface IMemberGameStats {
  totalGames: number;
  wins: number;
  draws: number;
  losses: number;
  winRate: number;
  recentGames: IGameRoom[];
  recentForm: ("W" | "D" | "L")[];
}

export function useMemberGameStats(memberId: string) {
  return useQuery({
    queryKey: ["members", memberId, "game-stats"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IGameRoom[]>>("/games/history/all", {
        params: { limit: 100 },
      });
      const allGames = data.data || [];

      // Lọc ván đấu của thành viên
      const memberGames = allGames.filter(
        (g) => g.white_player_id === memberId || g.black_player_id === memberId
      );

      let wins = 0;
      let draws = 0;
      let losses = 0;

      memberGames.forEach((game) => {
        if (game.result === "draw") {
          draws++;
        } else if (
          (game.result === "white_win" && game.white_player_id === memberId) ||
          (game.result === "black_win" && game.black_player_id === memberId)
        ) {
          wins++;
        } else {
          losses++;
        }
      });

      const totalGames = memberGames.length;
      const winRate = totalGames > 0 ? (wins / totalGames) * 100 : 0;
      const recentGames = memberGames.slice(0, 10);

      // Kết quả 5 ván gần nhất
      const recentForm: ("W" | "D" | "L")[] = recentGames.slice(0, 5).map((game) => {
        if (game.result === "draw") return "D";
        if (
          (game.result === "white_win" && game.white_player_id === memberId) ||
          (game.result === "black_win" && game.black_player_id === memberId)
        ) {
          return "W";
        }
        return "L";
      });

      return { totalGames, wins, draws, losses, winRate, recentGames, recentForm } as IMemberGameStats;
    },
    enabled: !!memberId,
  });
}
