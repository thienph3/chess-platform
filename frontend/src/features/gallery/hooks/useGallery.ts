import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IPaginatedResponse, IResponseEnvelope } from "@/types/api";

import { IGalleryImage } from "../types";

export function useGallery(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["gallery", page, pageSize],
    queryFn: async () => {
      const { data } = await apiClient.get<IPaginatedResponse<IGalleryImage>>("/gallery", {
        params: { page, page_size: pageSize },
      });
      return data;
    },
  });
}

export function useUploadImage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (formData: FormData) => {
      const { data } = await apiClient.post<IResponseEnvelope<IGalleryImage>>("/gallery", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["gallery"] }),
  });
}

export function useDeleteImage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/gallery/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["gallery"] }),
  });
}
