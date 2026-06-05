import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { IGameRoom } from "../../games/types";

/** Tạo phòng cho tất cả ván đấu trong 1 vòng (admin only) */
export function useCreateRoundRooms(tournamentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (roundId: string) => {
      const { data } = await apiClient.post<IResponseEnvelope<unknown>>(
        `/tournaments/${tournamentId}/rounds/${roundId}/create-rooms`
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tournaments", tournamentId, "rounds"] });
    },
  });
}

/** Tạo phòng từ match_id và navigate đến phòng chơi */
export function useStartMatchGame() {
  const navigate = useNavigate();
  return useMutation({
    mutationFn: async (matchId: string) => {
      const { data } = await apiClient.post<IResponseEnvelope<IGameRoom>>(
        `/games/from-match/${matchId}`
      );
      return data.data!;
    },
    onSuccess: (room) => {
      navigate(`/play/${room.id}`);
    },
  });
}


/** Nhập kết quả OTB match (admin) */
export function useSubmitMatchResult(tournamentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ matchId, result, pgn }: { matchId: string; result: string; pgn?: string }) => {
      await apiClient.patch(`/matches/${matchId}/result`, { result, pgn });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tournaments", tournamentId, "rounds"] });
    },
  });
}
