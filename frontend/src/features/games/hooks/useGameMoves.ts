import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { IMoveHistory } from "../types";

export function useGameMoves(roomId: string) {
  return useQuery({
    queryKey: ["games", roomId, "moves"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IMoveHistory[]>>(
        `/games/${roomId}/moves`
      );
      return data.data || [];
    },
    enabled: !!roomId,
  });
}
