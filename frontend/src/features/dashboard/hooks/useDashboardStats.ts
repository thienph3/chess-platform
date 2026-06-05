import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IPaginatedResponse, IResponseEnvelope } from "@/types/api";

interface DashboardStats {
  totalMembers: number;
  activeTournaments: number;
  balance: number;
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: async () => {
      const [membersRes, tournamentsRes, balanceRes] = await Promise.all([
        apiClient.get<IPaginatedResponse<unknown>>("/members", { params: { page: 1, page_size: 1 } }),
        apiClient.get<IPaginatedResponse<unknown>>("/tournaments", { params: { page: 1, page_size: 1, status_filter: "in_progress" } }),
        apiClient.get<IResponseEnvelope<{ balance: number }>>("/finance/balance"),
      ]);

      const stats: DashboardStats = {
        totalMembers: membersRes.data.total,
        activeTournaments: tournamentsRes.data.total,
        balance: balanceRes.data.data?.balance || 0,
      };
      return stats;
    },
  });
}
