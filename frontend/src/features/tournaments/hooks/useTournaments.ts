import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IPaginatedResponse } from "@/types/api";

import { GameType, ITournament, TournamentStatus } from "../types";

interface UseTournamentsParams {
  page?: number;
  pageSize?: number;
  status?: TournamentStatus | "";
  gameType?: GameType | "";
}

export function useTournaments({ page = 1, pageSize = 20, status, gameType }: UseTournamentsParams = {}) {
  return useQuery({
    queryKey: ["tournaments", page, pageSize, status, gameType],
    queryFn: async () => {
      const params: Record<string, unknown> = { page, page_size: pageSize };
      if (status) params.status_filter = status;
      if (gameType) params.game_type = gameType;

      const { data } = await apiClient.get<IPaginatedResponse<ITournament>>("/tournaments", { params });
      return data;
    },
  });
}
