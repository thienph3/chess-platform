import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { IGameRoom, IGameRoomCreate } from "../types";

export function useLiveGames() {
  return useQuery({
    queryKey: ["games", "live"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IGameRoom[]>>("/games/live");
      return data.data || [];
    },
    refetchInterval: 5000,
  });
}

export function useGameRoom(id: string) {
  return useQuery({
    queryKey: ["games", id],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IGameRoom>>(`/games/${id}`);
      return data.data!;
    },
    enabled: !!id,
  });
}

export function useCreateGameRoom() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: IGameRoomCreate) => {
      const res = await apiClient.post<IResponseEnvelope<IGameRoom>>("/games", data);
      return res.data.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["games"] });
    },
  });
}

export function useJoinGameRoom() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (roomId: string) => {
      const res = await apiClient.post<IResponseEnvelope<IGameRoom>>(`/games/${roomId}/join`);
      return res.data.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["games"] });
    },
  });
}
