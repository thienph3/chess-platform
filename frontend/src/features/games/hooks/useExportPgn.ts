import { useCallback } from "react";

import apiClient from "@/api/client";

export function useExportPgn() {
  const exportPgn = useCallback(async (roomId: string) => {
    const response = await apiClient.get(`/games/${roomId}/export/pgn`, {
      responseType: "blob",
    });

    const blob = new Blob([response.data], { type: "application/x-chess-pgn" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `game_${roomId}.pgn`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }, []);

  return { exportPgn };
}
