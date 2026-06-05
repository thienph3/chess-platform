import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IPaginatedResponse } from "@/types/api";

import { ITournament } from "../types";

export function useTournamentCalendar(year: number, month: number) {
  return useQuery({
    queryKey: ["tournaments", "calendar", year, month],
    queryFn: async () => {
      // Lấy tất cả giải đấu (không phân trang lớn) để hiển thị trên lịch
      const { data } = await apiClient.get<IPaginatedResponse<ITournament>>("/tournaments", {
        params: { page: 1, page_size: 100 },
      });
      return data.data || [];
    },
  });
}
