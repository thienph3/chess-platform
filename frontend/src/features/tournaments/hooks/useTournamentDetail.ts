import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

import { ITournament } from "../types";

export interface IParticipant {
  id: string;
  tournament_id: string;
  member_id: string;
  status: string;
  seed: number | null;
  final_rank: number | null;
  created_at: string;
}

export interface IMatch {
  id: string;
  round_id: string;
  white_player_id: string;
  black_player_id: string;
  result: string;
  played_at: string | null;
  created_at: string;
}

export interface IRound {
  id: string;
  tournament_id: string;
  round_number: number;
  status: string;
  matches: IMatch[];
  created_at: string;
}

export function useTournamentDetail(id: string) {
  return useQuery({
    queryKey: ["tournaments", id],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<ITournament>>(`/tournaments/${id}`);
      return data.data!;
    },
    enabled: !!id,
  });
}

export function useTournamentParticipants(id: string) {
  return useQuery({
    queryKey: ["tournaments", id, "participants"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IParticipant[]>>(`/tournaments/${id}/participants`);
      return data.data || [];
    },
    enabled: !!id,
  });
}

export function useTournamentRounds(id: string) {
  return useQuery({
    queryKey: ["tournaments", id, "rounds"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IRound[]>>(`/tournaments/${id}/rounds`);
      return data.data || [];
    },
    enabled: !!id,
  });
}
