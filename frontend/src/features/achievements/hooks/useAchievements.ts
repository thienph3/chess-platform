import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

export interface IAchievement {
  id: string;
  code: string;
  name: string;
  description: string;
  icon: string;
  condition_type: string;
  condition_value: number;
}

export interface IMemberAchievement {
  id: string;
  member_id: string;
  achievement_id: string;
  earned_at: string;
}

export function useAchievements() {
  return useQuery({
    queryKey: ["achievements"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IAchievement[]>>("/achievements");
      return data.data || [];
    },
  });
}

export function useMemberAchievements() {
  return useQuery({
    queryKey: ["achievements", "member"],
    queryFn: async () => {
      const memberId = localStorage.getItem("vcc_member_id");
      if (!memberId) return [];
      const { data } = await apiClient.get<IResponseEnvelope<IMemberAchievement[]>>(
        `/achievements/member/${memberId}`
      );
      return data.data || [];
    },
  });
}
