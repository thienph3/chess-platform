import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { DataGrid, GridColDef, GridPaginationModel } from "@mui/x-data-grid";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import AppSnackbar from "@/components/AppSnackbar";
import { dataGridLocaleText } from "@/utils/dataGridLocale";

import TournamentFormDialog from "../components/TournamentFormDialog";
import { useCreateTournament, useUpdateTournament } from "../hooks/useTournamentMutations";
import { useTournaments } from "../hooks/useTournaments";
import { GameType, ITournament, ITournamentCreate, TournamentStatus } from "../types";

const STATUS_LABELS: Record<TournamentStatus, string> = {
  draft: "Nháp",
  registration: "Đăng ký",
  in_progress: "Đang diễn ra",
  completed: "Đã kết thúc",
  cancelled: "Đã hủy",
};

import { GAME_LABELS as GAME_TYPE_LABELS } from "@/utils/gameConstants";

const columns: GridColDef[] = [
  { field: "name", headerName: "Tên giải đấu", flex: 1 },
  { field: "game_type", headerName: "Bộ môn", width: 120, valueGetter: (value: GameType) => GAME_TYPE_LABELS[value] || value },
  { field: "time_format", headerName: "Thể thức", width: 120 },
  { field: "format", headerName: "Hình thức", width: 130 },
  { field: "max_participants", headerName: "Số người", width: 100 },
  { field: "status", headerName: "Trạng thái", width: 140, valueGetter: (value: TournamentStatus) => STATUS_LABELS[value] || value },
  { field: "start_date", headerName: "Ngày bắt đầu", width: 130 },
];

function TournamentsPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [status, setStatus] = useState<TournamentStatus | "">("");
  const [gameType, setGameType] = useState<GameType | "">("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editTournament, setEditTournament] = useState<ITournament | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({
    open: false, message: "", severity: "success",
  });

  const { data, isLoading } = useTournaments({ page: page + 1, pageSize, status, gameType });
  const createMutation = useCreateTournament();
  const updateMutation = useUpdateTournament();

  const handleCreate = () => { setEditTournament(null); setDialogOpen(true); };

  const handleSubmit = async (formData: ITournamentCreate) => {
    try {
      if (editTournament) {
        await updateMutation.mutateAsync({ id: editTournament.id, data: formData });
        setSnackbar({ open: true, message: "Cập nhật giải đấu thành công", severity: "success" });
      } else {
        await createMutation.mutateAsync(formData);
        setSnackbar({ open: true, message: "Tạo giải đấu thành công", severity: "success" });
      }
      setDialogOpen(false);
    } catch {
      setSnackbar({ open: true, message: "Có lỗi xảy ra", severity: "error" });
    }
  };

  if (isLoading) {
    return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Giải đấu</Typography>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<CalendarMonthIcon />} onClick={() => navigate("/tournaments/calendar")}>
            Lịch
          </Button>
          <Button variant="contained" startIcon={<EmojiEventsIcon />} onClick={handleCreate}>
            Tạo giải đấu
          </Button>
        </Stack>
      </Stack>
      <Stack direction="row" spacing={2} mb={2}>
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Trạng thái</InputLabel>
          <Select value={status} label="Trạng thái" onChange={(e: SelectChangeEvent) => setStatus(e.target.value as TournamentStatus | "")}>
            <MenuItem value="">Tất cả</MenuItem>
            {Object.entries(STATUS_LABELS).map(([key, label]) => (
              <MenuItem key={key} value={key}>{label}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Bộ môn</InputLabel>
          <Select value={gameType} label="Bộ môn" onChange={(e: SelectChangeEvent) => setGameType(e.target.value as GameType | "")}>
            <MenuItem value="">Tất cả</MenuItem>
            {Object.entries(GAME_TYPE_LABELS).map(([key, label]) => (
              <MenuItem key={key} value={key}>{label}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Stack>
      <DataGrid
        rows={data?.data || []}
        columns={columns}
        rowCount={data?.total || 0}
        paginationMode="server"
        paginationModel={{ page, pageSize }}
        onPaginationModelChange={(model: GridPaginationModel) => { setPage(model.page); setPageSize(model.pageSize); }}
        onRowClick={(params) => navigate(`/tournaments/${params.row.id}`)}
        pageSizeOptions={[10, 20, 50]}
        disableRowSelectionOnClick
        autoHeight
        localeText={dataGridLocaleText}
        sx={{ cursor: "pointer" }}
      />
      <TournamentFormDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSubmit={handleSubmit}
        tournament={editTournament}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />
      <AppSnackbar
        open={snackbar.open}
        message={snackbar.message}
        severity={snackbar.severity}
        onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
      />
    </Box>
  );
}

export default TournamentsPage;
