import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

export interface INewsPost {
  id: string;
  title: string;
  content: string;
  author_id: string;
  is_pinned: boolean;
  created_at: string;
}

export function useNewsList() {
  return useQuery({
    queryKey: ["news"],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<INewsPost[]>>("/news");
      return data.data || [];
    },
  });
}

export function useCreateNews() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (req: { title: string; content: string; is_pinned: boolean }) => {
      const { data } = await apiClient.post<IResponseEnvelope<INewsPost>>("/news", req);
      return data.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["news"] });
    },
  });
}

export function useDeleteNews() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (postId: string) => {
      await apiClient.delete(`/news/${postId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["news"] });
    },
  });
}
