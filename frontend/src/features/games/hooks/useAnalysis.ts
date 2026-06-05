import { useMutation } from "@tanstack/react-query";
import axios from "axios";

const ANALYSIS_API = "http://localhost:8001/api/v1/analyze/position";

export interface IAnalysisResult {
  best_move: string;
  evaluation: number;
  variations: string[];
}

interface AnalysisRequest {
  fen: string;
  game_type: string;
}

export function usePositionAnalysis(fen: string, gameType: string) {
  const mutation = useMutation({
    mutationFn: async () => {
      const payload: AnalysisRequest = { fen, game_type: gameType };
      const { data } = await axios.post<{ data: IAnalysisResult }>(ANALYSIS_API, payload);
      return data.data;
    },
  });

  return {
    data: mutation.data ?? null,
    isLoading: mutation.isPending,
    analyze: () => mutation.mutate(),
  };
}
