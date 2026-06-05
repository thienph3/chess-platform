import { useQueries } from "@tanstack/react-query";

import apiClient from "@/api/client";

async function fetchMemberName(id: string): Promise<{ id: string; name: string }> {
  const { data } = await apiClient.get(`/members/${id}`);
  return { id, name: data.data?.full_name || id.slice(0, 8) };
}

/**
 * Hook để resolve danh sách member IDs thành tên hiển thị.
 * Trả về Record<string, string> mapping id → full_name.
 */
export function useMemberNames(ids: string[]): Record<string, string> {
  const uniqueIds = [...new Set(ids.filter(Boolean))];

  const results = useQueries({
    queries: uniqueIds.map((id) => ({
      queryKey: ["member-name", id],
      queryFn: () => fetchMemberName(id),
      staleTime: 5 * 60 * 1000,
      enabled: !!id,
    })),
  });

  const nameMap: Record<string, string> = {};
  results.forEach((result) => {
    if (result.data) {
      nameMap[result.data.id] = result.data.name;
    }
  });

  return nameMap;
}
