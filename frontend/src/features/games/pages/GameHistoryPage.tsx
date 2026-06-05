import AnalyticsIcon from "@mui/icons-material/Analytics";
import DownloadIcon from "@mui/icons-material/Download";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { useNavigate } from "react-router-dom";

import EmptyState from "@/components/EmptyState";
import PlayerName from "@/components/PlayerName";
import { dataGridLocaleText } from "@/utils/dataGridLocale";

import { useExportPgn } from "../hooks/useExportPgn";
import { useGameHistory, useReviewGame } from "../hooks/useGameHistory";
import { IGameRoom } from "../types";

const GAME_LABELS: Record<string, string> = { chess: "Cờ vua", xiangqi: "Cờ tướng", go: "Cờ vây" };
const RESULT_LABELS: Record<string, string> = { white_win: "Trắng thắng", black_win: "Đen thắng", draw: "Hòa" };
const RESULT_COLORS: Record<string, "success" | "error" | "default" | "warning"> = {
  white_win: "success", black_win: "error", draw: "default", pending: "warning",
};

function AccuracyChip({ value }: { value: number | null }) {
  if (value === null) return <Chip label="—" size="small" variant="outlined" />;
  const color = value >= 90 ? "success" : value >= 70 ? "primary" : value >= 50 ? "warning" : "error";
  return <Chip label={`${value.toFixed(1)}%`} size="small" color={color} />;
}

function GameHistoryPage() {
  const navigate = useNavigate();
  const { data: games, isLoading } = useGameHistory();
  const reviewMutation = useReviewGame();
  const { exportPgn } = useExportPgn();

  const columns: GridColDef[] = [
    { field: "game_type", headerName: "Bộ môn", width: 100, valueGetter: (value: string) => GAME_LABELS[value] || value },
    {
      field: "white_player_id", headerName: "Trắng", flex: 1,
      renderCell: (params) => <PlayerName memberId={params.value} />,
    },
    { field: "white_accuracy", headerName: "Acc Trắng", width: 110, renderCell: (params) => <AccuracyChip value={params.value} /> },
    {
      field: "black_player_id", headerName: "Đen", flex: 1,
      renderCell: (params) => <PlayerName memberId={params.value} />,
    },
    { field: "black_accuracy", headerName: "Acc Đen", width: 110, renderCell: (params) => <AccuracyChip value={params.value} /> },
    {
      field: "result", headerName: "Kết quả", width: 130,
      renderCell: (params) => (
        <Chip
          label={RESULT_LABELS[params.value] || params.value || "—"}
          size="small"
          color={RESULT_COLORS[params.value] || "default"}
        />
      ),
    },
    { field: "created_at", headerName: "Ngày", width: 120, valueGetter: (value: string) => new Date(value).toLocaleDateString("vi-VN") },
    {
      field: "actions", headerName: "", width: 200, sortable: false,
      renderCell: (params) => {
        const room = params.row as IGameRoom;
        return (
          <Stack direction="row" spacing={0.5} alignItems="center">
            <Button
              size="small"
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={(e) => { e.stopPropagation(); exportPgn(room.id); }}
            >
              PGN
            </Button>
            {room.is_reviewed ? (
              <Chip label="Đã chấm" size="small" variant="outlined" />
            ) : (
              <Button
                size="small"
                variant="outlined"
                onClick={(e) => { e.stopPropagation(); reviewMutation.mutate(room.id); }}
                disabled={reviewMutation.isPending}
              >
                Chấm điểm
              </Button>
            )}
          </Stack>
        );
      },
    },
  ];

  if (isLoading) return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Lịch sử ván đấu</Typography>
      </Stack>
      {(!games || games.length === 0) ? (
        <EmptyState icon={<AnalyticsIcon sx={{ fontSize: 60 }} />} message="Chưa có ván đấu nào kết thúc" />
      ) : (
        <DataGrid
          rows={games}
          columns={columns}
          pageSizeOptions={[20, 50]}
          disableRowSelectionOnClick
          autoHeight
          onRowClick={(params) => navigate(`/play/${params.row.id}/replay`)}
          localeText={dataGridLocaleText}
          sx={{ cursor: "pointer" }}
        />
      )}
    </Box>
  );
}

export default GameHistoryPage;
