import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

export interface IAttendance {
  id: string;
  member_id: string;
  date: string;
  event_type: string;
  notes: string | null;
  created_at: string;
}

export interface IAttendanceSummary {
  total_sessions: number;
  current_streak: number;
  last_attendance: string | null;
}

export function useAttendanceHistory() {
  return useQuery({
    queryKey: ["attendance", "history"],
    queryFn: async () => {
      // Lấy member_id từ localStorage (set khi login)
      const memberId = localStorage.getItem("vcc_member_id");
      if (!memberId) return [];
      const { data } = await apiClient.get<IResponseEnvelope<IAttendance[]>>(`/attendance/member/${memberId}`);
      return data.data || [];
    },
  });
}

export function useAttendanceSummary() {
  return useQuery({
    queryKey: ["attendance", "summary"],
    queryFn: async () => {
      const memberId = localStorage.getItem("vcc_member_id");
      if (!memberId) return null;
      const { data } = await apiClient.get<IResponseEnvelope<IAttendanceSummary>>(`/attendance/summary/${memberId}`);
      return data.data;
    },
  });
}

export function useCheckIn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (req: { event_type: string; notes?: string }) => {
      const { data } = await apiClient.post<IResponseEnvelope<IAttendance>>("/attendance/check-in", req);
      return data.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["attendance"] });
    },
  });
}
