import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

export interface IChallenge {
  id: string;
  challenger_id: string;
  challenged_id: string;
  game_type: string;
  time_control: number;
  status: string;
  created_at: string;
}

interface ChallengeCreateRequest {
  challenged_id: string;
  game_type: string;
  time_control: number;
}

export function usePendingChallenges() {
  return useQuery({
    queryKey: ["challenges", "pending"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IChallenge[]>>("/games/challenges/pending");
      return data.data || [];
    },
    refetchInterval: 5000,
  });
}

export function useCreateChallenge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (req: ChallengeCreateRequest) => {
      const { data } = await apiClient.post<IResponseEnvelope<IChallenge>>("/games/challenges", req);
      return data.data!;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["challenges"] }),
  });
}

export function useAcceptChallenge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<IResponseEnvelope<IChallenge>>(`/games/challenges/${id}/accept`);
      return data.data!;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["challenges"] }),
  });
}

export function useDeclineChallenge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<IResponseEnvelope<IChallenge>>(`/games/challenges/${id}/decline`);
      return data.data!;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["challenges"] }),
  });
}
